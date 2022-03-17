# background worker part
import os
import urllib.request

from apscheduler.schedulers.background import BackgroundScheduler

heroku_link = os.environ['heroku_link']
# heroku_link = "http://127.0.0.1:5000/hello_world/local"

sched = BackgroundScheduler()

# @sched.scheduled_job('interval', minutes = 19)
@sched.scheduled_job('interval', seconds = 4)
def scheduled_job():
    conn = urllib.request.urlopen(heroku_link)
    print(conn.read())
    for key, value in conn.getheaders():
        print(key, value)
sched.start()

# web service part
# from flask import Flask

# app = Flask(__name__)
# @app.route("/hello_world/<source>")
# def hello_world(source):
#     print("call once by {}".format(source))
#     return f"<p>Hello, {source}!</p>"

#導入 Discord.py
import discord
from discord.ext import tasks

#client 是我們與 Discord 連結的橋樑
# 控制 bot 有哪些權限，同時必須在
intents = discord.Intents(messages=True, guilds=True, members=True)
client = discord.Client(intents=intents)
from src import Utils
from src.Bot import Bot
from src.Bot.Entity import Member_cls
# 載入 setting
settings = Utils.Load_Setting()

if __name__ == '__main__':
    # a bot
    bot = Bot(client, settings.google_api_key)

    #調用 event 函式庫
    @client.event
    #當機器人完成啟動時
    async def on_ready():
        print('目前登入身份：', client.user)
        for guild in client.guilds:
            bot.InitGuildData(guild)

    @client.event
    #當有訊息時
    async def on_message(message: discord.Message):
        #排除自己的訊息，避免陷入無限循環
        if message.author == client.user:
            return
        # 如果訊息由 += 開頭，傳入機器人內部
        if message.content.startswith("+="):
            await bot.ProcessMessage(message)
        #如果包含 ping，機器人回傳 pong
        if message.content == 'ping':
            await message.channel.send('pong')

    @client.event
    async def on_member_remove(member: discord.Member):
        print("[Debug] in on_member_remove")
        leave_member = Member_cls.Init_wMember(member)
        await bot.SendLeaveMSG(member.guild, leave_member)

    @client.event
    async def on_member_join(member: discord.Member):
        print("[Debug] in on_member_join")
        leave_member = Member_cls.Init_wMember(member)
        await bot.SendWelcomeMSG(member.guild, leave_member)

    @tasks.loop(minutes=1)
    async def BotWorking():
        print("UTC_TIMEZONE: ", os.environ['UTC_TIMEZONE'])
        await bot.DoTasks()
        for _, guild in bot.guilds.items():
            guild.UpdateGuildFile()

    BotWorking.start()
    client.run(settings.dc_bot_token) #TOKEN 在 Discord Developer 那邊「BOT」頁面裡面
    # app.run(host="0.0.0.0")
