# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250605-111924
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装Flarum所需的独立函数
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []  # 存储文本片段

    def handle_data(self, data):
        # 重写基类函数
        self.text_parts.append(data)  # 捕获非标签内容

    def get_clean_text(self):
        return ''.join(self.text_parts)  # 合并所有文本


def get_clean_text_from_html(sHtml):
    # 剔除HTML标签
    parser = TextExtractor()
    parser.feed(sHtml)
    return parser.get_clean_text()


def remove_mention_info(sV):
    # 从 sV 删除通知信息中提到用户名信息
    # @"用户名"#2 by Admin
    #  @RobotAI

    return sV  # 展示不处理

    iL = sV.find('@"')
    iR = sV.rfind('"#')
    if iL > 0 and iR > 0:
        sV = sV[:iL] + sV[iR + 2:]
    else:
        if sV.startswith('@'):
            iSpace = sV.find(' ')
            if iSpace > 0:
                sV = sV[iSpace + 1:]
        elif sV.endswith(' '):
            iAt = sV.rfind('@')
            if iAt > 0:
                sV = sV[:iAt]
    sV = sV.strip()
    return sV


def get_from_dict_default(dictValue, sDotKey):
    # 根据 k1.k2.k3 从dict中取得相应值
    dictV = dictValue
    for sK in sDotKey.split('.'):
        dictV = dictV.get(sK, {})
        if not isinstance(dictV, dict):  # 不是dict，则跳出
            break
    return dictV


def mainClassOne():
    # o = ClassOne()
    pass


if __name__ == '__main__':
    mainClassOne()
