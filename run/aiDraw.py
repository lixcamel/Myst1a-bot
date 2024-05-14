# -*- coding: utf-8 -*-

import yaml
from mirai import Image
from mirai import GroupMessage

from plugins.RandomStr import random_str
from plugins.aiDrawer import SdDraw ,draw, airedraw, draw1, draw3,tiktokredraw,draw5,draw4


def main(bot,logger):
    logger.info("ai绘画 启用")
    global redraw
    redraw={}
    
    @bot.on(GroupMessage)
    async def AiSdDraw(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")#由于SD的无审查性，请不要输入R18词条，例如：nsfw，否则号没了
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("由于SD的无审查性，请不要输入R18词条，例如：nsfw，否则号没了")
            logger.info("发起SDai绘画请求，path:" + path + "|prompt:" + tag)
            try:
                p = await SdDraw(tag, path)
                #logger.error(str(p))
                
                await bot.send(event, [Image(path=p)], True)
                #logger.info("success")
            except Exception as e:
                logger.error(e)
                logger.error("绘画失败，可能是绘画接口寄了，请检查plugins\aiDrawer.py中url有效")
    
    @bot.on(GroupMessage)
    async def aidrawf1(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag=str(event.message_chain).replace("画 ","")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:"+path+"|prompt:"+tag)
            i = 1
            while i < 8:
                try:
                    logger.info(f"接口1绘画中......第{i}次请求....")
                    p=await draw1(tag,path)
                    logger.error(str(p))
                    await bot.send(event,[Image(path=p[0]),Image(path=p[1]),Image(path=p[2]),Image(path=p[3])],True)
                except Exception as e:
                    logger.error(e)
                    logger.error("接口1绘画失败.......")
                    i+=1
                    #await bot.send(event,"接口1绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff2(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag=str(event.message_chain).replace("画 ","")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口2绘画中......")
                p=await draw(tag,path)
                await bot.send(event,Image(path=p),True)
            except Exception as e:
                logger.error(e)
                logger.error("接口2绘画失败.......")
                #await bot.send(event,"接口2绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff3(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            if len(tag)>100:
                return
            try:
                logger.info("接口3绘画中......")
                p = await draw3(tag, path)
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口3绘画失败.......")
    @bot.on(GroupMessage)
    async def aidrawff4(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口5绘画中......")
                p = await draw5(tag, path)
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口5绘画失败.......")
    @bot.on(GroupMessage)
    async def aidrawff5(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口4绘画中......")
                p = await draw4(tag, path)
                await bot.send(event, Image(path=p), True)
            except Exception as e:
                logger.error(e)
                logger.error("接口4绘画失败.......")
    @bot.on(GroupMessage)
    async def rededd(event: GroupMessage):
        global redraw
        if str(event.message_chain).startswith("以图生图 "):
            await bot.send(event,"请发送图片，bot随后将开始绘制")
            redraw[event.sender.id]=str(event.message_chain).replace("以图生图 ","")
    @bot.on(GroupMessage)
    async def redrawStart(event: GroupMessage):
        global redraw
        if event.message_chain.count(Image) and event.sender.id in redraw:
            prompt=redraw.get(event.sender.id)
            lst_img = event.message_chain.get(Image)
            url1 = lst_img[0].url
            logger.info(f"以图生图,prompt:{prompt} url:{url1}")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                p=await airedraw(prompt,url1,path)
                await bot.send(event,Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event,"接口1绘画出错")
            try:
                p=await tiktokredraw(prompt,url1,path)
                await bot.send(event,Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event,"接口2绘画出错")
            redraw.pop(event.sender.id)
