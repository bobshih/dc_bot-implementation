'''
    this class used to describe the actions of a bot in this project
'''
from collections import defaultdict
from discord import (
    Guild as dGuild,
    Message as dMessage,
    Client
)
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

from .Entity import Guild, Member, ChannelData
from ..Utils import bot_utils

BotPrefix = '+='

class Bot:
    def __init__(self, client_obj: Client):
        guild_settings = bot_utils.LoadGuildData()
        self.guilds = {
            gid: Guild(setting) for gid, setting in guild_settings.items()
        }
        channel_settings = bot_utils.LoadChannelData()
        self.client = client_obj
        # self.live_list = []             # 目前有在直播的 stream id (video id)

    def InitGuildData(self, guild: dGuild)->None:
        ''' 載入 guild 資料並更新 '''
        guild_id = guild.id
        if guild_id not in self.guilds:
            self.guilds[guild_id] = Guild.Init_wGuild(guild)
            bot_utils.SaveGuildData(guild_id, self.guilds[guild_id].GetSetting())
        else:
            print(f"[Warning] guild, {guild.name}, has been added in data.")

    async def SendWelcomeMSG(self, guild: dGuild, member: Member)->None:
        ''' send welcome message '''
        if guild.id not in self.guilds:
            print(f"[Error] guild, {guild.name} is not found")
            return
        target_channel = self.guilds[guild.id].welcome_channel
        target_text = self.guilds[guild.id].welcome_text
        # send the text
        channel = guild.get_channel(target_channel)
        if channel != None:
            await channel.send(target_text.format(user=f"<@{member.id}>", count=guild.member_count))
        else:
            print(f"[Error] guild, {guild.name}, has no channel whose id is {target_channel}")

    async def SendLeaveMSG(self, guild: dGuild, member: Member)->None:
        ''' send leave message '''
        if guild.id not in self.guilds:
            print(f"[Error] guild, {guild.name} is not found")
            return
        target_channel = self.guilds[guild.id].leave_channel
        target_text = self.guilds[guild.id].leave_text
        # send the text
        channel = guild.get_channel(target_channel)
        if channel != None:
            await channel.send(target_text.format(user=f"<@{member.id}>", count=guild.member_count))
        else:
            print(f"[Error] guild, {guild.name}, has no channel whose id is {target_channel}")
    
    def CheckLiveStreaming(self)->Dict[str, List[Tuple(str, str)]]:
        ''' 檢查有沒有 live，此函式不管是不是已經停止直播了，專心檢查是否有直播 '''
        result = defaultdict(list)
        for guild_id, guild in self.guilds.items():
            if guild.described_channels == []: continue
            if guild.notify_text_channel == '': continue
            for channel_data in guild.described_channels:
                if channel_data.live:       # 已經在 live 了，不用檢查了
                    continue
                page = requests.get(f"https://youtube.com/channel/{channel_data.id}/live")
                page_soup = BeautifulSoup(page.text, 'html.parser')
                # 取得轉址後的 html url
                link = page_soup.find('link', {'rel': 'canonical'})
                href_html = link.get('href')
                if 'watch?v=' in href_html:
                    live_streaming_id = href_html.split('watch?v=')[1]
                    # self.live_list.append(live_streaming_id)
                    channel_data.live = True
                    result[guild_id].append((channel_data.id, live_streaming_id))
        return dict(result)

    async def DoTasks(self)->None:
        ''' 機器人做事，會傳訊息出去 '''
        # 1. Check the streams which is starting
        start_streams = self.CheckLiveStreaming()
        # 2. check waiting room
        new_waiting = self.CheckWaitingRoom()
        # 3. check steam ending
        end_stream = self.CheckEndingStream()
        # 4. send messages
        # 4.1 send live message
        for guild_id, live_infos in start_streams.items():
            channel_id = self.guilds[guild_id].notify_text_channel
            notify_channel = await self.client.fetch_channel(channel_id)
            for channel_id, video_id in live_infos:
                message = self.guilds[guild_id]
                await notify_channel.send(message)

    async def ProcessMessage(self, message: dMessage)->None:
        ''' process the message '''
        guild_id = message.guild.id
        channel = message.channel
        message_segs = message.content[len(BotPrefix):].strip().split(' ')
        if len(message_segs) < 3:
            await channel.send("看不懂的指令")
            return
        command, sub_command = message_segs[:2]
        content = message_segs[2:]
        if command == 'Welcome':
            if sub_command == 'Channel':
                self.guilds[guild_id].SetWelcomeChannel(int(content[0]))
                await channel.send(f"已設定歡迎訊息頻道到: {content[0]}")
                return
            elif sub_command == 'Text':
                self.guilds[guild_id].SetWelcomeTxt(content)
                await channel.send(f"已設定歡迎訊息: {' '.join(content)}")
                return
            else:
                await channel.send("看不懂的指令")
                return
        elif command == 'Leave':
            if sub_command == 'Channel':
                self.guilds[guild_id].SetLeaveChannel(int(content[0]))
                await channel.send(f"已設定離開訊息頻道到: {content[0]}")
                return
            elif sub_command == 'Text':
                self.guilds[guild_id].SetLeaveTxt(content)
                await channel.send(f"已設定離開訊息: {' '.join(content)}")
                return
            else:
                await channel.send("看不懂的指令")
                return
        await channel.send("看不懂的指令")
