# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250605-101458
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
测试 pyFlarum ，发现有如下几个问题：
1. 仅支持用户名密码，不支持API-KEY
2. 官方文档与封装的API函数不匹配，学习成本太高
3. 放弃该库，但可参考
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
import os
from pyflarum import FlarumUser, Filter
from dotenv import load_dotenv


class CFlarumBase:
    def __init__(self, sWorkDir):
        PrintTimeMsg('CFlarumBase.__init__')
        # sWorkDir 是工作目录，其下的 flarum.env 文件就是环境变量参数文件
        if sWorkDir:
            self.sWorkDir = sWorkDir
        else:
            self.sWorkDir = os.getcwd()
        PrintTimeMsg(f'CFlarumBase.sWorkDir={self.sWorkDir}=')
        # self.oControlCron = control_cron(self.sWorkDir)

        # sEnvDir = GetSrcParentPath(__file__, True)
        sEnvFN = os.path.join(self.sWorkDir, 'flarum.env')
        # sEnvFN = os.path.join(self.sWorkDir, 'flarumBrain.env')
        bLoad = load_dotenv(dotenv_path=sEnvFN)  # load environment variables from .env
        PrintTimeMsg(f"CFlarumBase.load_dotenv({sEnvFN})={bLoad}")
        if not bLoad:
            exit(-1)

        self.sFlarumUrl = os.getenv("FLARUM_URL")
        self.sFlarumToken = os.getenv("FLARUM_TOKEN")
        self.sFlarumTagFocus = os.getenv("FLARUM_TAG_FOCUS")
        self.sCronParamDefault = os.getenv("CRON_PARAM_DEFAULT")

        self.bDebugPrint = True  # 控制是否打印日志

        self.oFU = FlarumUser(forum_url=self.sFlarumUrl,
                              username_or_email='***',
                              password='***',
                              )
        for discussion in self.oFU.get_discussions():
            print(type(discussion))  # <class 'DiscussionFromBulk'>
        for posts in self.oFU.get_posts(filter=Filter(additional_data={'discussion': '14'})):
            # 这种Filter写法不能按 discussion 过滤，具体写法不知道，也可能根本就不支持
            print(posts)  # <class 'DiscussionFromBulk'>



def mainCFlarumBase():
    sWorkDir = r'E:\WeberSrcRoot\Rocky9GogsRoot\RobotAgentMCP\FileIoDumpDeal'
    o = CFlarumBase(sWorkDir)


if __name__ == '__main__':
    mainCFlarumBase()

