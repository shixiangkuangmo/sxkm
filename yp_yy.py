"""
name:甬派
author:食翔狂魔
version:1.7
desc:每天最少0.4,支付宝现金
date:2025-04-16 21:26:43
log:增加农场相关功能(二改妖火@重庆第一深情)、修复Id获取异常
"""

import os
import re
import json
import string
import time
import uuid
import random
import requests
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote, urlparse, parse_qs
import urllib
import execjs
devId = "e9de40c589453658" #devId
#品赞代理链接
PINZAN = "https://service.ipzan.com/core-extract?num=1&no=202641&minute=1&format=json&pool=quality&mode=auth&secret=63o"

isProxy = True #是否启用代理
doTask = True
# from notify import send
def hide_phone_number(text):
    if not text:
        return text
    if len(text) != 11:
        return text
    return re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", text)


glo_msg = []


class TASK:
    def __init__(self, index, account):
        self.index = index
        self.name = account.get("name", None)
        self.pwd = account.get("pwd", None)
        self.zfb_name = account.get("zfb_name", None)
        self.zfb_account = account.get("zfb_account", None)
        self.isTx = account.get("tx", "y")
        self.deviceId2 = account.get("deviceId", None)
        self.deviceId = self.register_device_code() #account.get("deviceId", None)
        self.model = self.generate_random_string()
        self.vendor = self.generate_random_string()
        self.user_id = None
        self.setCk = ""
        self.nick_name = None
        self.ua = None
        self.token = None
        self.query_token = None
        self.jwtToken = None
        self.news_id = None
        self.lottery_id = None
        self.lottery_cookie = None
        self.consumerId = None
        self.wdata = ""
        self.msg = ""
        self.proxies = None
        self.push_user_id = account.get("push_user_id", None)
        self.push_im_type = account.get("push_im_type", None)
        self.ncID = None
        self.ncOpenID = None

    @staticmethod
    def generate_device_code():
        device_code = ""
        chars = "abcdef0123456789"
        for _ in range(16):
            device_code += random.choice(chars)
        return device_code

    def generate_uuid(self):
        return str(uuid.uuid4())

    def log_info(self, msg):
        print(f"用户{self.index}【{hide_phone_number(self.name)}】：{msg}")

    def log_err(self, msg):
        print(f"用户{self.index}【{hide_phone_number(self.name)}】：{msg}")

    def generate_random_string(self):
        length = random.randint(5, 8)
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choices(characters, k=length))
        return random_string
    def generate_random_string2(self):
        length = 15
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choices(characters, k=length))
        return random_string
    def generate_random_device(self):
        device_id = self.generate_device_id()
        models = [
            "M1903F2A",
            "M2001J2E",
            "M2001J2C",
            "M2001J1E",
            "M2001J1C",
            "M2002J9E",
            "M2011K2C",
            "M2102K1C",
            "M2101K9C",
            "2107119DC",
            "2201123C",
            "2112123AC",
            "2201122C",
            "2211133C",
            "2210132C",
            "2304FPN6DC",
            "23127PN0CC",
            "24031PN0DC",
            "23090RA98C",
            "2312DRA50C",
            "2312CRAD3C",
            "2312DRAABC",
            "22101316UCP",
            "22101316C",
        ]
        model = self.get_random_element(models)
        return {"deviceId": device_id, "model": model}

    def get_random_element(self, arr):
        return random.choice(arr)

    def generate_device_id(self, length=16):
        characters = string.ascii_lowercase + string.digits
        return "".join(random.choice(characters) for _ in range(int(length)))

    def is_today(self, datetime_str, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        判断给定的时间字符串是否是今天。

        :param datetime_str: 时间字符串
        :param datetime_format: 时间字符串的格式，默认为"%Y-%m-%d %H:%M:%S"
        :return: 如果是今天，返回True，否则返回False
        """
        # 将时间字符串转换为日期时间对象
        dt = datetime.strptime(datetime_str, datetime_format)
        # 获取今天的日期
        today = datetime.today().date()
        # 判断日期是否为今天
        return dt.date() == today

    def format_cookies(self, cookie_string):
        cookies = cookie_string.split(", ")
        formatted_cookies = [cookie.split(";")[0].strip() for cookie in cookies]
        return "; ".join(formatted_cookies)

    def common_get(self, path):
        headers = {
            "system": "android",
            "version": "30",
            "model": self.model,
            "appversion": "10.1.6",
            "appbuild": "202401111",
            "deviceid": self.deviceId,
            "ticket": self.token,
            "module": "web-member",
            "Authorization": f"Bearer {self.jwtToken}",
            "userid": self.user_id,
            "accept-encoding": "gzip",
            "user-agent": "PLYongPaiProject/10.1.6 (iPhone; iOS 15.4.1; Scale/3.00)",
        }
        res = requests.get(f"https://ypapp.cnnb.com.cn{path}", headers=headers)
        # self.log_info(f"{path} res {res.text}")
        if res.status_code == 200:
            return res.json()
        return None
    def register_device_code(self):
        url = "http://101.42.152.146:3030/deviceRegister"
        response = requests.get(url)
        res = response.json()
        if res["msg"] == "注册成功":
            return res["devID"]
        else:
            return self.deviceId2
        
    def login(self):
        now = int(time.time() * 1000)
        raw = f"globalDatetime{str(now)}username{self.name}test_123456679890123456"
        sign = hashlib.md5(raw.encode("utf-8")).hexdigest()

        params = {
            "username": self.name,
            "password": quote(self.pwd),
            "deviceId": self.deviceId,
            "globalDatetime": now,
            "sign": sign,
        }
        headers = {
            "system": "android",
            "version": "31",
            "model": "Redmi K30 Pro Zoom Edition",
            "appversion": "10.2.0",
            "appbuild": "202403210",
            "deviceid": self.deviceId,
            "ticket": "",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
        }
        # res = requests.get(f"https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username={self.name}&password={quote(self.pwd)}&deviceId=${self.deviceId}&globalDatetime={now}&sign={sign}",headers=headers)
        res = requests.get(
            f"https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3",
            headers=headers,
            params=params,
        )
        if "错误" in res.text:
            self.msg += f"\n{res.text}"
            return False
        if res.status_code == 200:
            rj = res.json()
            if "OK" in rj["message"]:
                self.msg += f"\n【登陆检测】：检测通过✅"
                self.msg += f"\n【用户昵称】：{rj['data']['nickname']}"
                self.msg += f"\n【绑定手机】：{hide_phone_number(rj['data']['mobile'])}"
                self.user_id = rj["data"]["userId"]
                self.log_info(f"用户id：{self.user_id}")
                self.query_token = rj["data"]["token"]
                self.nick_name = rj["data"]["nickname"]
                self.jwtToken = rj["data"]["jwtToken"]
                self.setCk = res.headers.get('Set-Cookie', '').split(';')[0]
                return True
        self.log_info(f"login  {res.text}")

    def login_get(self):
        data_string = f"/member/login{{loginName:{self.name},name:{self.nick_name},phone:{self.name},userId:{self.user_id}}}"
        sign = hashlib.md5(data_string.encode("utf-8")).hexdigest()
        params = {
            "userId": self.user_id,
            "loginName": self.name,
            "name": quote(self.nick_name),
            "phone": self.name,
        }
        headers = {
            "content-type": "application/json",
            "module": "web-member",
            "sign": sign,
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
        }
        res = requests.get(
            f"https://ypapp.cnnb.com.cn/web-nbcc/member/login",
            headers=headers,
            params=params,
        )
        if res.status_code == 200:
            rj = res.json()
            if "success" in rj["message"]:
                self.msg += f"\n【登陆结果】：登陆成功✅"
                self.token = rj["data"]
                return True
            else:
                return False
        return False

    def news_list(self):
        res = self.common_get(
            f"/yongpai-news/api/news/list?channelId=4&currentPage=1&timestamp=0"
        )
        if res:
            for news in res["data"]["content"]:
                # 条件列表
                conditions = [
                    "转盘" in news.get("keywords", ""),
                    "转盘" in news.get("title", ""),
                    "转盘" in news.get("detailTitle", ""),
                    "转一转" in news.get("detailTitle", ""),
                    "赚" in news.get("detailTitle", ""),
                    "转盘" in news.get("subtitle", ""),
                    "红包" in news.get("subtitle", "")
                    and "话费" not in news.get("subtitle", ""),
                    "领红包" in news.get("detailTitle", ""),
                    "领取一份幸运" in news.get("subtitle", ""),
                ]
                # 使用 any 函数检查是否有任何一个条件为 True
                if any(conditions) and "农场" not in news.get("subtitle", ""):
                    self.msg += f"\n【获取抽奖】：抓取抽奖活动成功✅"
                    self.log_info(f"成功获取抽奖活动：{news['newsId']}")
                    self.news_id = news["newsId"]
                    return True
        return False

    def getProxyMeta(self):
      if isProxy == False:
          self.log_info(f"代理未启用！")
          self.msg += f"代理未启用！"
          return None
      url = PINZAN
      response = requests.get(url)
      res = response.json()
      if res["status"] == 200:
          proxyMeta = f"http://{res['data']['list'][0]['account']}:{res['data']['list'][0]['password']}@{res['data']['list'][0]['ip']}:{res['data']['list'][0]['port']}"
          
          self.log_info(f"成功获取代理IP：" + proxyMeta)
          self.msg += f"成功获取代理IP：" + proxyMeta
          return proxyMeta
      else:
          return self.getProxyMeta()

    def news_detail(self):
        res = self.common_get(
            f"/yongpai-news/api/news/detail?newsId={self.news_id}&userId={self.user_id}&deviceId={self.deviceId}"
        )
        if res and res["data"]:
            match = re.search(r"\?id=(\d+)&?", res["data"]["body"])
            if match:
                self.lottery_id = re.search(r"\?id=(\d+)&?", res["data"]["body"]).group(
                    1
                )
                self.msg += f"\n【抽奖ID】：解析抽奖ID成功✅"
                self.log_info(f"【抽奖ID】：解析抽奖ID成功✅{self.lottery_id}")
                return True
            else:
                self.log_info(f"查找转盘id失败：{res}")
        return False

    def json_to_url_params(self, json_data):
        encoded_params = urllib.parse.urlencode(json_data)
        return encoded_params

    def task_list(self):
        try:
            self.msg += f"\n---------阅读----------"
            path = f"/yongpai-user/api/user/my_level?userId={self.user_id}"
            res = self.common_get(path)
            if not res:
                return
            readFinish = True
            likeFinish = True
            shareFinish = True
            for task in res["data"]["scoreRule"]:
                self.log_info(f"{task['type']}  {task['dayscore']} {task['usedScore']}")
                self.msg += f"\n{task['type']}：{task['usedScore']}/{task['dayscore']}"
                if task["dayscore"] == task["usedScore"]:
                    continue
                if task["type"] == "阅读新闻":
                    readFinish = False
                if task["type"] == "点赞":
                    likeFinish = False
                if task["type"] == "分享新闻":
                    shareFinish = False
            if not readFinish or not likeFinish or not shareFinish:
                channelIds = [2, 20183, 20184, 4, 32]
                count = 1
                read_count = 0
                like_count = 0
                share_count = 0
                for channelId in channelIds:
                    article_list_res = self.common_get(
                        f"/yongpai-news/api/news/list?channelId={channelId}&currentPage=1&timestamp=0"
                    )
                    if not article_list_res:
                        continue
                    for index, article in enumerate(
                        article_list_res["data"]["content"]
                    ):
                        if not self.is_today(
                            article.get("sourcetime", "2024-07-20 00:00:00")
                        ):
                            continue
                        if count > 30:
                            break
                        if "id" not in article:
                            continue
                        id = article["id"]
                        time.sleep(random.randint(1, 2))
                        if not readFinish:
                            read_res = self.common_get(
                                f"/yongpai-news/api/news/detail?newsId={id}&userId={self.user_id}&deviceId={self.deviceId}"
                            )
                            if read_res:
                                read_count += 1
                                self.log_info(f"阅读第{count}篇：{res.get('message')}")
                                # self.msg += f"\n阅读文章【{id}】:{read_res.get('message')}"
                        if not likeFinish:
                            time.sleep(random.randint(1, 2))
                            like_res = self.common_get(
                                f"/yongpai-ugc/api/praise/save_news?userId={self.user_id}&newsId={id}&deviceId={self.deviceId}"
                            )
                            self.log_info(f"点赞第{count}篇文章【{id}】：{like_res}")
                            if like_res and like_res.get("code") == 0:
                                count += 1
                                like_count += 1
                                self.log_info(f"点赞获得：{like_res['message']}")
                                # self.msg += f"\n点赞文章【{id}】: {like_res['message']}"
                            else:
                                self.log_info(f"文章【{id}】已点赞")
                        if not shareFinish:
                            time.sleep(random.randint(1, 2))
                            share_res = self.common_get(
                                f"/yongpai-ugc/api/forward/news?userId={self.user_id}&newsId={id}&source=4"
                            )
                            self.log_info(f"分享第{count}篇文章【{id}】：{share_res}")
                            if share_res and share_res.get("code") == 0:
                                share_count += 1
                                self.log_info(f"分享获得：{share_res['data']}积分")
                                # self.msg += f"\n分享文章【{id}】:获得{share_res['data']}积分"
                            else:
                                self.log_info(f"文章【{id}】已分享")
                self.msg += f"\n 阅读成功：{read_count}篇"
                self.msg += f"\n 点赞成功：{like_count}篇"
                self.msg += f"\n 分享成功：{share_count}篇"
        except Exception as e:
            print("task_list error")
            print(e)

    def tx(self, recordId):
        self.log_info(f"开始提现-{self.zfb_account}")
        if self.zfb_account and self.zfb_name:
            self.key_get(
                f"https://92722.activity-12.m.duiba.com.cn/activity/takePrizeNew?recordId={recordId}&dbnewopen"
            )
            getToken_res = self.lottery_post(f"/ctoken/getToken.do")
            if getToken_res:
                token = self.get_token(self.key_str, getToken_res.get("token"))
                doTakePrize_data = {
                    "alipay": self.zfb_account,
                    "realname": self.zfb_name,
                    "recordId": recordId,
                    "token": token,
                }
                self.log_info(f"提现参数：{doTakePrize_data}")
                res = self.lottery_post(
                    f"/activity/doTakePrize", self.json_to_url_params(doTakePrize_data)
                )
                self.log_info(f"提现结果：{res}")
                if res:
                    self.log_info(f"自动体现支付宝结果：{res}")
                    self.msg += f"\n提现结果：{res.get('message')}"

    def zfbtx(self, orderId, no, res):
        order_data = {"orderId": orderId, "adslotId": ""}
        order_status = 0
        count = 0
        while order_status == 0 and count < 10:
            count += 1
            order_res = self.lottery_post(
                f"/hdtool/getOrderStatus?_={int(time.time()*1000)}", order_data
            )
            if order_res and order_res["success"]:
                order_status = order_res.get("result", 0)
                if order_status == 0:
                    self.log_info(f"查询订单{orderId}状态：{res.get('message')}")
                    continue
                if order_res["lottery"]["type"] == "thanks":
                    self.msg += f"\n第{no+1}次抽奖：谢谢惠顾"
                    continue
                if order_res["lottery"]["type"] == "alipay":
                    self.log_info(f"获得支付宝红包：{order_res['lottery']['title']}")
                    self.msg += f"\n第{no+1}次抽奖：{order_res['lottery']['title']}"
                    url = order_res["lottery"]["link"]
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    result = {k: v[0] for k, v in query_params.items()}
                    recordId = result["recordId"]
                    self.log_info(f"开始提现-{self.zfb_account}")
                    if self.zfb_account and self.zfb_name:
                        self.key_get(
                            f"https://92722.activity-12.m.duiba.com.cn/activity/takePrizeNew?recordId={recordId}&dbnewopen"
                        )
                        getToken_res = self.lottery_post(f"/ctoken/getToken.do")
                        if getToken_res:
                            token = self.get_token(
                                self.key_str, getToken_res.get("token")
                            )
                            doTakePrize_data = {
                                "alipay": self.zfb_account,
                                "realname": self.zfb_name,
                                "recordId": recordId,
                                "token": token,
                            }
                            self.log_info(f"提现参数：{doTakePrize_data}")
                            res = self.lottery_post(
                                f"/activity/doTakePrize",
                                self.json_to_url_params(doTakePrize_data),
                            )
                            self.log_info(f"提现结果：{res}")
                            if res:
                                self.log_info(f"自动体现支付宝结果：{res}")
                                self.msg += f"\n提现结果：{res.get('message')}"
            else:
                self.msg += f"\查询订单状态失败：{order_res}"
                order_status = 1

    def startYy(self):
        acids = ["284364336059191", "284981603837881", "284981727582016"]
        for id in acids:
            self.lottery_id = id
            self.lottery_Login_get()
            time.sleep(1)

    def lottery_Login_get(self):
        proxyMeta = self.getProxyMeta()
        self.proxies = {
            "http": proxyMeta,
            "https": proxyMeta
        }
        params = {
            "userId": self.user_id,
            "dbredirect": f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen",
        }
        headers = {
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.1",
        }
        url = "https://ypapp.cnnb.com.cn/yongpai-user/api/duiba/autologin?${url}"
        try:
            res = requests.get(url, headers=headers, params=params,proxies=self.proxies)
            if res.status_code == 200:
                rj = res.json()
                if "OK" in rj["message"]:
                    headers = {
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "x-requested-with": "io.dcloud.H55BDF6BE",
                        "sec-fetch-site": "none",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-user": "?1",
                        "sec-fetch-dest": "document",
                        "accept-encoding": "gzip, deflate",
                        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    }
                    res = requests.get(rj["data"], headers=headers, allow_redirects=False)
                    self.lottery_cookie = self.format_cookies(res.headers["Set-Cookie"])
                    self.log_info(f"获取key")
                    self.msg += f"\n---------抽奖----------"
                    self.key_get(
                        f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen&from=login&spm=92722.1.1.1"
                    )
                    # self.get_key_api(f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen&from=login&spm=92722.1.1.1")
                    res = self.lottery_post(
                        f"/hdtool/ajaxElement?_={int(time.time()*1000)}",
                        {
                            "hdType": "dev",
                            "hdToolId": "",
                            "preview": False,
                            "actId": self.lottery_id,
                            "adslotId": "",
                        },
                    )
                    if res and res["success"]:
                        if "失败" in str(res["element"]["freeLimit"]):
                            self.msg += f"\n【抽奖次数】：获取抽奖次数失败:{res['element']['freeLimit']}"
                            self.log_info(f"获取抽奖次数失败：{res}")
                            return
                        else:
                            self.msg += f"\n【抽奖次数】：{res['element']['freeLimit']}"
                        count = res["element"]["freeLimit"]
                        self.log_info(count)
                        
                        if count == 0:
                            return
                        for no in range(0, 1):
                            token_data = {
                                "timestamp": int(time.time() * 1000),
                                "activityId": self.lottery_id,
                                "activityType": "hdtool",
                                "consumerId": self.consumerId,
                            }
                            res = self.lottery_post(
                                f"/hdtool/ctoken/getTokenNew", token_data
                            )
                            if res and res["success"]:
                                token = self.get_token(self.key_str, res["token"])
                                join_data = {
                                    "actId": self.lottery_id,
                                    "oaId": self.lottery_id,
                                    "activityType": "hdtool",
                                    "consumerId": self.consumerId,
                                    "token": token,
                                }
                                self.log_info(f"抽奖参数：{join_data}")
                                res = self.lottery_post(
                                    f"/hdtool/doJoin?dpm=92722.3.1.0&activityId={self.lottery_id}&_={int(time.time()*1000)}",
                                    join_data,
                                )
                                if res and res.get("success"):
                                    self.log_info(f"第{no+1}次抽奖：{res}")
                                    orderId = res.get("orderId", "2713157983293370443")
                                    if not orderId:
                                        continue
                                    self.zfbtx(orderId, no, res)
                                else:
                                    self.log_info(f"抽奖失败：{res}")
                                    self.msg += (
                                        f"\n抽奖结果：{res.get('message','未知错误')}"
                                    )
                    else:
                        self.log_info(f"活动异常：{res}")
        except Exception as e:
            print("lottery_Login_get")    
            print(e)    
    def key_get(self, url):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            "x-requested-with": "io.dcloud.H55BDF6BE",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": self.lottery_cookie,
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            time.sleep(2)  # Wait for 2 seconds
            regex = r"consumerId:'(\d+)'"
            match = re.search(regex, res.text)
            if match:
                self.consumerId = match.group(1)
            else:
                self.consumerId = "4136126583"

            self.log_info(f"consumerId {self.consumerId}")
            js_str = """
            function deal(res){
                let code = /<script\\b[^>]*>\s*var([\s\S]*?)<\/script>/.exec(res)[1];
                eval(code)
                key = /var\s+key\s+=\s+'([^']+)';/.exec(getDuibaToken.toString())[1];
                console.log(key)
                return key;
            }
            """
            ctx = execjs.compile(js_str)
            self.key_str = ctx.call("deal", res.text)
            self.log_info(self.key_str)

    def js_key(self):
        js_str = """
        function deal(key,res){
            window={}
            let code = /<script\\b[^>]*>\s*var([\s\S]*?)<\/script>/.exec(res)[1];
            eval(code)
            key = /var\s+key\s+=\s+'([^']+)';/.exec(getDuibaToken.toString())[1];
            return window[key];
        }
        """
        res = self.lottery_post(f"/ctoken/getToken.do")
        if res:
            ctx = execjs.compile(js_str)
            return ctx.call("deal", self.key_str, res["token"])

    def get_token(self, key, code):
        js_str = """
        function deal(key,code){
            window={}
            eval(code)
            return window[key];
        }
        """
        ctx = execjs.compile(js_str)
        token = ctx.call("deal", key, code)
        self.log_info(f"get_token  {token}")
        return token

    def lottery_post(self, path, body=None):
        url = f"https://92722.activity-12.m.duiba.com.cn{path}"
        headers = {
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://92722.activity-12.m.duiba.com.cn",
            "cookie": self.lottery_cookie,
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen&from=login&spm=92722.1.1.1",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        res = requests.post(url, headers=headers, data=body,proxies=self.proxies)
        if res.status_code == 200:
            rj = res.json()
            return rj
        return None

    def lottery_get(self, path):
        url = f"https://92722.activity-12.m.duiba.com.cn{path}"
        headers = {
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://92722.activity-12.m.duiba.com.cn",
            "cookie": self.lottery_cookie,
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen&from=login&spm=92722.1.1.1",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            rj = res.json()
            return rj
        return None

    def user_info(self):
        res = self.common_get(f"/yongpai-user/api/user/my_level?userId={self.user_id}")
        if res:
            self.msg += f"\n---------资产----------"
            self.msg += f"\n【当前积分】：{res['data']['score']}"

    def extract_span_content(self, html_string):
        pattern = r"<span[^>]*>(.*?)</span>"
        match = re.search(pattern, html_string)
        if match:
            return match.group(1)
        else:
            return ""

    def getLottery_List(self):
        count = 1
        rj = self.lottery_get(f"/crecord/getrecord?page=1&_={int(time.time()*1000)}")
        if rj != None:
            self.msg += f"\n---------记录----------"
            for item in rj["records"]:
                if count < 6:
                    exmsg = ""
                    if "待" in item["statusText"]:
                        data = json.loads(item["emdJson"])
                        self.tx(data["info"])
                        exmsg = "，已执行自动领奖。"
                    self.msg += f"\n{count}.{item['title']},时间：{item['gmtCreate']},状态：{self.extract_span_content(item['statusText'])}{exmsg}"
                    count = count + 1

    def hear(self):
        url = "http://101.42.152.146:3030/upYyTime"
        payload = {
            "user_id": self.user_id
        }
        headers = {
            "content-type": "application/json; charset=utf-8",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        res = response.json()["data"]
        if res["message"] == "OK":
            self.msg += f"\n【甬音】：刷取时长成功✅"
            self.log_info(f"甬音刷取时长成功，开始执行3次抽奖！")
            self.startYy()
        else:
            self.msg += f"\n【甬音】：刷取时长失败❌"
            self.log_info(f"甬音刷取时长失败！")


    def getFruit(self):
        sgsurl = "https://kzsv.cnnb.com.cn/Server/ypfarmapi/"
        sgsparams = {'action': "client_harvest"}
        sgspayload = {'userId': self.ncID}
        ncdlheaders = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.38 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-ch-ua': "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            'sec-ch-ua-mobile': "?1",
            'origin': "https://kzsv.cnnb.com.cn",
            'x-requested-with': "io.dcloud.H55BDF6BE",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://kzsv.cnnb.com.cn/YPFarm/?time=1236",
            'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i",
            'Cookie': self.setCk
        }
        sgsresponse = requests.post(sgsurl, params=sgsparams, data=sgspayload, headers=ncdlheaders)
        if '200' in sgsresponse.text:
            self.msg += f"\n【收果实】：成功✅"
            self.log_info(f"\n【收果实】：成功✅")
        elif '402' in sgsresponse.text:
            self.msg += f"\n【收果实】：您的果树还没有结果哦，请继续栽培！❌"
            self.log_info(f"【收果实】：您的果树还没有结果哦，请继续栽培！❌")
        else:
            self.msg += f"\n【收果实】：失败❌"
            self.log_info(f"【收果实】：失败❌")
            print(sgsresponse.text)
    def getFruitJf(self):
        dhjfurl = "https://kzsv.cnnb.com.cn/Server/ypfarmapi/"
        dhjfparams = {'action': "client_operation"}
        dhjfpayload = {'userId': self.ncID,'type': '3','openId': self.ncOpenID}
        ncdlheaders = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.38 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-ch-ua': "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            'sec-ch-ua-mobile': "?1",
            'origin': "https://kzsv.cnnb.com.cn",
            'x-requested-with': "io.dcloud.H55BDF6BE",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://kzsv.cnnb.com.cn/YPFarm/?time=1236",
            'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i",
            'Cookie': self.setCk
        }
        dhjfresponse = requests.post(dhjfurl, params=dhjfparams, data=dhjfpayload, headers=ncdlheaders)
        if '200' in dhjfresponse.text:
            self.msg += f"\n【果实兑换】：成功✅"
            self.log_info(f"\n【果实兑换】：成功✅")
        elif '503' in dhjfresponse.text:
            self.msg += f"\n【果实兑换】：物品数量有误，请确定后重试！❌"
            self.log_info(f"【果实兑换】：物品数量有误，请确定后重试！❌")
        else:
            self.msg += f"\n【收果实】：失败❌"
            self.log_info(f"【收果实】：失败❌")
            print(f"\n兑换积分：\n{dhjfresponse.text}")
        
    def make_request(self,NCURL,NCPARAMS,action):
        try:
            ncdlheaders = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.38 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
                'Accept-Encoding': "gzip, deflate, br, zstd",
                'sec-ch-ua-platform': "\"Android\"",
                'sec-ch-ua': "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                'sec-ch-ua-mobile': "?1",
                'origin': "https://kzsv.cnnb.com.cn",
                'x-requested-with': "io.dcloud.H55BDF6BE",
                'sec-fetch-site': "same-origin",
                'sec-fetch-mode': "cors",
                'sec-fetch-dest': "empty",
                'referer': "https://kzsv.cnnb.com.cn/YPFarm/?time=1236",
                'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                'priority': "u=1, i",
                'Cookie': self.setCk
            }
            response = requests.post(NCURL, params=NCPARAMS, data=action['payload'], headers=ncdlheaders)
            if '200' in response.text:
                self.msg += f"\n【农场任务】：{action['action']}成功😘"
                self.log_info(f"\n【农场任务】：{action['action']}成功😘")
            elif '502' in response.text:
                self.msg += f"\n【农场任务】：已经{action['action']}了😖"
                self.log_info(f"\n【农场任务】：已经{action['action']}了😖")
            else:
                self.msg += f"\n【农场任务】：{action['action']}失败😵"
                self.log_info(f"【农场任务】：{action['action']}失败😵")
                print(response.text)
        except requests.RequestException as e:
            print(f"请求错误: {e}")
    def farmDaily(self):
        NCURL = "https://kzsv.cnnb.com.cn/Server/ypfarmapi/"
        NCPARAMS = {'action': "client_interactive"}

        actions = [
            {'action': '浇水', 'payload': {'userId': '84390', 'type': '100'}},
            {'action': '施肥', 'payload': {'userId': '84390', 'type': '10'}},
            {'action': '除草', 'payload': {'userId': '84390', 'type': '1'}}
        ]
        for action in actions:
            self.msg += f"\n【农场任务】：开始{action['action']}😘"
            self.log_info(f"\n【农场任务】：开始{action['action']}😘")
            self.make_request(NCURL,NCPARAMS,action)
        self.getFruit()

        
    def getSeed(self):
        lqzzurl = "https://kzsv.cnnb.com.cn/Server/ypfarmapi/"
        lqzzparams = { 'action': "client_operation"}
        lqzzpayload = {  'userId': self.ncID,'type': '0','openId': self.ncOpenID}
        ncdlheaders = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.38 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-ch-ua': "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            'sec-ch-ua-mobile': "?1",
            'origin': "https://kzsv.cnnb.com.cn",
            'x-requested-with': "io.dcloud.H55BDF6BE",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://kzsv.cnnb.com.cn/YPFarm/?time=1236",
            'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            'priority': "u=1, i",
            'Cookie': self.setCk
        }
        lqzz = requests.post(lqzzurl, params=lqzzparams, data=lqzzpayload, headers=ncdlheaders)
        if '200' in lqzz.text:
            self.msg += f"\n【种子】：领取成功✅"
            self.log_info(f"【种子】：领取成功✅")
        else:
            self.msg += f"\n【种子】：领取失败,{json.loads(lqzz.content.decode('utf-8-sig'))['data']}❌"
            self.log_info(f"【种子】：领取失败,{json.loads(lqzz.content.decode('utf-8-sig'))['data']}❌")
        
        self.farmDaily()
    #农场部分来自妖火 重庆第一深情 二改
    def farm(self):
        ncdlurl = "https://kzsv.cnnb.com.cn/Server/ypfarmapi/"
        ncdlparams = {'action': "client_login"}
        ncdlpayload = {'userId': self.user_id,'nickname': self.nick_name,'token': self.query_token}
        ncdlheaders = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.38 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua': "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        'sec-ch-ua-mobile': "?1",
        'origin': "https://kzsv.cnnb.com.cn",
        'x-requested-with': "io.dcloud.H55BDF6BE",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://kzsv.cnnb.com.cn/YPFarm/?time=1236",
        'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'priority': "u=1, i",
        'Cookie': self.setCk
        }
        response = requests.post(ncdlurl, headers=ncdlheaders, data=ncdlpayload, params=ncdlparams)
        if '200' in response.text:
            self.msg += f"\n【农场】：登录成功✅"
            self.log_info(f"【农场】：登录成功✅")
            response_text = response.content.decode('utf-8-sig')
            ncdljson = json.loads(response_text)
            self.ncID = ncdljson['data']['userinfo']['ID']
            self.ncOpenID = ncdljson['data']['userinfo']['OpenID']
            self.getSeed()
        else:
            self.msg += f"\n【农场】：登录失败❌"
            self.log_info(f"【农场】：登录失败❌")
            print(response.text)
    def run(self):
        self.msg = f"【账号备注】：{hide_phone_number(self.name)}"
        if self.login():
            self.login_get()
            if self.news_list():
                self.news_detail()
                if doTask == True:
                    self.task_list()
                if self.isTx == "y":
                    self.lottery_Login_get()
                    self.hear()
                    self.user_info()
                    self.getLottery_List()
                self.farm()
            else:
                self.msg += f"\n【获取抽奖】：抓取抽奖活动失败❌，请改日再来。"
        print(self.msg)
        glo_msg.extend(self.msg.split("\n"))
        glo_msg.append("")
        glo_msg.append("")


if __name__ == "__main__":
    user_str = ""  # os.environ.get("yp_user_data","[]")
    user_data_arr = [
        {
            "name": "登录账号",
            "pwd": "密码",
            "zfb_name": "支付宝姓名(unicode编码一下,百度直接搜)",
            "zfb_account": "支付宝账号",
            "deviceId": "设备id(填不填都行,最好填)",
            "disable": "n",
            "expire": "2024-10-19",
        },
        {
            "name": "登录账号",
            "pwd": "密码",
            "zfb_name": "支付宝姓名(unicode编码一下,百度直接搜)",
            "zfb_account": "支付宝账号",
            "deviceId": "设备id(填不填都行,最好填)",
            "disable": "n",
            "expire": "2024-10-19",
        },
    ]
    if len(user_data_arr) == 0:
        print("无账号！")
        exit(0)
    print(f"开始运行，共{len(user_data_arr)}个账号")
    for index, user_data in enumerate(user_data_arr, start=1):
        if user_data["disable"] != "y":
            TASK(index, user_data).run()
            if index != len(user_data_arr):
                print(f"延迟运行1秒")
                time.sleep(1)

    # send('甬派', "\n<br />".join(glo_msg))
    print("\n<br />".join(glo_msg))
    exit(0)
