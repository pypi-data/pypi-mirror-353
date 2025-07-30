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

t = OpenRouter(api_key=["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",
                        "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"], async_mode=False,
               console_log_level="DEBUG",
               random_key=False)
# t = OpenRouter(api_key="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", async_mode=False)
# print(t.get_free_models(10, True))
# ['deepseek/deepseek-r1-0528-qwen3-8b:free', 'deepseek/deepseek-r1-0528:free', 'sarvamai/sarvam-m:free', 'mistralai/devstral-small:free', 'google/gemma-3n-e4b-it:free', 'meta-llama/llama-3.3-8b-instruct:free', 'nousresearch/deephermes-3-mistral-24b-preview:free', 'microsoft/phi-4-reasoning-plus:free', 'microsoft/phi-4-reasoning:free', 'opengvlab/internvl3-14b:free']
# print(t.chat("你好", primary_model="deepseek/deepseek-r1-0528-qwen3-8b:free",
#              backup_models=['deepseek/deepseek-r1-0528:free2',
#                             'sarvamai/sarvam-m:free2', "deepseek/deepseek-r1-0528-qwen3-8b:free2"], fallback_max=2))
print(t.chat("你好", primary_model='microsoft/phi-4-reasoning-plus:free'))
# print(t.get_key_status())
# {'label': 'sk-or-v1-e6d...61a', 'limit': None, 'usage': 0, 'is_provisioning_key': False, 'limit_remaining': None, 'is_free_tier': True, 'rate_limit': {'requests': 10, 'interval': '10s'}}
# {'label': 'sk-or-v1-018...029', 'limit': None, 'usage': 0, 'is_provisioning_key': False, 'limit_remaining': None, 'is_free_tier': True, 'rate_limit': {'requests': 10, 'interval': '10s'}}
# if __name__ == '__main__':
#     import asyncio
#
#
#     async def main():
#         # print(await t.chat("你好",))
#
#         print(await t.chat("你好", primary_model="google/gemma-3-27b-it:free",
#                            backup_models=['deepseek/deepseek-r1-0528:free',
#                                           'sarvamai/sarvam-m:free', "deepseek/deepseek-r1-0528-qwen3-8b:free"],
#                            fallback_max=2))
#
#
#     asyncio.run(main())
#
# print(f"耗时：{time.time() - start_time}s")
