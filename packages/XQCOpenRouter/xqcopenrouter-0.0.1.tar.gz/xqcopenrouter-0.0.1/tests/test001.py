"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/7 12:15
文件描述：
文件路径：/tests/test001.py
"""
from openrouter import OpenRouter

t = OpenRouter(api_key="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")
# print(t.get_free_models(1,False))
print(t.chat("你好"))