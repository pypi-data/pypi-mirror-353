import os
import asyncio
from openrouter import OpenRouter, OpenRouterSync, OpenRouterAsync, read_str_or_file
from unittest.mock import patch


def test_read_str_or_file():
    # 测试字符串
    assert read_str_or_file("hello") == "hello"
    # 测试文件
    with open("test_prompt.txt", "w", encoding="utf-8") as f:
        f.write("文件内容测试")
    assert read_str_or_file("test_prompt.txt") == "文件内容测试"
    os.remove("test_prompt.txt")


def test_sync_chat_and_prompt():
    client = OpenRouterSync(api_key="sk-xxx",
                            primary_model="model-main", backup_models=["model-bak1", "model-bak2"],
                            system_prompt="你是AI", assistant_prompt="你好")
    # 动态修改prompt
    client.set_system_prompt("新系统提示")
    client.set_assistant_prompt("新助手提示")
    assert client.system_prompt == "新系统提示"
    assert client.assistant_prompt == "新助手提示"
    # 测试文件参数
    with open("user_input.txt", "w", encoding="utf-8") as f:
        f.write("文件输入内容")
    try:
        client.chat("user_input.txt")
    except Exception:
        pass
    os.remove("user_input.txt")
    # 测试备用模型设置
    client.set_backup_models(["bak3", "bak4"])
    assert client._backup_models == ["bak3", "bak4"]
    # 测试自动免费模型兜底
    client2 = OpenRouterSync(api_key="sk-xxx")
    try:
        client2.chat("测试自动免费模型")
    except Exception:
        pass


def test_async_chat_and_prompt():
    async def run():
        client = OpenRouterAsync(api_key="sk-xxx",
                                 primary_model="model-main", backup_models=["model-bak1"],
                                 system_prompt="你是AI", assistant_prompt="你好")
        await client.set_system_prompt("异步系统提示")
        await client.set_assistant_prompt("异步助手提示")
        assert client.system_prompt == "异步系统提示"
        assert client.assistant_prompt == "异步助手提示"
        with open("user_input_async.txt", "w", encoding="utf-8") as f:
            f.write("异步文件输入")
        try:
            await client.chat("user_input_async.txt")
        except Exception:
            pass
        os.remove("user_input_async.txt")
        # 测试备用模型设置
        client.set_backup_models(["bak5"])
        assert client._backup_models == ["bak5"]
        # 测试自动免费模型兜底
        client2 = OpenRouterAsync(api_key="sk-xxx")
        try:
            await client2.chat("测试自动免费模型")
        except Exception:
            pass

    asyncio.run(run())


def test_openrouter_entry():
    # 测试统一入口
    sync_client = OpenRouter(api_key="sk-xxx",
                             primary_model="main", backup_models=["bak1"])
    assert isinstance(sync_client._impl, OpenRouterSync)
    async_client = OpenRouter(api_key="sk-xxx",
                              primary_model="main", backup_models=["bak1"], async_mode=True)
    assert isinstance(async_client._impl, OpenRouterAsync)
    # 测试自动免费模型兜底
    sync_client2 = OpenRouter(api_key="sk-xxx")
    try:
        sync_client2.chat("测试自动免费模型")
    except Exception:
        pass

    async def run2():
        async_client2 = OpenRouter(api_key="sk-xxx",
                                   async_mode=True)
        try:
            await async_client2.chat("测试自动免费模型")
        except Exception:
            pass

    asyncio.run(run2())


def test_search_models():
    client = OpenRouterSync(api_key="sk-xxx",
                            primary_model="main")
    try:
        client.search_models(keyword="llama", only_free=True)
    except Exception:
        pass


def test_sync_chat_fallback_order():
    client = OpenRouterSync(api_key="sk-xxx", primary_model="main", backup_models=["bak1", "bak2"])
    # mock主模型和备用模型都失败，只有免费模型成功
    with patch.object(OpenRouterSync, 'search_models', return_value=[{"id": "free1"}, {"id": "free2"}]):
        with patch("httpx.Client.post") as mock_post:
            # 前3次抛异常（主+2备），第4次成功
            mock_post.side_effect = [Exception("fail1"), Exception("fail2"), Exception("fail3"),
                                     type("Resp", (), {"raise_for_status": lambda s: None, "json": lambda s: {
                                         "choices": [{"message": {"content": "free-ok"}}]}})()]
            result = client.chat("hi", fallback_max=2)
            assert result == "free-ok"


def test_async_chat_fallback_order():
    import types
    async def run():
        client = OpenRouterAsync(api_key="sk-xxx", primary_model="main", backup_models=["bak1", "bak2"])
        # mock主模型和备用模型都失败，只有免费模型成功
        with patch.object(OpenRouterAsync, 'search_models', return_value=[{"id": "free1"}, {"id": "free2"}]):
            with patch("httpx.AsyncClient.post") as mock_post:
                # 前3次抛异常（主+2备），第4次成功
                async def raise_exc(*a, **k): raise Exception("fail")

                async def ok_resp(*a, **k):
                    class R:
                        def raise_for_status(self): pass

                        def json(self): return {"choices": [{"message": {"content": "free-ok"}}]}

                    return R()

                mock_post.side_effect = [raise_exc, raise_exc, raise_exc, ok_resp]
                result = await client.chat("hi", fallback_max=2)
                assert result == "free-ok"

    asyncio.run(run())


def test_api_key_random_strategy():
    # 测试random_key参数下的多key切换
    keys = ["sk-1", "sk-2", "sk-3"]
    client_seq = OpenRouterSync(api_key=keys, random_key=False)
    seq_results = [client_seq._get_next_api_key() for _ in range(6)]
    assert seq_results == ["sk-1", "sk-2", "sk-3", "sk-1", "sk-2", "sk-3"]
    client_rand = OpenRouterSync(api_key=keys, random_key=True)
    rand_results = [client_rand._get_next_api_key() for _ in range(10)]
    # 随机模式下结果分布应包含所有key
    assert set(rand_results) == set(keys)


def test_get_free_models_random_pick():
    # 测试get_free_models的random_pick参数
    client = OpenRouterSync(api_key="sk-xxx")
    with patch.object(OpenRouterSync, 'search_models', return_value=[{"id": f"free{i}"} for i in range(10)]):
        # 顺序取前3
        seq = client.get_free_models(limit=3, only_id=True, random_pick=False)
        assert seq == ["free0", "free1", "free2"]
        # 随机取3个
        rand = client.get_free_models(limit=3, only_id=True, random_pick=True)
        assert len(rand) == 3 and all(r in [f"free{i}" for i in range(10)] for r in rand)
        # 不重复
        assert len(set(rand)) == 3
