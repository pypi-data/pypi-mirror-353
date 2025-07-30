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
from typing import Optional, List, Dict, Any, Literal, Union
import random


class OpenRouterSync:
    def __init__(
            self,
            api_key: Union[str, List[str]],
            random_key: bool = False,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_fallback: bool = True,
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
        :param random_key: 多key时是否随机选择key，True为随机，False为顺序
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认开启
        :param base_url: OpenRouter 的 API 地址
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径
        """
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
        self.auto_fallback = auto_fallback
        self._api_keys = api_key if isinstance(api_key, list) else [api_key]
        self._random_key = random_key
        self._api_key_index = 0

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
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        聊天接口，主模型-备用模型-免费模型顺序兜底

        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认True
        :param fallback_max: 免费模型最大尝试次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串
        """
        chosen_model = primary_model or self.primary_model
        backup_models_list = backup_models or self._backup_models
        auto_fallback = auto_fallback or self.auto_fallback
        model_try_list = []
        if chosen_model:
            model_try_list.append(chosen_model)
        if backup_models_list:
            model_try_list.extend(backup_models_list)

        # 先顺序尝试主模型和所有备用模型
        for idx, try_model in enumerate(model_try_list):
            key_used = self._get_next_api_key()
            if idx == 0 and chosen_model:
                self.logger.info(f"🚀 使用主模型：{try_model}")
            else:
                self.logger.warning(f"🎯 尝试备用模型：{try_model}")
            url = f"{self.base_url}/chat/completions"
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            if self.assistant_prompt:
                messages.append({"role": "assistant", "content": self.assistant_prompt})
            user_content = read_str_or_file(content)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": try_model,
                "messages": messages
            }
            if body_extra:
                payload.update(body_extra)
            headers = {
                "Authorization": f"Bearer {key_used}",
                "Content-Type": "application/json"
            }
            if headers_extra:
                headers.update(headers_extra)
            self.logger.debug(f"🔑 本次请求使用的API Key: sk-******{key_used[-5:]}")
            self.logger.debug(f"📤 正在发送请求（第{idx + 1}次，模型：{try_model}）")
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
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 402:
                    self.logger.error(
                        f"❌ 402 Payment Required：模型ID错误或额度不足。请检查模型ID或账户余额。\n响应内容：{e.response.text}")
                elif status == 429:
                    self.logger.error(
                        f"❌ 429 Too Many Requests：访问速率过快，请等待或更换API Key。\n响应内容：{e.response.text}")
                elif 400 <= status < 500:
                    self.logger.error(f"❌ {status} 客户端错误：请检查请求参数或API Key。\n响应内容：{e.response.text}")
                else:
                    self.logger.error(f"❌ 模型 {try_model} 请求失败：{str(e)}")
            except Exception as e:
                self.logger.error(f"❌ 模型 {try_model} 请求失败：{str(e)}")

        # 所有主模型和备用模型都失败后，尝试免费模型
        if auto_fallback or not model_try_list:
            free_models = self.get_free_models(fallback_max, only_id=True, random_pick=True)
            for i, m_id in enumerate(free_models):
                key_used = self._get_next_api_key()
                self.logger.warning(f"🎈 尝试免费模型：{m_id}")
                url = f"{self.base_url}/chat/completions"
                messages = []
                if self.system_prompt:
                    messages.append({"role": "system", "content": self.system_prompt})
                if self.assistant_prompt:
                    messages.append({"role": "assistant", "content": self.assistant_prompt})
                user_content = read_str_or_file(content)
                messages.append({"role": "user", "content": user_content})
                payload = {
                    "model": m_id,
                    "messages": messages
                }
                if body_extra:
                    payload.update(body_extra)
                headers = {
                    "Authorization": f"Bearer {key_used}",
                    "Content-Type": "application/json"
                }
                if headers_extra:
                    headers.update(headers_extra)
                self.logger.debug(f"🔑 本次请求使用的API Key: sk-******{key_used[-5:]}")
                self.logger.debug(f"📤 正在发送请求（免费模型第{i + 1}次，模型：{m_id}）")
                try:
                    with httpx.Client(timeout=30) as client:
                        response = client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        result = response.json()
                        message = result["choices"][0]["message"]["content"]
                        self.logger.debug(f"📥 接收到回复：{message}")
                        return message
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    if status == 402:
                        self.logger.error(
                            f"❌ 402 Payment Required：可能是模型ID错误、模型为付费模型或额度不足。请检查模型ID或账户余额。\n响应内容：{e.response.text}")
                    elif status == 429:
                        self.logger.error(
                            f"❌ 429 Too Many Requests：访问速率过快或账户被限，请等待或更换API Key。\n响应内容：{e.response.text}")
                    elif 400 <= status < 500:
                        self.logger.error(f"❌ {status} 客户端错误：请检查请求参数或API Key。\n响应内容：{e.response.text}")
                    else:
                        self.logger.error(f"❌ 免费模型 {m_id} 请求失败：{str(e)}")
                except Exception as e:
                    self.logger.error(f"❌ 免费模型 {m_id} 请求失败：{str(e)}")

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
                    "Authorization": f"Bearer {self._get_next_api_key()}",
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

    def get_free_models(self, limit: Optional[int] = None, only_id: bool = True, random_pick: bool = False):
        """
        获取免费模型列表
        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :param random_pick: limit生效时，是否随机选取指定数量，默认False为顺序切片
        :return: 模型id列表或模型字典列表
        """
        models = self.search_models(only_free=True)
        if limit is not None:
            if random_pick:
                models = random.sample(models, min(limit, len(models)))
            else:
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

    def _get_next_api_key(self):
        """
        获取下一个可用的API Key
        :return: API Key
        """
        if self._random_key:
            return random.choice(self._api_keys)
        else:
            key = self._api_keys[self._api_key_index]
            self._api_key_index = (self._api_key_index + 1) % len(self._api_keys)
            return key

    def get_key_status(self, api_key: Optional[str] = None) -> dict:
        """
        查询指定API Key的额度和速率限制信息
        :param api_key: 可选，指定要查询的key，不传则用当前key
        :return: 额度和速率信息字典
        """
        key = api_key or self._api_keys[self._api_key_index]
        url = f"{self.base_url}/auth/key"
        headers = {"Authorization": f"Bearer {key}"}
        try:
            resp = httpx.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            self.logger.error(f"❌ 查询API Key额度失败：{str(e)}")
            return {"error": str(e)}

    def get_keys_status(self) -> List[dict]:
        """
        查询所有API Key的额度和速率限制信息
        :return: 每个key的额度和速率信息列表
        """
        return [self.get_key_status(api_key=k) for k in self._api_keys]


