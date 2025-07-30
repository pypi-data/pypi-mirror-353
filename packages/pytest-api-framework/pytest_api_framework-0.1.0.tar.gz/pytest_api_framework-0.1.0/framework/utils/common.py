import re
import os
import time
import binascii


import pyotp
import cn2an as c2a

from framework.settings import CONFIG_DIR


def generate_2fa_code(secret_key):
    """
    获取2fa code
    :return:
    """
    current_time = int(time.time())
    totp = pyotp.TOTP(secret_key)
    google_code = totp.at(current_time)

    return google_code


def is_digit(string):
    """判断是否为数字字符串"""
    digit_re = re.compile(r'^-?[0-9.]+$')
    return digit_re.search(string)


def an2cn(integer):
    """阿拉伯数字转中文数字"""
    return c2a.an2cn(integer)


def cn2an(string):
    """中文数字转阿拉伯数字"""
    return c2a.cn2an(string)


def get_current_datetime():
    """
    获取当前日期和时间 2023-02-19 08:31:51
    :return:
    """
    return time.strftime("%Y-%m-%d %X")


def valid_hex_format(s):
    """
    判断是否为16进制字符串
    :param s:
    :return:
    """
    hex_re = re.compile(r"^[0-9a-fA-F]+$")
    if hex_re.match(s):
        return True
    return False


def valid_b64_format(s):
    """
    判断是否为base64字符串
    :param s:
    :return:
    """
    b64_re = re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
    if b64_re.match(s):
        return True
    return False


def hex_to_bytes(hex_str):
    """
    16进制->字节
    :param hex_str:
    :return:
    """
    return binascii.a2b_hex(hex_str).strip()


def bytes_to_hex(byte):
    """
    字节->16进制
    :param byte:
    :return:
    """
    return binascii.b2a_hex(byte)


def singleton(cls):
    """
    单例模式装饰器
    :param cls:
    :return:
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def snake_to_pascal(name: str) -> str:
    # 将字符串按照下划线分割，然后将每个单词的首字母大写，最后连接起来
    return ''.join(word.capitalize() for word in name.split('_'))


def get_apps():
    """
    获取所有app
    """
    return [name for name in os.listdir(CONFIG_DIR) if
            os.path.isdir(os.path.join(CONFIG_DIR, name)) and not name.startswith(("__", "."))]
