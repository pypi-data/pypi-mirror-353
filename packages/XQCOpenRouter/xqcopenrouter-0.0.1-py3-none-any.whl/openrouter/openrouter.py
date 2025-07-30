"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/7 10:41
文件描述：高效、易用的 OpenRouter API Python 客户端，支持同步与异步调用。
文件路径：/src/openrouter/openrouter.py
"""
import logging
import httpx
from .utils import read_str_or_file, logger_init
from typing import Optional, List, Dict, Any, Literal


class OpenRouterSync:
    def __init__(
            self,
            api_key: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            base_url: str = "https://openrouter.ai/api/v1",
            logger: Optional[logging.Logger] = None,
            system_prompt: Optional[str] = None,
            assistant_prompt: Optional[str] = None,
            console_log_level: str = "INFO",
            log_file_level: str = "WARNING",
            log_file: Optional[str] = None
    ) -> None:
        """
        OpenRouter 的 Python 客户端
        :param api_key: OpenRouter 的 API Key
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param base_url: OpenRouter 的 API 地址
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径
        """
        self.api_key = api_key
        self.base_url = base_url
        self.primary_model = primary_model
        self.logger = logger or logger_init(
            name="OpenRouter",
            console_log_level=console_log_level,
            log_file_level=log_file_level,
            log_file=log_file
        )
        self.system_prompt = read_str_or_file(system_prompt) if system_prompt else None
        self.assistant_prompt = read_str_or_file(assistant_prompt) if assistant_prompt else None
        self._current_model = primary_model
        self._backup_models = backup_models or []

    def set_backup_models(self, models: List[str]):
        """
        设置备用模型列表
        :param models: 备用模型ID列表
        """
        self._backup_models = models or []

    def chat(
            self,
            content: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_latest_free: bool = False,
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        聊天接口，支持主模型、备用模型、自动免费模型三重兜底。
        若主模型和备用模型均未设置，将自动搜索并调用可用的免费模型。
        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_latest_free: 是否自动使用最新的免费模型（会覆盖主模型）
        :param auto_fallback: 请求失败时是否自动尝试使用其他免费模型，默认True
        :param fallback_max: 自动替换尝试的最大次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串
        """
        chosen_model = primary_model or self.primary_model
        backup_models_list = backup_models if backup_models is not None else self._backup_models
        # 自动兜底：主模型和备用模型都未设置时，自动搜索免费模型
        if not chosen_model and not backup_models_list:
            free_models = self.get_free_models()
            if free_models:
                chosen_model = free_models[0]
                self.logger.info(f"✅ 自动选择免费模型：{chosen_model}")
        if auto_latest_free:
            free_models = self.search_models(sort_by="newest", only_free=True)
            if free_models:
                chosen_model = free_models[0]["id"]
                self._current_model = chosen_model
                self.logger.info(f"✅ 使用最新免费模型：{chosen_model}")
        attempt = 0
        backup_used = False
        free_used = False
        while attempt <= fallback_max:
            url = f"{self.base_url}/chat/completions"
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            if self.assistant_prompt:
                messages.append({"role": "assistant", "content": self.assistant_prompt})
            user_content = read_str_or_file(content)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": chosen_model,
                "messages": messages
            }
            if body_extra:
                payload.update(body_extra)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            if headers_extra:
                headers.update(headers_extra)
            self.logger.debug(f"📤 正在发送请求（尝试 {attempt + 1}）到模型：{chosen_model}")
            try:
                with httpx.Client(timeout=30) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    message = result["choices"][0]["message"]["content"]
                    self.logger.debug(f"📥 接收到回复：{message}")
                    if reset_user_model and primary_model:
                        self._current_model = primary_model
                    return message
            except Exception as e:
                self.logger.error(f"❌ 模型 {chosen_model} 请求失败：{str(e)}")
                # 先尝试备用模型
                if not backup_used and backup_models_list:
                    chosen_model = backup_models_list[attempt % len(backup_models_list)]
                    self._current_model = chosen_model
                    backup_used = True
                    self.logger.warning(f"⚠️ 正在尝试使用备用模型：{chosen_model}")
                # 再尝试自动免费模型
                elif not free_used and auto_fallback:
                    fallback_auto_models = self.search_models(sort_by="newest", only_free=True)
                    if attempt < len(fallback_auto_models):
                        chosen_model = fallback_auto_models[attempt % len(fallback_auto_models)]["id"]
                        self._current_model = chosen_model
                        free_used = True
                        self.logger.warning(f"⚠️ 正在尝试使用自动免费备用模型：{chosen_model}")
                    else:
                        break
                else:
                    break
            attempt += 1
        return "请求失败"

    def search_models(
            self,
            sort_by: Literal[
                "newest",
                "pricing_low",
                "pricing_high",
                "context_high",
                "throughput_high",
                "latency_low"
            ] = "newest",
            only_free: bool = False,
            keyword: Optional[str] = None,
            input_modalities: Optional[List[str]] = None,
            output_modalities: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索并筛选模型列表

        :param sort_by: 排序方式，可选值包括：
            - "newest": 最新模型优先
            - "pricing_low": 价格低优先（prompt + completion）
            - "pricing_high": 价格高优先
            - "context_high": 上下文长度高优先
            - "throughput_high": 最大生成令牌数优先
            - "latency_low": 延迟低优先（用价格近似）
        :param only_free: 是否只筛选免费模型（模型 ID 含 ":free" 或名称含 "(free)"）
        :param keyword: 关键词，匹配模型 ID 或名称（不区分大小写）
        :param input_modalities: 输入模态列表，如 ["text", "image"]，要求模型支持全部模态
        :param output_modalities: 输出模态列表，如 ["text"]，要求模型支持全部模态
        :return: 满足条件的模型字典列表
        """
        self.logger.info(f"🔍 正在搜索模型（排序：{sort_by}，只看免费：{only_free}，关键词：{keyword}）")

        try:
            response = httpx.get(
                f"{self.base_url}/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            models = response.json().get("data", [])

            if only_free:
                models = [
                    m for m in models
                    if ":free" in m.get("id", "").lower() or "(free)" in m.get("name", "").lower()
                ]

            if keyword:
                kw = keyword.lower()
                models = [
                    m for m in models
                    if kw in m.get("id", "").lower() or kw in m.get("name", "").lower()
                ]

            if input_modalities:
                models = [
                    m for m in models
                    if self._modality_match(input_modalities, m.get("architecture", {}).get("input_modalities"))
                ]
            if output_modalities:
                models = [
                    m for m in models
                    if self._modality_match(output_modalities, m.get("architecture", {}).get("output_modalities"))
                ]

            def total_price(m: Dict[str, Any]) -> float:
                try:
                    p = float(m.get("pricing", {}).get("prompt", 0))
                    c = float(m.get("pricing", {}).get("completion", 0))
                    return p + c
                except:
                    return float("inf")

            if sort_by == "newest":
                models.sort(key=lambda x: x.get("created", 0), reverse=True)
            elif sort_by == "pricing_low":
                models.sort(key=total_price)
            elif sort_by == "pricing_high":
                models.sort(key=total_price, reverse=True)
            elif sort_by == "context_high":
                models.sort(key=lambda x: x.get("top_provider", {}).get("context_length", 0), reverse=True)
            elif sort_by == "throughput_high":
                models.sort(key=lambda x: x.get("top_provider", {}).get("max_completion_tokens") or 0, reverse=True)
            elif sort_by == "latency_low":
                models.sort(key=total_price)

            self.logger.info(f"✅ 共找到 {len(models)} 个模型")

            for i, model in enumerate(models[:3]):
                self.logger.debug(
                    f"🧠 模型 {i + 1}：ID={model.get('id')}，名称={model.get('name', '未知')}，"
                    f"输入={model.get('architecture', {}).get('input_modalities')}，"
                    f"输出={model.get('architecture', {}).get('output_modalities')}，"
                    f"价格={total_price(model):.8f}"
                )

            return models

        except Exception as e:
            self.logger.error(f"❌ 搜索失败：{str(e)}")
            return []

    @staticmethod
    def _modality_match(keywords: Optional[List[str]], target: Optional[List[str]]) -> bool:
        """
        判断模态是否匹配（私有方法）

        :param keywords: 用户提供的模态关键词列表
        :param target: 模型支持的模态列表
        :return: 是否匹配
        """
        if not keywords:
            return True
        if not target:
            return False
        return all(m in target for m in keywords)

    def get_free_models(self, limit: Optional[int] = None, only_id: bool = True):
        """
        获取免费模型列表
        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :return: 模型id列表或模型字典列表
        """
        models = self.search_models(only_free=True)
        if limit is not None:
            models = models[:limit]
        if only_id:
            return [m["id"] for m in models]
        return models

    def set_system_prompt(self, prompt: Optional[str]):
        """
        设置系统提示词（支持字符串或文件路径）
        :param prompt: 字符串或文件路径
        """
        self.system_prompt = read_str_or_file(prompt) if prompt else None

    def set_assistant_prompt(self, prompt: Optional[str]):
        """
        设置助手提示词（支持字符串或文件路径）
        :param prompt: 字符串或文件路径
        """
        self.assistant_prompt = read_str_or_file(prompt) if prompt else None

    def set_primary_model(self, model: Optional[str]):
        """
        设置主模型
        :param model: 主模型ID
        """
        self.primary_model = model
        self._current_model = model


class OpenRouterAsync:
    def __init__(
            self,
            api_key: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            base_url: str = "https://openrouter.ai/api/v1",
            logger: Optional[logging.Logger] = None,
            system_prompt: Optional[str] = None,
            assistant_prompt: Optional[str] = None,
            console_log_level: str = "INFO",
            log_file_level: str = "WARNING",
            log_file: Optional[str] = None
    ) -> None:
        """
        OpenRouter 的 Python 异步客户端
        :param api_key: OpenRouter 的 API Key
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param base_url: OpenRouter 的 API 地址
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径
        """
        self.api_key = api_key
        self.base_url = base_url
        self.primary_model = primary_model
        self.logger = logger or logger_init(
            name="OpenRouter",
            console_log_level=console_log_level,
            log_file_level=log_file_level,
            log_file=log_file
        )
        self.system_prompt = read_str_or_file(system_prompt) if system_prompt else None
        self.assistant_prompt = read_str_or_file(assistant_prompt) if assistant_prompt else None
        self._current_model = primary_model
        self._backup_models = backup_models or []

    def set_backup_models(self, models: List[str]):
        """
        设置备用模型列表
        :param models: 备用模型ID列表
        """
        self._backup_models = models or []

    async def chat(
            self,
            content: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_latest_free: bool = False,
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        异步方式聊天接口，支持主模型、备用模型、自动免费模型三重兜底。
        若主模型和备用模型均未设置，将自动搜索并调用可用的免费模型。
        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_latest_free: 是否自动使用最新的免费模型（会覆盖主模型）
        :param auto_fallback: 请求失败时是否自动尝试使用其他免费模型，默认True
        :param fallback_max: 自动替换尝试的最大次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串
        """
        chosen_model = primary_model or self.primary_model
        backup_models_list = backup_models if backup_models is not None else self._backup_models
        # 自动兜底：主模型和备用模型都未设置时，自动搜索免费模型
        if not chosen_model and not backup_models_list:
            free_models = await self.get_free_models()
            if free_models:
                chosen_model = free_models[0]
                self.logger.info(f"✅ 自动选择免费模型：{chosen_model}")
        if auto_latest_free:
            free_models = await self.search_models(sort_by="newest", only_free=True)
            if free_models:
                chosen_model = free_models[0]["id"]
                self._current_model = chosen_model
                self.logger.info(f"✅ 使用最新免费模型：{chosen_model}")
        attempt = 0
        backup_used = False
        free_used = False
        while attempt <= fallback_max:
            url = f"{self.base_url}/chat/completions"
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            if self.assistant_prompt:
                messages.append({"role": "assistant", "content": self.assistant_prompt})
            user_content = read_str_or_file(content)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": chosen_model,
                "messages": messages
            }
            if body_extra:
                payload.update(body_extra)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            if headers_extra:
                headers.update(headers_extra)
            self.logger.debug(f"📤 正在发送请求（尝试 {attempt + 1}）到模型：{chosen_model}")
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    if callable(result):
                        result = await response.json()
                    message = result["choices"][0]["message"]["content"]
                    self.logger.debug(f"📥 接收到回复：{message}")
                    if reset_user_model and primary_model:
                        self._current_model = primary_model
                    return message
            except Exception as e:
                self.logger.error(f"❌ 模型 {chosen_model} 请求失败：{str(e)}")
                # 先尝试备用模型
                if not backup_used and backup_models_list:
                    chosen_model = backup_models_list[attempt % len(backup_models_list)]
                    self._current_model = chosen_model
                    backup_used = True
                    self.logger.warning(f"⚠️ 正在尝试使用备用模型：{chosen_model}")
                # 再尝试自动免费模型
                elif not free_used and auto_fallback:
                    fallback_auto_models = await self.search_models(sort_by="newest", only_free=True)
                    if attempt < len(fallback_auto_models):
                        chosen_model = fallback_auto_models[attempt % len(fallback_auto_models)]["id"]
                        self._current_model = chosen_model
                        free_used = True
                        self.logger.warning(f"⚠️ 正在尝试使用自动免费备用模型：{chosen_model}")
                    else:
                        break
                else:
                    break
            attempt += 1
        return "请求失败"

    async def search_models(
            self,
            sort_by: Literal[
                "newest",
                "pricing_low",
                "pricing_high",
                "context_high",
                "throughput_high",
                "latency_low"
            ] = "newest",
            only_free: bool = False,
            keyword: Optional[str] = None,
            input_modalities: Optional[List[str]] = None,
            output_modalities: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索并筛选模型列表（异步）
        :param sort_by: 排序方式
        :param only_free: 是否只筛选免费模型
        :param keyword: 关键词
        :param input_modalities: 输入模态
        :param output_modalities: 输出模态
        :return: 满足条件的模型字典列表
        """
        self.logger.info(f"🔍 正在搜索模型（排序：{sort_by}，只看免费：{only_free}，关键词：{keyword}）")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                models = response.json().get("data", [])
                if callable(models):
                    models = await response.json()
                    models = models.get("data", [])
                if only_free:
                    models = [
                        m for m in models
                        if ":free" in m.get("id", "").lower() or "(free)" in m.get("name", "").lower()
                    ]
                if keyword:
                    kw = keyword.lower()
                    models = [
                        m for m in models
                        if kw in m.get("id", "").lower() or kw in m.get("name", "").lower()
                    ]
                if input_modalities:
                    models = [
                        m for m in models
                        if OpenRouterSync._modality_match(input_modalities,
                                                          m.get("architecture", {}).get("input_modalities"))
                    ]
                if output_modalities:
                    models = [
                        m for m in models
                        if OpenRouterSync._modality_match(output_modalities,
                                                          m.get("architecture", {}).get("output_modalities"))
                    ]

                def total_price(m: Dict[str, Any]) -> float:
                    try:
                        p = float(m.get("pricing", {}).get("prompt", 0))
                        c = float(m.get("pricing", {}).get("completion", 0))
                        return p + c
                    except:
                        return float("inf")

                if sort_by == "newest":
                    models.sort(key=lambda x: x.get("created", 0), reverse=True)
                elif sort_by == "pricing_low":
                    models.sort(key=total_price)
                elif sort_by == "pricing_high":
                    models.sort(key=total_price, reverse=True)
                elif sort_by == "context_high":
                    models.sort(key=lambda x: x.get("top_provider", {}).get("context_length", 0), reverse=True)
                elif sort_by == "throughput_high":
                    models.sort(key=lambda x: x.get("top_provider", {}).get("max_completion_tokens") or 0, reverse=True)
                elif sort_by == "latency_low":
                    models.sort(key=total_price)
                self.logger.info(f"✅ 共找到 {len(models)} 个模型")
                for i, model in enumerate(models[:3]):
                    self.logger.debug(
                        f"🧠 模型 {i + 1}：ID={model.get('id')}，名称={model.get('name', '未知')}，"
                        f"输入={model.get('architecture', {}).get('input_modalities')}，"
                        f"输出={model.get('architecture', {}).get('output_modalities')}，"
                        f"价格={total_price(model):.8f}"
                    )
                return models
        except Exception as e:
            self.logger.error(f"❌ 搜索失败：{str(e)}")
            return []

    async def get_free_models(self, limit: Optional[int] = None, only_id: bool = True):
        """
        获取免费模型列表（异步）
        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :return: 模型id列表或模型字典列表
        """
        models = await self.search_models(only_free=True)
        if limit is not None:
            models = models[:limit]
        if only_id:
            return [m["id"] for m in models]
        return models

    def set_system_prompt(self, prompt: Optional[str]):
        """
        设置系统提示词（支持字符串或文件路径）
        :param prompt: 字符串或文件路径
        """
        self.system_prompt = read_str_or_file(prompt) if prompt else None

    def set_assistant_prompt(self, prompt: Optional[str]):
        """
        设置助手提示词（支持字符串或文件路径）
        :param prompt: 字符串或文件路径
        """
        self.assistant_prompt = read_str_or_file(prompt) if prompt else None

    def set_primary_model(self, model: Optional[str]):
        """
        设置主模型
        :param model: 主模型ID
        """
        self.primary_model = model
        self._current_model = model


class OpenRouter:
    def __init__(
            self,
            api_key: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            base_url: str = "https://openrouter.ai/api/v1",
            logger: Optional[logging.Logger] = None,
            system_prompt: Optional[str] = None,
            assistant_prompt: Optional[str] = None,
            async_mode: bool = False,
            console_log_level: str = "INFO",
            log_file_level: str = "WARNING",
            log_file: Optional[str] = None
    ):
        """
        OpenRouter 的 Python SDK，用于与 OpenRouter 的 API 进行交互。
        :param api_key: OpenRouter 的 API Key，必填
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型ID列表，主模型失效时自动尝试
        :param base_url: OpenRouter 的 API 地址，默认 https://openrouter.ai/api/v1
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param async_mode: True为异步，False为同步，默认False
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径，当log_file为None时，将不保存日志文件，log_file_level参数将无效
        """
        self.async_mode = async_mode
        if not async_mode:
            self._impl = OpenRouterSync(
                api_key=api_key,
                primary_model=primary_model,
                backup_models=backup_models,
                base_url=base_url,
                logger=logger,
                system_prompt=system_prompt,
                assistant_prompt=assistant_prompt,
                console_log_level=console_log_level,
                log_file_level=log_file_level,
                log_file=log_file
            )
        else:
            self._impl = OpenRouterAsync(
                api_key=api_key,
                primary_model=primary_model,
                backup_models=backup_models,
                base_url=base_url,
                logger=logger,
                system_prompt=system_prompt,
                assistant_prompt=assistant_prompt,
                console_log_level=console_log_level,
                log_file_level=log_file_level,
                log_file=log_file
            )

    def chat(
            self,
            content: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_latest_free: bool = False,
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ):
        """
        聊天接口，支持主模型、备用模型、自动免费模型三重兜底。
        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_latest_free: 是否自动使用最新的免费模型（会覆盖主模型）
        :param auto_fallback: 请求失败时是否自动尝试使用其他免费模型，默认True
        :param fallback_max: 自动替换尝试的最大次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串（同步为str，异步为coroutine）
        """
        return self._impl.chat(
            content=content,
            primary_model=primary_model,
            backup_models=backup_models,
            auto_latest_free=auto_latest_free,
            auto_fallback=auto_fallback,
            fallback_max=fallback_max,
            reset_user_model=reset_user_model,
            headers_extra=headers_extra,
            body_extra=body_extra
        )

    def set_primary_model(self, model: Optional[str]):
        """
        设置主模型（同步/异步统一接口）
        :param model: 主模型ID
        """
        return self._impl.set_primary_model(model)

    def set_backup_models(self, models: List[str]):
        """
        设置备用模型列表（同步/异步统一接口）
        :param models: 备用模型ID列表
        """
        return self._impl.set_backup_models(models)

    def set_system_prompt(self, prompt: Optional[str]):
        """
        设置系统提示词（同步/异步统一接口）
        :param prompt: 字符串或文件路径
        """
        return self._impl.set_system_prompt(prompt)

    def set_assistant_prompt(self, prompt: Optional[str]):
        """
        设置助手提示词（同步/异步统一接口）
        :param prompt: 字符串或文件路径
        """
        return self._impl.set_assistant_prompt(prompt)

    def search_models(
            self,
            sort_by: Literal[
                "newest",
                "pricing_low",
                "pricing_high",
                "context_high",
                "throughput_high",
                "latency_low"
            ] = "newest",
            only_free: bool = False,
            keyword: Optional[str] = None,
            input_modalities: Optional[List[str]] = None,
            output_modalities: Optional[List[str]] = None
    ):
        """
        搜索并筛选模型列表（同步/异步统一接口）
        :param sort_by: 排序方式
        :param only_free: 是否只筛选免费模型
        :param keyword: 关键词
        :param input_modalities: 输入模态
        :param output_modalities: 输出模态
        :return: 满足条件的模型字典列表（同步为List，异步为coroutine）
        """
        return self._impl.search_models(
            sort_by=sort_by,
            only_free=only_free,
            keyword=keyword,
            input_modalities=input_modalities,
            output_modalities=output_modalities
        )

    def get_free_models(self, limit: Optional[int] = None, only_id: bool = True):
        """
        获取免费模型列表（同步/异步统一接口）
        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :return: 模型id列表或模型字典列表（同步为list，异步为coroutine）
        """
        return self._impl.get_free_models(limit=limit, only_id=only_id)

    def __getattr__(self, item):
        return getattr(self._impl, item)

    def __dir__(self):
        # 让编辑器能自动提示OpenRouterSync/Async的所有方法和属性
        return list(set(dir(self._impl)) | set(super().__dir__()))