class OpenRouterAsync:
    def __init__(
            self,
            api_key: Union[str, List[str]],
            random_key: bool = False,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_fallback: bool = True,
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
        :param random_key: 多key时是否随机选择key，True为随机，False为顺序
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认开启
        :param base_url: OpenRouter 的 API 地址
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径
        """
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
        self.auto_fallback = auto_fallback
        self._api_keys = api_key if isinstance(api_key, list) else [api_key]
        self._random_key = random_key
        self._api_key_index = 0

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
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        聊天接口，主模型-备用模型-免费模型顺序兜底

        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认True
        :param fallback_max: 免费模型最大尝试次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串
        """
        chosen_model = primary_model or self.primary_model
        backup_models_list = backup_models if backup_models is not None else self._backup_models
        auto_fallback = auto_fallback and self.auto_fallback
        model_try_list = []
        if chosen_model:
            model_try_list.append(chosen_model)
        if backup_models_list:
            model_try_list.extend(backup_models_list)

        # 先顺序尝试主模型和所有备用模型
        for idx, try_model in enumerate(model_try_list):
            key_used = self._get_next_api_key()
            if idx == 0 and chosen_model:
                self.logger.info(f"🚀 使用主模型：{try_model}")
            else:
                self.logger.warning(f"🎯 尝试备用模型：{try_model}")
            url = f"{self.base_url}/chat/completions"
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            if self.assistant_prompt:
                messages.append({"role": "assistant", "content": self.assistant_prompt})
            user_content = read_str_or_file(content)
            messages.append({"role": "user", "content": user_content})
            payload = {
                "model": try_model,
                "messages": messages
            }
            if body_extra:
                payload.update(body_extra)
            headers = {
                "Authorization": f"Bearer {key_used}",
                "Content-Type": "application/json"
            }
            if headers_extra:
                headers.update(headers_extra)
            self.logger.debug(f"🔑 本次请求使用的API Key: sk-******{key_used[-5:]}")
            self.logger.debug(f"📤 正在发送请求（第{idx + 1}次，模型：{try_model}）")
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
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 402:
                    self.logger.error(
                        f"❌ 402 Payment Required：可能是模型ID错误、模型为付费模型或额度不足。请检查模型ID或账户余额。\n响应内容：{e.response.text}")
                elif status == 429:
                    self.logger.error(
                        f"❌ 429 Too Many Requests：访问速率过快或账户被限，请等待或更换API Key。\n响应内容：{e.response.text}")
                elif 400 <= status < 500:
                    self.logger.error(f"❌ {status} 客户端错误：请检查请求参数或API Key。\n响应内容：{e.response.text}")
                else:
                    self.logger.error(f"❌ 模型 {try_model} 请求失败：{str(e)}")
            except Exception as e:
                self.logger.error(f"❌ 模型 {try_model} 请求失败：{str(e)}")

        # 所有主模型和备用模型都失败后，尝试免费模型
        if auto_fallback or not model_try_list:
            free_models = await self.get_free_models(fallback_max, only_id=True, random_pick=True)

            for i, m_id in enumerate(free_models):
                key_used = self._get_next_api_key()
                self.logger.warning(f"🎈 尝试免费模型：{m_id}")
                url = f"{self.base_url}/chat/completions"
                messages = []
                if self.system_prompt:
                    messages.append({"role": "system", "content": self.system_prompt})
                if self.assistant_prompt:
                    messages.append({"role": "assistant", "content": self.assistant_prompt})
                user_content = read_str_or_file(content)
                messages.append({"role": "user", "content": user_content})
                payload = {
                    "model": m_id,
                    "messages": messages
                }
                if body_extra:
                    payload.update(body_extra)
                headers = {
                    "Authorization": f"Bearer {key_used}",
                    "Content-Type": "application/json"
                }
                if headers_extra:
                    headers.update(headers_extra)
                self.logger.debug(f"🔑 本次请求使用的API Key: sk-******{key_used[-5:]}")
                self.logger.debug(f"📤 正在发送请求（免费模型第{i + 1}次，模型：{m_id}）")
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        result = response.json()
                        if callable(result):
                            result = await response.json()
                        message = result["choices"][0]["message"]["content"]
                        self.logger.debug(f"📥 接收到回复：{message}")
                        return message
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    if status == 402:
                        self.logger.error(
                            f"❌ 402 Payment Required：可能是模型ID错误、模型为付费模型或额度不足。请检查模型ID或账户余额。\n响应内容：{e.response.text}")
                    elif status == 429:
                        self.logger.error(
                            f"❌ 429 Too Many Requests：访问速率过快或账户被限，请等待或更换API Key。\n响应内容：{e.response.text}")
                    elif 400 <= status < 500:
                        self.logger.error(f"❌ {status} 客户端错误：请检查请求参数或API Key。\n响应内容：{e.response.text}")
                    else:
                        self.logger.error(f"❌ 免费模型 {m_id} 请求失败：{str(e)}")
                except Exception as e:
                    self.logger.error(f"❌ 免费模型 {m_id} 请求失败：{str(e)}")

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
                        "Authorization": f"Bearer {self._get_next_api_key()}",
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

    async def get_free_models(self, limit: Optional[int] = None, only_id: bool = True, random_pick: bool = False):
        """
        获取免费模型列表（异步）

        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :param random_pick: limit生效时，是否随机选取指定数量，默认False为顺序切片
        :return: 模型id列表或模型字典列表
        """
        models = await self.search_models(only_free=True)
        if limit is not None:
            if random_pick:
                models = random.sample(models, min(limit, len(models)))
            else:
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

    def _get_next_api_key(self):
        """
        获取下一个可用的API Key
        :return: API Key
        """
        if self._random_key:
            return random.choice(self._api_keys)
        else:
            key = self._api_keys[self._api_key_index]
            self._api_key_index = (self._api_key_index + 1) % len(self._api_keys)
            return key

    async def get_key_status(self, api_key: Optional[str] = None) -> dict:
        """
        查询指定API Key的额度和速率限制信息（异步）
        :param api_key: 可选，指定要查询的key，不传则用当前key
        :return: 额度和速率信息字典
        """
        key = api_key or self._api_keys[self._api_key_index]
        url = f"{self.base_url}/auth/key"
        headers = {"Authorization": f"Bearer {key}"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json().get("data", {})
        except Exception as e:
            self.logger.error(f"❌ 查询API Key额度失败：{str(e)}")
            return {"error": str(e)}

    async def get_keys_status(self) -> List[dict]:
        """
        查询所有API Key的额度和速率限制信息（异步）
        :return: 每个key的额度和速率信息列表
        """
        return [await self.get_key_status(api_key=k) for k in self._api_keys]


class OpenRouter:
    def __init__(
            self,
            api_key: Union[str, List[str]],
            random_key: bool = False,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_fallback: bool = True,
            base_url: str = "https://openrouter.ai/api/v1",
            logger: Optional[logging.Logger] = None,
            system_prompt: Optional[str] = None,
            assistant_prompt: Optional[str] = None,
            async_mode: bool = False,
            console_log_level: str = "INFO",
            log_file_level: str = "WARNING",
            log_file: Optional[str] = None,
            not_print_welcome: bool = False
    ):
        """
        OpenRouter 的 Python SDK，用于与 OpenRouter 的 API 进行交互

        :param api_key: OpenRouter 的 API Key，必填
        :param random_key: 多key时是否随机选择key，True为随机，False为顺序
        :param primary_model: 主模型，优先级最高，必填
        :param backup_models: 备用模型ID列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认开启
        :param base_url: OpenRouter 的 API 地址，默认 https://openrouter.ai/api/v1
        :param logger: 可选，传入自定义日志对象
        :param system_prompt: 可选，系统角色的默认提示（字符串或文件路径）
        :param assistant_prompt: 可选，助手角色的默认提示（字符串或文件路径）
        :param async_mode: True为异步，False为同步，默认False
        :param console_log_level: 控制台日志级别
        :param log_file_level: 文件日志级别
        :param log_file: 日志文件路径，当log_file为None时，将不保存日志文件，log_file_level参数将无效
        :param not_print_welcome: 是否打印欢迎信息，默认False
        """
        self.async_mode = async_mode
        if not async_mode:
            self._impl = OpenRouterSync(
                api_key=api_key,
                random_key=random_key,
                primary_model=primary_model,
                backup_models=backup_models,
                auto_fallback=auto_fallback,
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
                random_key=random_key,
                primary_model=primary_model,
                backup_models=backup_models,
                auto_fallback=auto_fallback,
                base_url=base_url,
                logger=logger,
                system_prompt=system_prompt,
                assistant_prompt=assistant_prompt,
                console_log_level=console_log_level,
                log_file_level=log_file_level,
                log_file=log_file
            )
        if not not_print_welcome:
            print(f"🚀 欢迎使用由微信公众号：XiaoqiangClub 编写的 OpenRouter 测试工具，工具仅用于学习测试，请合法使用！")

    def chat(
            self,
            content: str,
            primary_model: Optional[str] = None,
            backup_models: Optional[List[str]] = None,
            auto_fallback: bool = True,
            fallback_max: int = 2,
            reset_user_model: bool = True,
            headers_extra: Optional[Dict[str, str]] = None,
            body_extra: Optional[Dict[str, Any]] = None
    ):
        """
        聊天接口，主模型-备用模型-免费模型顺序兜底

        :param content: 用户的消息内容（字符串或文件路径）
        :param primary_model: 主模型，优先级最高，若为None则用实例的primary_model
        :param backup_models: 备用模型列表，主模型失效时自动尝试
        :param auto_fallback: 启用最新免费模型作为最后的容灾模型，默认True
        :param fallback_max: 自动使用免费模型的尝试次数
        :param reset_user_model: 若使用备用模型成功响应，下次是否恢复用户设定的模型
        :param headers_extra: 可选，额外的请求头（用于 Referer 或 X-Title）
        :param body_extra: 可选，额外的 body 参数
        :return: 模型回复的内容字符串（同步为str，异步为coroutine）
        """
        return self._impl.chat(
            content=content,
            primary_model=primary_model,
            backup_models=backup_models,
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

    def get_free_models(self, limit: Optional[int] = None, only_id: bool = True, random_pick: bool = False):
        """
        获取免费模型列表（同步/异步统一接口）

        :param limit: 返回模型数量，None为全部
        :param only_id: 是否只返回模型id，True只返回id，False返回完整字典
        :param random_pick: limit生效时，是否随机选取指定数量，默认False为顺序切片
        :return: 模型id列表或模型字典列表（同步为list，异步为coroutine）
        """
        return self._impl.get_free_models(limit=limit, only_id=only_id, random_pick=random_pick)

    def get_key_status(self, api_key: Optional[str] = None):
        """
        查询指定API Key的额度和速率限制信息（同步/异步统一接口）
        :param api_key: 可选，指定要查询的key，不传则用当前key
        :return: 额度和速率信息字典（同步为dict，异步为coroutine）
        """
        return self._impl.get_key_status(api_key=api_key)

    def get_keys_status(self):
        """
        查询所有API Key的额度和速率限制信息（同步/异步统一接口）
        :return: 每个key的额度和速率信息列表（同步为list，异步为coroutine）
        """
        return self._impl.get_keys_status()

    def __getattr__(self, item):
        return getattr(self._impl, item)

    def __dir__(self):
        # 让编辑器能自动提示OpenRouterSync/Async的所有方法和属性
        return list(set(dir(self._impl)) | set(super().__dir__()))
