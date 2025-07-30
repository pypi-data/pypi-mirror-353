"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/7 10:41
文件描述：获取提示词和日志工具
文件路径：/src/openrouter/openrouter.py
"""
import os
import logging
from typing import Optional


def read_str_or_file(obj: str) -> str:
    """
    判断输入是字符串内容还是文件路径，如果是文件路径则读取文件内容，否则直接返回字符串。
    :param obj: 字符串内容或文件路径
    :return: 文件内容或原字符串
    """
    if not obj:
        return ""
    if os.path.isfile(obj):
        with open(obj, "r", encoding="utf-8") as f:
            return f.read()
    return obj


def logger_init(
        name: str = "OpenRouter",
        console_log_level: str = "INFO",
        log_file_level: str = "WARNING",
        log_file: Optional[str] = None,
        log_debug_format: bool = False,
) -> logging.Logger:
    """
    日志初始化工具
    :param name: logger名称
    :param console_log_level: 控制台日志等级
    :param log_file_level: 文件日志等级
    :param log_file: 日志文件路径
    :param log_debug_format: 日志格式
    :return: logger对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fmt = (
            "%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
            if log_debug_format
            else "%(asctime)s - %(levelname)s：%(message)s"
        )
        # 控制台handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, console_log_level.upper(), logging.INFO))
        ch.setFormatter(logging.Formatter(fmt))
        logger.addHandler(ch)
        # 文件handler
        if log_file:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(getattr(logging, log_file_level.upper(), logging.WARNING))
            fh.setFormatter(logging.Formatter(fmt))
            logger.addHandler(fh)
    return logger
