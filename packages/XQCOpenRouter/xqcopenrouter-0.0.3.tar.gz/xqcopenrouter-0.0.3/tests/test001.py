"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/7 12:15
文件描述：
文件路径：/tests/test001.py
"""
import time

from tests.test_openrouter import test_async_chat_and_prompt

start_time = time.time()
from openrouter import OpenRouter

t = OpenRouter(api_key="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", async_mode=True)
# # print(t.get_free_models(3,True))
# print(t.chat("你好", primary_model="deepseek/deepseek-r1-0528-qwen3-8b:free2",
#              backup_models=['deepseek/deepseek-r1-0528:free2',
#                             'sarvamai/sarvam-m:free2', "deepseek/deepseek-r1-0528-qwen3-8b:free2"], fallback_max=2))
# print(t.chat("你好",))


if __name__ == '__main__':
    import asyncio


    async def main():
        # print(await t.chat("你好",))

        print(await t.chat("你好", primary_model="deepseek/deepseek-r1-0528-qwen3-8b:free2",
                           backup_models=['deepseek/deepseek-r1-0528:free2',
                                          'sarvamai/sarvam-m:free2', "deepseek/deepseek-r1-0528-qwen3-8b:free2"],
                           fallback_max=2))


    asyncio.run(main())

print(f"耗时：{time.time() - start_time}s")
