'''
name:达美乐最新脚本V2
author:食翔狂魔
desc:加密参数改为每个账号独立获取
ck格式:备注#openid#Authorization  多号@连接，需要自行搭建接口，穿透出去后填到apiUrl那儿
version:v3.7
'''
import os
import asyncio
import aiohttp
from os import environ, path
import datetime
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
KAMI = "食翔狂魔" #卡密，不用动
apiUrl = '自己搭建的接口' #必填
KAMI2 = "" #狂魔自己用的其它人不需要不用管
isAutoLogin = False #狂魔自己用的其它人不需要不用管

send=""
giftName = {
    "001": '一等奖 免费披萨券',
    "002": '二等奖 半价披萨券',
    "003": '三等奖 免费嫩汁鸡块券',
    "004": '四等奖 免费任意口味一对烤翅券',
    "005": '五等奖 免费招牌蛋挞',
    "006": '六等奖 免费当季特饮',
}
globalScore = {}

TARGET_HOUR = 10  # 目标小时
TARGET_MINUTE = 31  # 目标分钟
TARGET_DELAY_MS = 1  # 提前xxx毫秒

# 加载通知服务函数保持不变
def load_send():
    global send
    cur_path = path.abspath(path.dirname(__file__))
    if path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            print("加载通知服务成功！")
        except ImportError:
            send = None
            print("加载通知服务失败~")
    else:
        send = None
        print("加载通知服务失败~")

#load_send()
def getJm(t,openid="",remark=""):
    json_data = {'kami': KAMI, 'jmtype': t,'openid':openid}

    response = requests.post(apiUrl, json=json_data)
    data = response.json()
    if "error" not in data and len(data["result"]) > 0:
        print(f"【{remark}】调用{t}加密接口成功! " + data["msg"])
        return data["result"]
    else:
        print(f"【{remark}】调用{t}加密接口失败! " + response.text)
        getJm(t,openid)
        return False
def getCode():
    json_data = {'kami': KAMI2, 'jmtype': "wxcode","openid":"132"}

    response = requests.post(apiUrl, json=json_data)
    data = response.json()
    return data["code"]
def login(e=""):
    url = 'https://game.dominos.com.cn/spring/v2/onLogin?code=' + getCode()
    response = requests.get(url)
    return response.json()["content"]["accessToken"]
async def getIsPsza(session, account, message_list, remark, gameid,token):
    try:
        arrAc = account.split("#")
        url = f"https://game.dominos.com.cn/{gameid}/v2/game/myPrize?pageSize=10000"
        params = {'openid': arrAc[0]}
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Zoom Edition Build/SKQ1.211006.001; wv) AppleWebKit/537.36",
            'Authorization':"Bearer " + token
        }
        
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            if data["errorMessage"] == "UNAUTHORIZED_ERROR":
                print(f"【{remark}】:登录失效。")
            id_counts = {}
            for item in data["content"]:
                gid = item['id']
                if gid in id_counts:
                    id_counts[gid] += 1
                else:
                    id_counts[gid] = 1
            for gid, count in id_counts.items():
                print(f"【{remark},{giftName[gid]}】:{count} 张。")
                message_list.append(f"【{remark},{giftName[gid]}】:{count} 张。" + "<br />\n")
            if data["statusCode"] == 0 and any(d.get("id") == "001" for d in data["content"]):
                return f"{arrAc[0]}，恭喜，已获得过免费披萨！"
            elif data["statusCode"] == 0:
                return f"{arrAc[0]}，遗憾，还未获得免费披萨！"
            else:
                return "用户不存在"
    except Exception as e:
        print(f"getIsPsza error: {e}")
        return str(e)

async def share_done(session, openid, message_list, remark, gameid,token):
    shrurl = f"https://game.dominos.com.cn/{gameid}/v2/game/sharingDone"
    payload ={
        "openid": openid,
        "from": 1,
        "target": 0,
        "encrypt": globalScore[openid+"gshare"]
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Referer': "https://servicewechat.com/wx887bf6ad752ca2f3/63/page-frame.html",
        'Authorization':"Bearer " + token
    }
    tag = True
    while True:
        try:
            async with session.post(shrurl, data=payload, headers=headers) as res:
                data = await res.json()
                print(f"【{remark}】开始执行分享：")
                if data['errorMessage'] == "UNAUTHORIZED_ERROR":
                    print(f"【{remark}】"+"登陆失效，重抓Authorization")
                    tag = False
                    break
                if data['errorMessage'] == "今日分享已用完，请明日再来":
                    message_list.append(f"【{remark}】" + "分享：今日分享已用完，请明日再来" + "<br />\n")
                    print(f"【{remark}】"+f'分享：今日分享已用完，请明日再来')
                    break 
                elif data['errorMessage'] == "用户不存在":
                    message_list.append(f"【{remark}】" + "分享：用户不存在" + "<br />\n")
                    print(f"【{remark}】" + "分享：用户不存在")
                    tag = False
                    break
                elif data['errorMessage'] == "异常":
                    print(f"【{remark}】" + "分享：异常")
                    message_list.append(f"【{remark}】" + "分享：异常" + "<br />\n")
                    tag = False
                    break
                else:
                    print(f"【{remark}】" + "分享：成功！")
            break
        except Exception as e:
            print(f"share_done: {e}")
            break
    return tag

