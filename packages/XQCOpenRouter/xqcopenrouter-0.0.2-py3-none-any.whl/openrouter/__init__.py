"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/7 10:48
文件描述：高效、易用的 OpenRouter API Python 客户端，支持同步与异步调用。
文件路径：/src/openrouter/__init__.py
"""
from .utils import read_str_or_file
from .openrouter import OpenRouter, OpenRouterSync, OpenRouterAsync

__all__ = [
    "OpenRouter",
    "OpenRouterSync",
    "OpenRouterAsync",
    "read_str_or_file"
]
