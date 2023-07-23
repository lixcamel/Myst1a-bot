# -*- coding:utf-8 -*-
import datetime
import json
import os.path
import random
import re
import urllib
from asyncio import sleep

import httpx
import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models.events import BotInvitedJoinGroupRequestEvent, NewFriendRequestEvent, MemberJoinRequestEvent, \
    MemberHonorChangeEvent, MemberCardChangeEvent, BotMuteEvent, MemberSpecialTitleChangeEvent, BotJoinGroupEvent

from plugins.setuModerate import setuModerate
from plugins.vitsGenerate import voiceGenerate


def main(bot,config,moderateKey,logger):
    # 读取设置
    global moderateK
    moderateK=moderateKey
    logger.info("读取群管设置")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global banWords
    banWords=result.get("moderate").get("banWords")
    #读取用户数据
    logger.info("读取用户数据")
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global userdict
    userdict = data


    global blackList
    blackList= result.get("banUser")
    global blGroups
    blGroups= result.get("banGroups")

    global blackListID
    blackListID=[]

    global master
    master=int(config.get('master'))

    moderate=result.get("moderate")

    global threshold
    threshold=moderate.get("threshold")


    global severGroups
    severGroups=moderate.get("groups")
    global banTime
    banTime=moderate.get("banTime")

    @bot.on(BotJoinGroupEvent)
    async def botJoin(event:BotJoinGroupEvent):
        await bot.send_group_message(event.group.id,"已加入服务群聊....")
        await bot.send_group_message(event.group.id,"发送 @bot 帮助 以获取功能列表\n项目地址：https://github.com/avilliai/Manyana\n喜欢bot的话可以给个star哦(≧∇≦)ﾉ")
        path="../data/autoReply/voiceReply/joinGroup.wav"
        ok=os.path.exists(path)
        if ok:
            await bot.send_group_message(event.group.id,Voice(path=path[3:]))
        else:
            data={'text':"[JA]みなさん、こんにちは、私はこのグループのメンバーになりました、将来もっとアドバイスしてください![JA]","path":path}
            await voiceGenerate(data)
            await bot.send_group_message(event.group.id,Voice(path=path[3:]))
        await bot.send_group_message(event.group.id,"发送 帮助 获取功能列表哦")

    @bot.on(Startup)
    async def updateData(event: Startup):
        while True:
            await sleep(60)
            # 读取用户数据
            logger.info("更新用户数据")
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global userdict
            userdict = data

    @bot.on(BotInvitedJoinGroupRequestEvent)
    async def allowStranger(event: BotInvitedJoinGroupRequestEvent):
        logger.info("接收来自 "+str(event.from_id)+" 的加群邀请")
        if str(event.from_id) in userdict.keys():
            if int(userdict.get(str(event.from_id)).get("sts"))>5:
                if event.group_id in blGroups:
                    await bot.send_friend_message(event.from_id,"该群在黑名单内")
                    return
                logger.info("同意")
                al = '同意'
                sdf="请先向目标群群员确认是否愿意接受bot加群"
                await bot.send_friend_message(event.from_id,sdf)
                await bot.send_friend_message(event.from_id,"40秒后自动同意")
                await sleep(40)
                await bot.allow(event)
            else:
                logger.info("签到天数不够，拒绝")
                al = '拒绝'
                await bot.send_friend_message(event.from_id,"群内签到天数不够呢(6)次，明天再来试试吧。也可联系master"+str(master)+" 获取授权")
        else:
            logger.info("非用户，拒绝")
            al = '拒绝'
        await bot.send_friend_message(master, '有新的加群申请\n来自：' + str(event.from_id) + '\n目标群：' + str(event.group_id) + '\n昵称：' + event.nick + '\n状态：' + al)


    @bot.on(NewFriendRequestEvent)
    async def allowStranger(event: NewFriendRequestEvent):
        logger.info("新的好友申请，来自"+str(event.from_id))
        if str(event.from_id) in userdict.keys():
            logger.info("有用户记录，同意")
            al='同意'
            await bot.allow(event)
            await sleep(5)
            await bot.send_friend_message(event.from_id,"你好ヾ(≧▽≦*)o，如有使用疑问请在用户群628763673反馈")
            await bot.send_friend_message(event.from_id, "群内发送 帮助 获取功能列表")
        else:
            logger.info("无用户记录，拒绝")
            al='拒绝'
        await bot.send_friend_message(master,'有新的好友申请\n来自：'+str(event.from_id)+'\n来自群：'+str(event.group_id)+'\n昵称：'+event.nick+'\n状态：'+al)



    @bot.on(MemberJoinRequestEvent)
    async def allowStrangerInvite(event: MemberJoinRequestEvent):
        logger.info("有新群员加群申请")
        if event.from_id in blackList:
            await bot.send_group_message(event.group_id,"有新的入群请求，存在bot黑名单记录")
        else:
            await bot.send_group_message(event.group_id,'有新的入群请求.....管理员快去看看吧\nQQ：'+str(event.from_id)+'\n昵称：'+event.nick+'\nextra:：'+event.message)

    @bot.on(MemberSpecialTitleChangeEvent)
    async def honorChange(event: MemberSpecialTitleChangeEvent):
        logger.info("群员称号改变")
        await bot.send_group_message(event.member.group.id, str(event.member) + '获得了称号：' + str(event.current))

    @bot.on(MemberCardChangeEvent)
    async def nameChange(event: MemberCardChangeEvent):
        if len(event.current) > 0:
            logger.info("群员昵称改变")
            await bot.send_group_message(event.member.group.id,
                                         event.origin + ' 的昵称改成了 ' + event.current + ' \n警惕新型皮套诈骗')


    @bot.on(BotMuteEvent)
    async def BanAndBlackList(event: BotMuteEvent):
        logger.info("bot被禁言，操作者"+str(event.operator.id))
        global blackList
        global blGroups
        blackList.append(event.operator.id)
        blGroups.append(event.operator.group.id)
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        result["banUser"]=blackList
        result["banGroups"]=blGroups
        with open('config/settings.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(result, file, allow_unicode=True)
        await bot.send_friend_message(master,'bot在群:\n'+str(event.operator.group.name)+str(event.operator.group.id)+'\n被禁言'+str(event.duration_seconds)+'秒\n操作者id：'+str(event.operator.id)+'\nname:('+str(event.operator.member_name)+')\n已退群并增加不良记录')
        await bot.quit(event.operator.group.id)
        logger.info("已退出群 "+str(event.operator.group.id)+" 并拉黑")

    @bot.on(FriendMessage)
    async def quiteG(event:FriendMessage):
        if str(event.message_chain).startswith("退群#") and str(event.sender.id)==str(master):
            dataG=str(event.message_chain).split("#")[1]
            try:
                await bot.quit(int(dataG))
                logger.info("退出："+str(dataG))
                await bot.send_friend_message(int(master),"已退出: "+str(dataG))
            except:
                logger.warning("不正确的群号")

    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        global banWords
        if str(event.group.id) in banWords.keys():
            group=str(event.sender.group.id)
            try:
                banw=banWords.get(group)

                for i in banw:
                    if i in str(event.message_chain) and i!="":
                        id = event.message_chain.message_id
                        logger.info("获取到违禁词列表" + str(banw))
                        try:
                            await bot.recall(id)
                            logger.info("撤回违禁消息"+str(event.message_chain))
                            await bot.send(event,"检测到违禁词"+i+"，撤回")
                        except:
                            logger.error("关键词撤回失败！")
                        try:
                            await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=banTime)
                            await bot.send(event, "检测到违禁词" + i + "，禁言")
                        except:
                            logger.error("禁言失败，权限可能过低")

            except:
                pass
    @bot.on(GroupMessage)
    async def checkBanWords(event:GroupMessage):
        global banWords
        if At(bot.qq) in event.message_chain and "违禁词" in str(event.message_chain) and "查" in str(event.message_chain):
            group = str(event.sender.group.id)
            banw = str(banWords.get(group)).replace(",",",\n")
            await bot.send(event,"本群违禁词列表如下：\n"+banw)

    @bot.on(GroupMessage)
    async def addBanWord(event:GroupMessage):
        global banWords
        if (str(event.sender.permission)!="Permission.Member" or str(event.sender.id)==str(master)) and "添加违禁词" in str(event.message_chain):
            msg = "".join(map(str, event.message_chain[Plain]))
            # 匹配指令
            m = re.match(r'^添加违禁词\s*(.*)\s*$', msg.strip())
            if m:
                aimWord = m.group(1)
                if str(event.sender.group.id) in banWords:
                    banw=banWords.get(str(event.sender.group.id))
                    banw.append(aimWord)
                    banWords[str(event.sender.group.id)]=[aimWord]
                else:
                    banWords[str(event.sender.group.id)]=[aimWord]
                with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                moderate=result.get("moderate")

                moderate["banWords"]=banWords
                result["moderate"]=moderate
                with open('config/settings.yaml', 'w',encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)
                await bot.send(event,"已添加违禁词："+aimWord)
    @bot.on(GroupMessage)
    async def removeBanWord(event:GroupMessage):
        global banWords
        if (str(event.sender.permission) != "Permission.Member" or str(event.sender.id) == str(
                master)) and "删除违禁词" in str(event.message_chain):
            msg = "".join(map(str, event.message_chain[Plain]))
            # 匹配指令
            m = re.match(r'^删除违禁词\s*(.*)\s*$', msg.strip())
            if m:
                aimWord = m.group(1)
                try:
                    newData=banWords.get(str(event.sender.group.id)).remove(aimWord)
                    banWords[str(event.sender.group.id)]==newData
                    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                        result = yaml.load(f.read(), Loader=yaml.FullLoader)
                    moderate = result.get("moderate")
                    moderate["banWords"] = banWords
                    result["moderate"] = moderate
                    with open('config/settings.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(result, file, allow_unicode=True)

                    await bot.send(event,"已移除违禁词："+aimWord)
                except:
                    await bot.send(event, "没有已添加的违禁词：" + aimWord)

    @bot.on(GroupMessage)
    async def geturla(event:GroupMessage):
        global moderateK
        global severGroups
        if str(event.group.permission)!=str('Permission.Member') and event.message_chain.count(Image) and str(event.group.id) in severGroups :
            lst_img = event.message_chain.get(Image)

            for i in lst_img:
                url=i.url
                logger.info("图片审核:url:" + url+" key:"+moderateK)
                rate=await setuModerate(url,moderateK)
                logger.info("图片审核:结果:" + str(rate))
                threshold=severGroups.get(str(event.group.id))
                if rate>threshold:
                    await bot.send(event, "检测到图片违规\npredictions-adult:" + str(rate))
                    try:
                        await bot.recall(event.message_chain.message_id)
                    except:
                        logger.error("撤回图片失败")
                    try:
                        await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=banTime)
                    except:
                        logger.error("禁言失败，权限可能过低")
                    return
    @bot.on(GroupMessage)
    async def geturla(event:GroupMessage):
        global moderateK
        global severGroups
        if  event.message_chain.count(Image)==1 and "ping" in str(event.message_chain):
            lst_img = event.message_chain.get(Image)
            url = lst_img[0].url
            logger.info("图片审核:url:" + url)
            rate = await setuModerate(url, moderateK)
            logger.info("图片审核:结果:" + str(rate))
            await bot.send(event, "图片检测结果：\npredictions-adult:" + str(rate))

    @bot.on(GroupMessage)
    async def setConfiga(event:GroupMessage):
        global threshold
        global severGroups
        if 1==1:
            if str(event.message_chain).startswith("/阈值") and (str(event.sender.permission)!="Permission.Member" or event.sender.id==master) :

                temp=int(str(event.message_chain)[3:])
                if temp>100 or temp<0:
                    await bot.send(event,"设置阈值不合法")
                else:
                    try:
                        threshold=temp
                        severGroups[str(event.group.id)] = temp
                        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                            result = yaml.load(f.read(), Loader=yaml.FullLoader)
                        moderate = result.get("moderate")
                        moderate["groups"] = severGroups
                        result["moderate"] = moderate
                        with open('config/settings.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(result, file, allow_unicode=True)

                        await bot.send(event,"成功修改撤回阈值为"+str(temp))
                    except:
                        await bot.send(event,"阈值设置出错，请进入config.json中手动设置threshold值")

        if (str(event.sender.permission)!="MEMBER"  or event.sender.id==master )and str(event.message_chain)=="/moderate":
            if str(event.group.id) in severGroups:
                logger.info("群:"+str(event.group.id)+" 关闭了审核")
                severGroups.pop(str(event.group.id))
                await bot.send(event,"关闭审核")
            else:
                logger.info("群:" + str(event.group.id) + " 开启了审核")
                severGroups[str(event.group.id)]=40
                await bot.send(event,"开启审核")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            moderate = result.get("moderate")
            moderate["groups"] = severGroups
            result["moderate"] = moderate
            with open('config/settings.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(result, file, allow_unicode=True)
            await bot.send(event, "ok")
    @bot.on(GroupMessage)
    async def exitBadGroup(event:GroupMessage):
        ls=["你妈","傻逼","艹逼","你妈","死你","垃圾"]
        if At(bot.qq) in event.message_chain:
            for i in ls:
                if i in str(event.message_chain):
                    logger.warn("遭到："+str(event.sender.id)+" 的辱骂,执行退群。群号:"+str(event.group.id))
                    await bot.quit(event.group.id)
                    return


