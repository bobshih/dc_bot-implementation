import os
import yaml

#導入 Discord.py
import discord
intents = discord.Intents(messages=True, guilds=True, members=True)
#client 是我們與 Discord 連結的橋樑
client = discord.Client(intents=intents)

from src import Utils
from src.Bot import OnInit
# 載入 setting
settings = Utils.Load_Setting()

#調用 event 函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', client.user)
    print(dir(client))
    print(client.guilds)
    for guild in client.guilds:
        guild_data = OnInit.GetGuildData(guild)
        with open(os.path.join("data", str(guild.id) + '.yaml'), 'w', encoding='utf8') as fp:
            yaml.dump(guild_data, fp, allow_unicode=True)

@client.event
#當有訊息時
async def on_message(message):
    #排除自己的訊息，避免陷入無限循環
    if message.author == client.user:
        return
    #如果包含 ping，機器人回傳 pong
    if message.content == 'ping':
        await message.channel.send('pong')

client.run(settings.dc_bot_token) #TOKEN 在剛剛 Discord Developer 那邊「BOT」頁面裡面