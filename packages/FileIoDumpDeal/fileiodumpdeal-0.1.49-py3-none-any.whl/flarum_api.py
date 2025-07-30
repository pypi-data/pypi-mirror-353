# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250507-153558
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装Flarum API
[Discussion 讨论](https://justjavac.gitbooks.io/flarum/content/using/api.html)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg
from weberFuncs import PrettyPrintStr
import os
import json
import requests
from dotenv import load_dotenv
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


class flarum_api:
    # 封装FlarumAPI
    def __init__(self, sWorkDir=''):
        # sWorkDir 是工作目录，其下的 flarum.env 文件就是环境变量参数文件
        if sWorkDir:
            self.sWorkDir = sWorkDir
        else:
            self.sWorkDir = os.getcwd()
        PrintTimeMsg(f'flarum_api.sWorkDir={self.sWorkDir}=')
        # self.oControlCron = control_cron(self.sWorkDir)

        # sEnvDir = GetSrcParentPath(__file__, True)
        sEnvFN = os.path.join(self.sWorkDir, 'flarum.env')
        # sEnvFN = os.path.join(self.sWorkDir, 'flarumBrain.env')
        bLoad = load_dotenv(dotenv_path=sEnvFN)  # load environment variables from .env
        PrintTimeMsg(f"flarum_api.load_dotenv({sEnvFN})={bLoad}")
        if not bLoad:
            exit(-1)

        self.sFlarumUrl = os.getenv("FLARUM_URL")
        self.sFlarumToken = os.getenv("FLARUM_TOKEN")
        self.sFlarumTagFocus = os.getenv("FLARUM_TAG_FOCUS")
        self.sCronParamDefault = os.getenv("CRON_PARAM_DEFAULT")

        self.bDebugPrint = True  # 控制是否打印日志

        self.dictTagIdByTagSlug = {}  # TagId 与 Slug 映射关系
        self.dictTagSlugByTagId = {}

    def debug_json_print_object(self, oJson, sDebugFN):
        # 格式化输出json数据到调试文件，仅在
        if not self.bDebugPrint:
            return
        with open(sDebugFN, 'w', encoding='utf8') as f:
            sOut = json.dumps(oJson, indent=4)
            f.write(sOut)

    def _create_new_discussion_by_tag_id(self, sTitle, sContent, sTagId):
        # 按某个标签Id创建新的讨论话题
        # 这里需要填入Tag标签ID，需要统一转为Slug
        dictPost = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "title": sTitle,
                    "content": sContent
                },
                "relationships": {
                    "tags": {
                        "data": [
                            {
                                "type": "tags",
                                "id": sTagId
                            }
                        ]
                    }
                }
            }
        }
        return self._post_call('/api/discussions', dictPost)

    def create_new_discussion_by_tag_slug(self, sTitle, sContent, sTagSlug):
        # 按某个标签Id创建新的讨论话题
        if not self.dictTagIdByTagSlug:
            self.get_all_tags_dict_map()
        sTagId = self.dictTagIdByTagSlug.get(sTagSlug, '')
        if not sTagId:
            PrintTimeMsg(f"create_new_discussion_by_tag_slug.sTagSlug={sTagSlug}=NotExists!")
            return None
        return self._create_new_discussion_by_tag_id(sTitle, sContent, sTagId)

    def reply_discussion_post(self, sDiscussionId, sContent):
        # 针对某个讨论话题回帖
        dictPost = {
            "data": {
                "type": "posts",
                "attributes": {
                    "content": sContent
                },
                "relationships": {
                    "discussion": {
                        "data": {
                            "type": "discussions",
                            "id": sDiscussionId
                        }
                    }
                }
            }
        }
        return self._post_call('/api/posts', dictPost)

    def modify_post_by_post_id(self, sPostId, sContent):
        # 通过post_id修改某个讨论话题回帖
        dictPost = {
            "data": {
                "type": "posts",
                "attributes": {
                    "content": sContent
                },
                "id": sPostId
            }
        }
        return self._post_call(f'/api/posts/{sPostId}', dictPost, 'PATCH')

    def modify_discussion_title_by_discussion_id(self, sDiscussionId, sTitle):
        # 通过discussion_id修改某个讨论话题标题
        dictPost = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "title": sTitle
                },
                "id": sDiscussionId
            }
        }
        return self._post_call(f'/api/discussions/{sDiscussionId}', dictPost, 'PATCH')

    def show_discussion_by_discussion_id(self, sDiscussionId):
        # 通过discussion_id恢复（显示）某个讨论话题
        return self._show_hide_discussion_by_discussion_id(sDiscussionId, False)

    def hide_discussion_by_discussion_id(self, sDiscussionId):
        # 通过discussion_id删除（隐藏）某个讨论话题
        return self._show_hide_discussion_by_discussion_id(sDiscussionId, True)

    def _show_hide_discussion_by_discussion_id(self, sDiscussionId, isHidden):
        # 通过discussion_id删除（隐藏）/恢复（显示）某个讨论话题
        dictPost = {
            "data": {
                "type": "discussions",
                "attributes": {
                    "isHidden": isHidden
                },
                "id": sDiscussionId
            }
        }
        return self._post_call(f'/api/discussions/{sDiscussionId}', dictPost, 'PATCH')

    def _show_hide_post_by_post_id(self, sPostId, isHidden):
        # 通过post_id删除（隐藏）/恢复（显示）某个讨论话题回帖
        dictPost = {
            "data": {
                "type": "posts",
                "attributes": {
                    "isHidden": isHidden
                },
                "id": sPostId
            }
        }
        return self._post_call(f'/api/posts/{sPostId}', dictPost, 'PATCH')

    def hide_post_by_post_id(self, sPostId):
        # 通过post_id删除（隐藏）某个讨论话题回帖
        return self._show_hide_post_by_post_id(sPostId, True)

    def show_post_by_post_id(self, sPostId):
        # 通过post_id恢复（显示）某个讨论话题回帖
        return self._show_hide_post_by_post_id(sPostId, False)

    def delete_post_by_post_id(self, sPostId):
        # 通过post_id永久删除某个讨论话题回帖
        # 列在此处，仅为展示该API的用法；实际并不需要该API
        dictPost = {}
        return self._post_call(f'/api/posts/{sPostId}', dictPost, 'DELETE')

    def delete_discussion_by_discussion_id(self, sDiscussionId):
        # 通过discussion_id永久删除某个讨论话题
        # 列在此处，仅为展示该API的用法；实际并不需要该API
        dictPost = {}
        return self._post_call(f'/api/discussions/{sDiscussionId}', dictPost, 'DELETE')

    def _post_call(self, sUrlPath, dictPayload, sMethodOverride=''):
        # 向Flarum发送 POST 请求， sUrlPath = /api/discussions
        # dictPayload 提交的数据
        # sMethodOverride 添加 x-http-method-override 的方法，默认为空不添加
        #   添加 x-http-method-override = PATCH 以模拟 PATCH 方法
        sUrl = f'{self.sFlarumUrl}{sUrlPath}'
        PrintTimeMsg(f'_post_call.sUrl={sUrl}={sMethodOverride}=')
        dictHeaders = {
            "Authorization": f"Token {self.sFlarumToken}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        if sMethodOverride:
            dictHeaders['x-http-method-override'] = sMethodOverride  # 'PATCH'
        try:
            response = requests.post(sUrl, headers=dictHeaders, json=dictPayload)
            if response.status_code in [201, 200]:
                PrintTimeMsg(f"_post_call.ok:len(response.text)={len(response.text)}={response.status_code}=")
                oJson = response.json()
                if self.bDebugPrint:
                    PrintTimeMsg(f"_post_call.oJson={PrettyPrintStr(oJson)}")
                return oJson
            else:
                PrintTimeMsg(f"_post_call.error:status_code={response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            PrintTimeMsg(f"_post_call.e={str(e)}=")
        return None

    def _get_call(self, sUrlPath):
        # 向Flarum发送 GET 请求， sUrlPath = /api/discussions
        sUrl = f'{self.sFlarumUrl}{sUrlPath}'
        PrintTimeMsg(f'_get_call.sUrl={sUrl}=')
        dictHeaders = {
            "Authorization": f"Token {self.sFlarumToken}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        try:
            response = requests.get(sUrl, headers=dictHeaders)
            if response.status_code in [201, 200]:
                PrintTimeMsg(f"_get_call.ok:len(response.text)={len(response.text)}={response.status_code}=")
                oJson = response.json()
                if self.bDebugPrint:
                    # PrintTimeMsg(f"_get_call.oJson={PrettyPrintStr(oJson)[:900]}")
                    PrintTimeMsg(f"_get_call.oJson={str(oJson)[:]}")
                return oJson
            else:
                PrintTimeMsg(f"_get_call.error:status_code={response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            PrintTimeMsg(f"_get_call({sUrl}).e={str(e)}=")
        return None

    def get_all_tags_dict_map(self):
        # 调用 GET /api/tags - 获取全部tag id 和 slug映射关系
        oJson = self._get_call(f'/api/tags')
        lsTagNameSlug = []
        self.dictTagIdByTagSlug = {}
        self.dictTagSlugByTagId = {}
        for post in oJson['data']:
            sType = post['type']
            if sType != 'tags':
                continue
            sId = post['id']
            dictAttr = post['attributes']
            sSlug = dictAttr['slug']
            sName = dictAttr['name']
            self.dictTagIdByTagSlug[sSlug] = sId
            self.dictTagSlugByTagId[sId] = sSlug
            lsTagNameSlug.append((sId, sSlug, sName))
        PrintTimeMsg(f"get_all_tags().lsTagNameSlug={PrettyPrintStr(lsTagNameSlug)}")
        return lsTagNameSlug

    def _get_posts(self, sParam):
        # 调用 GET /api/posts - 获取并过滤讨论话题
        return self._get_call(f'/api/posts{sParam}')

    def get_posts_dict_by_discussion_id(self, sDiscussionId):
        # 根据关注标签，获取讨论话题的标识和标题字典
        # WeiYF.20250512 经测试，无法按tagid进行过滤，只能按tag的slug过滤
        sParam = f'?filter[discussion]={sDiscussionId}'
        oJson = self._get_posts(sParam)
        self.debug_json_print_object(oJson, r'E:\tmp\get_posts_dict_by_discussion_id.json')

    def _get_discussions(self, sParam):
        # 调用 GET /api/discussions - 获取并过滤讨论话题
        return self._get_call(f'/api/discussions{sParam}')

    def get_discussion_dict_by_tag(self, sFocusTag):
        # 根据关注标签，获取讨论话题的标识和标题字典
        # WeiYF.20250512 经测试，无法按tagid进行过滤，只能按tag的slug过滤
        sParam = f'?filter[tag]={sFocusTag}'
        oJson = self._get_discussions(sParam)
        dictTitleByDiscussionId = {}
        if oJson:
            for post in oJson['data']:
                sId = post['id']
                dictAttr = post['attributes']
                dictTitleByDiscussionId[sId] = dictAttr['title']
        PrintTimeMsg(f"get_discussion_dict_by_tag({sFocusTag}).dictTitleByDiscussionId={PrettyPrintStr(dictTitleByDiscussionId)}")
        return dictTitleByDiscussionId

    def get_reply_dict_by_discussion_id(self, sDiscussionId):
        # 根据讨论话题标识，获取回帖标识和标题字典
        # Python3.6+ 默认是有序字典
        #   但通过 PrettyPrintStr 格式化后的是按key排序后的
        #   采用items和keys方式正常遍历，得到就是最添加到字典的顺序
        sParam = f'/{sDiscussionId}'
        oJson = self._get_discussions(sParam)
        # 经排查，该API在回帖内容较多情况下，返回 included 数据包含的回帖不全，但 data.relationships 中是全的
        # self.debug_json_print_object(oJson, r'E:\tmp\_get_discussions.json')
        dictReplyInfo = {}
        dictUserName = {}
        if oJson:
            lsPosts = get_from_dict_default(oJson, 'data.relationships.posts.data')
            for post in lsPosts:
                dictReplyInfo[post['id']] = {}
            for post in oJson.get('included', []):
                if post['type'] == 'posts':
                    sContent = get_from_dict_default(post, 'attributes.content')
                    if not sContent:
                        sContent = get_from_dict_default(post, 'attributes.contentHtml')
                        sContent = get_clean_text_from_html(sContent)
                    dictReplyInfo[post['id']] = {
                        'createdAt': get_from_dict_default(post, 'attributes.createdAt'),
                        'sContent': sContent,
                        'user_id': get_from_dict_default(post, 'relationships.user.data.id'),
                    }
                if post['type'] == 'users':
                    dictUserName[post['id']] = get_from_dict_default(post, 'attributes.displayName')
            # PrintTimeMsg(f"get_reply_dict_by_discussion_id({sId}).sContent={dictPostTitleById[sId]}=")
        # PrintTimeMsg(f"get_reply_dict_by_discussion_id({sDiscussionId}).dictPostTitleById={PrettyPrintStr(dictPostTitleById)}")
        for dictV in dictReplyInfo.values():
            if 'user_id' in dictV:
                # 合并 sUserName 到 dictReplyInfo
                user_id = dictV['user_id']
                sUserName = dictUserName.get(user_id, user_id)
                dictV['sUserName'] = sUserName
        if self.bDebugPrint:
            for sId, dictV in dictReplyInfo.items():
                sContent = dictV.get('sContent', '')
                PrintTimeMsg(f"get_reply_dict_by_discussion_id({sId}).sContent={sContent[:20]}=")
        # lsId = dictPostTitleById.keys()
        # PrintTimeMsg(f"get_reply_dict_by_discussion_id({sDiscussionId}).lsId={PrettyPrintStr(lsId)}")
        return dictReplyInfo

    def get_title_topic_by_discussion_id(self, sDiscussionId):
        # 根据讨论话题标识，获取话题的内容
        sParam = f'/{sDiscussionId}'
        oJson = self._get_discussions(sParam)
        dictTitleTopic = {}
        if oJson:
            post = oJson.get('data', {})
            if post['type'] == 'discussions':
                dictTitleTopic['id'] = post['id']
                dictTitleTopic['title'] = get_from_dict_default(post, 'attributes.title')
                dictTitleTopic['createdAt'] = get_from_dict_default(post, 'attributes.createdAt')
            for post in oJson.get('included', []):
                if post['type'] == 'posts':
                    sContent = get_from_dict_default(post, 'attributes.content')
                    if not sContent:
                        sContent = get_from_dict_default(post, 'attributes.contentHtml')
                        sContent = get_clean_text_from_html(sContent)
                    dictTitleTopic['sContent'] = sContent
                    break  # First
        if self.bDebugPrint:
            PrintTimeMsg(f"get_title_topic_by_discussion_id({sDiscussionId}).dictTitleTopic={dictTitleTopic}=")
        return dictTitleTopic

    def get_self_notifications(self):
        # 取得当前用户被提到的通知信息字典
        oJson = self._get_call(f'/api/notifications')
        # ?filter[isRead]=false 测试无法过滤已读通知
        # contentType 取值有 userMentioned/postMentioned
        dictNotiInfo = {}
        dictPostInfo = {}
        if oJson:
            for post in oJson.get('data', []):
                if post['type'] == 'notifications':
                    isRead = get_from_dict_default(post, 'attributes.isRead')
                    if isRead: continue
                    dictNotiInfo[post['id']] = {
                        'createdAt': get_from_dict_default(post, 'attributes.createdAt'),
                        'contentType': get_from_dict_default(post, 'attributes.contentType'),
                        'user_id': get_from_dict_default(post, 'relationships.fromUser.data.id'),
                        'post_id': get_from_dict_default(post, 'relationships.subject.data.id'),
                    }
            for post in oJson.get('included', []):
                if post['type'] == 'posts':
                    # sContent = get_from_dict_default(post, 'attributes.content')
                    # if not sContent:
                    #     sContent = get_from_dict_default(post, 'attributes.contentHtml')
                    #     if sContent:
                    #         sContent = get_clean_text_from_html(sContent)
                    #     else:
                    #         sContent = ''
                    # sContent = remove_mention_info(sContent)
                    dictPostInfo[post['id']] = {
                        # 'post_content': sContent,
                        'discussion_id': get_from_dict_default(post, 'relationships.discussion.data.id'),
                    }
        # PrintTimeMsg(f"get_self_notifications().dictNotiInfo={PrettyPrintStr(dictNotiInfo)}")
        # PrintTimeMsg(f"get_self_notifications().dictPostInfo={PrettyPrintStr(dictPostInfo)}")
        for dictV in dictNotiInfo.values():
            post_id = dictV['post_id']
            dictP = dictPostInfo.get(post_id, {})
            dictV.update(dictP)
            # 合并 dictPostInfo 到 dictNotiInfo
        if self.bDebugPrint:
            PrintTimeMsg(f"get_self_notifications().dictNotiInfo={PrettyPrintStr(dictNotiInfo)}")
        return dictNotiInfo

    def gen_chat_list_from_reply(self, dictReplyInfo, sPostId):
        # 通过 dictReplyInfo, sPostId 生成聊天字典列表
        iPostId = int(sPostId)
        listDictChat = []
        for post_id, dictReply in dictReplyInfo.items():
            if int(post_id) <= iPostId:
                listDictChat.append(dictReply)
        if self.bDebugPrint:
            PrintTimeMsg(f"gen_chat_list_from_reply().listDictChat={PrettyPrintStr(listDictChat)}")
        return listDictChat

    def gen_chat_dict_by_disc_post_id(self, sDiscussionId, sPostId):
        # 通过 sDiscussionId, sPostId 生成聊天字典列表
        dictReplyInfo = self.get_reply_dict_by_discussion_id(sDiscussionId)
        return self.gen_chat_list_from_reply(dictReplyInfo, sPostId)

    def mark_read_notification(self, sNotificationId):
        # 通过sNotificationId标记某个通知已读
        dictPost = {
            "data": {
                "type": "notifications",
                "attributes": {
                    "isRead": True
                },
                "id": sNotificationId
            }
        }
        return self._post_call(f'/api/notifications/{sNotificationId}', dictPost, 'PATCH')

    def _get_discussion_posts(self, sParam):
        # 调用 GET /api/discussions - 获取并过滤讨论话题
        return self._get_call(f'/api/posts{sParam}')


def main_flarum_api():
    sWorkDir = r'E:\WeberSrcRoot\Rocky9GogsRoot\RobotAgentMCP\FileIoDumpDeal'
    o = flarum_api(sWorkDir)
    # o._get_discussions('?filter[tag]=general&sort&page[offset]=0')
    # o.get_discussion_dict_by_tag('general')
    # o.get_reply_dict_by_discussion_id('6')
    # o.get_title_topic_by_discussion_id('6')
    # o.modify_post_by_post_id('5', '测试程序自动发帖改贴mod.auto')
    # o.show_post_by_post_id('21')
    # o.delete_post_by_post_id('21')
    # o.get_reply_dict_by_discussion_id('6')
    # o.modify_discussion_title_by_discussion_id('13', 'test2.auto')
    # o.get_focus_discussion_dict()
    # sTestDir = r"E:\WeberSrcRoot\Rocky9GogsRoot\RobotAgentMCP\FileIoDumpDeal\run"
    # o.dump_file_4_query_discussion(sTestDir)
    # o.reply_discussion_post('6', 'main_flarum_api.auto.1')
    # o.modify_discussion_post('6', 'main_flarum_api.auto.1')
    # o.get_all_tags_dict_map()
    # o.create_new_discussion_by_tag_slug('测试发表新的话题', '测试发表新的内容api.1', 'general')
    # o.get_discussion_dict_by_tag('general')
    # o.get_discussion_dict_by_tag('1')
    # o._get_discussions('?filter[tagid]=2')  # 经测试，无法按tagid进行过滤
    # o.reply_discussion_post(20, 'main_flarum_api.auto.4 @admin')
    # o._get_discussion_posts('/163')
    # o._get_discussions('/13')
    # o.reply_discussion_post('13', '机器人回复1')
    # o.get_reply_dict_by_discussion_id('13')
    # o.get_title_topic_by_discussion_id('13')
    # o.get_self_notifications()
    # dictReplyInfo = o.get_reply_dict_by_discussion_id('13')
    # dictReplyInfo = o.get_reply_dict_by_discussion_id('14')
    # o.gen_chat_list_from_reply(dictReplyInfo, '187')
    # o.get_posts_dict_by_discussion_id('14')
    o._get_posts('/208')


if __name__ == '__main__':
    main_flarum_api()