async def game_done(session, openid, score, message_list, remark, gameid,token):
    url = f"https://game.dominos.com.cn/{gameid}/v2/game/gameDone"
    payload = {
    'openid': "ojOaM5ILuObRk-csjx92hCR_ThhQ",
    'score': globalScore[openid+"gscore"],
    'tempId': "null"
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 15; PKG110 Build/UKQ1.231108.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300333 MMWEBSDK/20240404 MMWEBID/9496 MicroMessenger/8.0.49.2600(0x28003133) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        'Accept-Encoding': "gzip,compress,br,deflate",
        'authorization': "Bearer " + token,
        'charset': "utf-8",
        'Referer': "https://servicewechat.com/wx887bf6ad752ca2f3/72/page-frame.html"
    }
    while True:
        try:
            async with session.post(url, data=payload, headers=headers) as response:
                data = await response.json()
                print(f"【{remark}】开始执行游戏：")
                if data["statusCode"] == 0:
                    prize = data['content']['name']
                    now = datetime.datetime.now()
                    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S') + ',{:03d}'.format(now.microsecond // 1000)
                    print(f"【{remark}】{prize}")
                    message_list.append(f"【{remark}】{prize}<br />\n")
                else:
                    err = data['errorMessage']
                    print(f"【{remark}】{err}")
                    message_list.append(f'【{remark}】{err}<br />\n')
                    break
                break
        except Exception as e:
            print(f"game_done error: {e}")
            break

async def process_account(session, account, message_list, stats, gameid):
    arrAc = account.split("#")
    if isAutoLogin == True and arrAc[0]=="狂魔2":
        arrAc[2] = login()
        print(arrAc[2])
    rshare = await share_done(session, arrAc[1], message_list, arrAc[0], gameid,arrAc[2])

    # if rshare == False:
    #     return
    await game_done(session, arrAc[1], "", message_list, arrAc[0], gameid,arrAc[2])

    strispsza = await getIsPsza(session, account, message_list, arrAc[0], gameid,arrAc[2])
    message_part = f"<br />\n账号【{arrAc[0]}】:\n<br />{strispsza}\n<br />"
    
    if "恭喜" in strispsza:
        stats['hasWin'].append(f"【{arrAc[0]}】")
        stats['hasCount'] += 1
    message_list.append(message_part)

async def main():
    # 定义需要并发处理的游戏ID元组及其对应的环境变量名
    gameids_and_envvars = (
        ("spring", "dmlck2"),
        #("bocconcini", "dmlck")
    )

    async with aiohttp.ClientSession() as session:
        tasks = []
        all_message_lists = {}
        all_stats = {}

        for gameid, env_var in gameids_and_envvars:
            accounts = environ.get(env_var)
            if not accounts:
                print(f'环境变量 {env_var} 未填写！')
                continue
            
            accounts_list = accounts.split('@')
            num_of_accounts = len(accounts_list)
            print(f"获取到 {num_of_accounts} 个账号对于 gameid {gameid}")

            message_list = []
            stats = {'hasCount': 0, 'hasWin': [],'allCount':num_of_accounts}
            all_message_lists[gameid] = message_list
            all_stats[gameid] = stats
            
            for account in accounts_list:
                aarr = account.split("#")
                gscore = getJm("score",aarr[1],aarr[0])
                if gscore == False:
                    continue
                globalScore[account.split("#")[1]+"gscore"] = gscore
                gshare = getJm("share",aarr[1],aarr[0])
                if gshare == False:
                    continue
                globalScore[account.split("#")[1]+"gshare"] = gshare
                task = asyncio.create_task(process_account(session, account, message_list, stats, gameid))
                tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        final_messages = []
        for gameid, message_list in all_message_lists.items():
            stats = all_stats[gameid]
            message = ''.join(message_list)
            message += f'中奖情况（{gameid}）：{stats["hasCount"]}/{stats["allCount"]}<br />\n'
            message += f'部分已中奖名单（{gameid}）：{"、".join(stats["hasWin"])}<br />\n'
            final_messages.append(message)
        
        final_message = '\n'.join(final_messages)
        
        if send:
            print("\n\n\n\nfinal_message")
            print(final_message)
            #send('达美乐', final_message)
        else:
            print("\n\n\n\nfinal_message")
            print(final_message)

if __name__ == '__main__':
    for i in range(30):

        asyncio.run(main())
        
        time.sleep(30)
