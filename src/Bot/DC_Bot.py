'''
    this class used to describe the actions of a bot in this project
'''
from collections import defaultdict
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
from urllib import request

from discord import (
    Guild as dGuild,
    Message as dMessage,
    Client,
    TextChannel as dTextChannel,
    File as dFile
)
from bs4 import BeautifulSoup
import yaml

from .Entity import Guild_cls, Member
from ..Utils import bot_utils

BotPrefix = '+='

class Bot:
    def __init__(self, client_obj: Client, google_api_key: str):
        guild_settings = bot_utils.LoadGuildData()
        self.google_api_key = google_api_key
        self.guilds = {
            gid: Guild_cls(setting) for gid, setting in guild_settings.items()
        }
        self.client = client_obj

    def InitGuildData(self, guild: dGuild)->None:
        ''' 載入 guild 資料並更新 '''
        guild_id = guild.id
        if guild_id not in self.guilds:
            self.guilds[guild_id] = Guild_cls.Init_wGuild(guild)
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
    
    def CheckLiveStreaming(self)->None:
        '''
            檢查有沒有 live 要開始或正在直播，如果已經在直播了，就不管
            此函式會影響後續檢查 live status 的 task
            要把 Live 資訊放到 channel.stream_id
        '''
        for guild_id, guild in self.guilds.items():
            if guild.notify_text_channel == -1: continue
            for channel_data in guild.described_channels:
                if channel_data.live:       # 已經在 live 了，不用檢查了
                    continue
                if channel_data.stream_id:  # 已經知道下一部 live stream id 了，不用再檢查
                    continue
                page = requests.get(f"https://youtube.com/channel/{channel_data.id}/live")
                page_soup = BeautifulSoup(page.text, 'html.parser')
                # 取得轉址後的 html url
                try:
                    link = page_soup.find('link', {'rel': 'canonical'})
                    href_html = link.get('href')
                    if 'watch?v=' in href_html:
                        live_streaming_id = href_html.split('watch?v=')[1]
                        channel_data.stream_id = live_streaming_id         # 在此更新 stream id
                except:
                    pass
        #             result[guild_id].append((channel_data.id, live_streaming_id))
        # return dict(result)

    def CheckStreamStatus(self)->Dict[str, List[Tuple[str, str]]]:
        '''
            檢查 stream_id 的直播狀態，根據狀態決定輸出的是 waiting msg 還是 live stream
            必須前一步 CheckLiveStreaming 有處理到
        '''
        result = defaultdict(list)
        for guild_id, guild in self.guilds.items():
            if guild.notify_text_channel == -1: continue
            for channel_data in guild.described_channels:
                if channel_data.stream_id == '':                # 沒有 stream id 表示沒有待機室或是直播
                    channel_data.live = False                   # 確保 Live flag 是正確的
                    continue
                notified_channel = channel_data.text_channel if channel_data.text_channel != -1 else guild.notify_text_channel
                yt_api_url = "https://www.googleapis.com/youtube/v3/videos?id={}&part=snippet,liveStreamingDetails&key={}".format(
                    channel_data.stream_id, self.google_api_key
                )
                res = requests.get(yt_api_url)
                try:
                    stream_data = res.json()['items'][0]
                except Exception as e:
                    print(e)
                    continue
                live_info = bot_utils.GetLiveStreamInfo(stream_data, channel_data.stream_id)
                if live_info.live_status == 'upcoming':
                    print(f"in upcoming, stream id: {channel_data.stream_id}, last_stream_id: {channel_data.last_stream_id}, live status: {channel_data.live}")
                    # if channel_data.stream_id == channel_data.last_stream_id:
                    #     continue
                    # 檢查是否超過 1 天，如果超過 1 天就不通知
                    if (live_info.scheduled_start_time - datetime.now()).days >= 1:
                        channel_data.stream_id = ''             # 重設 stream id，因為這個超過一天，一分鐘後再抓一次 Live stream id
                        continue
                    if channel_data.last_stream_id != channel_data.stream_id:
                        # 未來的下一部直播會是下一個 last_stream_id，如果不同，表示有新的待機室產生，這時候就印出一次訊息
                        message = self.guilds[guild_id].GetWaitingMSG(channel_data.id, live_info)
                        channel_data.last_stream_id = channel_data.stream_id
                        channel_data.live = False
                    else:
                        message = ''
                    if guild.using_thread:
                        result[guild_id].append((notified_channel, channel_data.thread_id, message))
                    else:
                        result[guild_id].append((notified_channel, None, message))
                elif live_info.live_status == 'live' and not channel_data.live:
                    print(f"in live start, stream id: {channel_data.stream_id}, last_stream_id: {channel_data.last_stream_id}, live status: {channel_data.live}")
                    # 切換成 live 模式，送出 live string
                    channel_data.live = True
                    channel_data.last_stream_id = channel_data.stream_id
                    message = self.guilds[guild_id].GetStartNotifyMSG(channel_data.id, live_info)
                    if guild.using_thread:
                        result[guild_id].append((notified_channel, channel_data.thread_id, message))
                    else:
                        result[guild_id].append((notified_channel, None, message))
                elif live_info.end_time != None:        # 已經有結束時間，表示直播結束了
                    print(f"in ending, stream id: {channel_data.stream_id}, last_stream_id: {channel_data.last_stream_id}, live status: {channel_data.live}")
                    # 更新 channel data 去激活 CheckLiveStreaming 的工作
                    channel_data.last_stream_id = channel_data.stream_id
                    channel_data.stream_id = ''
                    channel_data.live = False
                    # 取得 end msg
                    message = self.guilds[guild_id].GetEndMSG(channel_data.id, live_info)
                    if guild.using_thread:
                        result[guild_id].append((notified_channel, channel_data.thread_id, message))
                    else:
                        result[guild_id].append((notified_channel, None, message))
                elif live_info.live_status != 'upcoming' and live_info.live_status != 'live':
                    channel_data.stream_id = ''
                    # 顯然哪裡有問題了
                    message = "我不知道為什麼會沒有第一時間抓到結束\n" + self.guilds[guild_id].GetEndMSG(channel_data.id, live_info)
                    channel_data.last_stream_id = channel_data.stream_id
                    channel_data.stream_id = ''
                    channel_data.live = False
                    if guild.using_thread:
                        result[guild_id].append((notified_channel, channel_data.thread_id, message))
                    else:
                        result[guild_id].append((notified_channel, None, message))
        return dict(result)

    async def DoTasks(self)->None:
        ''' 機器人做事，會傳訊息出去 '''
        # 1. Check the streams which is starting
        self.CheckLiveStreaming()
        # 2. check waiting room
        guild_messages = self.CheckStreamStatus()
        # 3. send messages to each guild
        for _, messages in guild_messages.items():
            # channel_id = self.guilds[guild_id].notify_text_channel
            for channel_id, thread_id, msg in messages:
                if msg == '':           # 空字串不傳送
                    continue
                if channel_id == -1:    # 沒有設定文字 channel id
                    continue
                notify_channel: dTextChannel = await self.client.fetch_channel(channel_id)
                await notify_channel.send(msg)
                # 以後再處理 thread 問題，discord 版本需要到 2.0

    async def ProcessMessage(self, message: dMessage)->None:
        ''' process the message '''
        guild_id = message.guild.id
        channel = message.channel
        message_segs = message.content[len(BotPrefix):].strip().split()
        print(message_segs)
        # if len(message_segs) < 2:
        #     await channel.send("看不懂的指令")
        #     return
        command, sub_commands = message_segs[0], message_segs[1:]
        response = ''
        if command == 'Welcome':
            # handle the content and its subcommand
            content = sub_commands[1:]
            if len(sub_commands) == 2:
                content = [sub_commands[1]]
            sub_commands = sub_commands[0]
            if sub_commands == 'Channel':
                self.guilds[guild_id].SetWelcomeChannel(int(content))
                await channel.send(f"已設定歡迎訊息頻道到: {content}")
                return
            elif sub_commands == 'Text':
                self.guilds[guild_id].SetWelcomeTxt(content)
                await channel.send(f"已設定歡迎訊息: {' '.join(content)}")
                return
            else:
                await channel.send("看不懂的指令")
                return
        elif command == 'Leave':
            # handle the content and its subcommand
            content = sub_commands[1:]
            if len(sub_commands) == 2:
                content = [sub_commands[1]]
            sub_commands = sub_commands[0]
            if sub_commands == 'Channel':
                self.guilds[guild_id].SetLeaveChannel(int(content))
                await channel.send(f"已設定離開訊息頻道到: {content}")
                return
            elif sub_commands == 'Text':
                self.guilds[guild_id].SetLeaveTxt(content)
                await channel.send(f"已設定離開訊息: {' '.join(content)}")
                return
            else:
                await channel.send("看不懂的指令")
                return
        elif command == "yt-notify":
            if len(sub_commands) == 1:
                if sub_commands[0] == 'list':
                    channel_setting = self.guilds[guild_id].GetSetting()['channel']
                    for key, value in channel_setting.items():
                        if key != 'channel_list':
                            await channel.send(f"{key}: {value}")
                        else:
                            for cSetting in value:
                                await channel.send(json.dumps(cSetting, indent='    ', ensure_ascii=False))
                            await channel.send("-"*20)
                    response = "==" * 20
            if len(sub_commands) == 2:
                if sub_commands[0] == 'add-new-channel':
                    response = self.guilds[guild_id].AddDescribedChannel(sub_commands[1])
                elif sub_commands[0] == 'update-general-notify-channel':
                    self.guilds[guild_id].notify_text_channel = sub_commands[1]
                    response = '[Success] yt 提醒通知的文字頻道已更新'
                elif sub_commands[0] == 'update-general-end-msg':
                    self.guilds[guild_id].end_stream_msg = sub_commands[1]
                    response = '[Success] yt 提醒通知的一般結束訊息已更新'
                elif sub_commands[0] == 'update-general-start-msg':
                    self.guilds[guild_id].start_stream_msg = sub_commands[1]
                    response = '[Success] yt 提醒通知的一般開始訊息已更新'
                elif sub_commands[0] == 'update-general-wait-msg':
                    self.guilds[guild_id].waiting_msg = sub_commands[1]
                    response = '[Success] yt 提醒通知的一般等待訊息已更新'
                elif sub_commands[0] == 'delete-channel':
                    response = self.guilds[guild_id].DeleteChannel(sub_commands[1])
                elif sub_commands[0] == 'reset-status':
                    response = self.guilds[guild_id].ResetChannelStatus(sub_commands[1])
                    if 'success' in response.lower():
                        await channel.send(response)
                        await self.DoTasks()
                        return
                elif sub_commands[0] == 'get-status':
                    status = self.guilds[guild_id].GetChannelStatus(sub_commands[1]
                    )
                    if status is not None:
                        await channel.send(json.dumps(status, indent='    ', ensure_ascii=False))
                        return
                    response = "[Error] 沒有找到對應的頻道，請確認輸入的 Channel ID 是否正確"
                else:
                    await channel.send("看不懂的指令")
            if len(sub_commands) >= 3:
                if sub_commands[0] == 'update-general-end-msg':
                    self.guilds[guild_id].end_stream_msg = ' '.join(sub_commands[1:])
                    response = '[Success] yt 提醒通知的一般結束訊息已更新'
                elif sub_commands[0] == 'update-general-start-msg':
                    self.guilds[guild_id].start_stream_msg = ' '.join(sub_commands[1:])
                    response = '[Success] yt 提醒通知的一般結束訊息已更新'
                elif sub_commands[0] == 'update-general-wait-msg':
                    self.guilds[guild_id].waiting_msg = ' '.join(sub_commands[1:])
                    response = '[Success] yt 提醒通知的一般結束訊息已更新'
                else:
                    data_name, channel_id = sub_commands[0], sub_commands[1]
                    new_content = ' '.join(sub_commands[2:])
                    response = self.guilds[guild_id].UpdateChannelData(channel_id, data_name, new_content)
        elif command == 'expand-guild-by-file':
            # 取得第一個檔案進行擴充
            attachment_data = await message.attachments[0].read()
            attachment_data = attachment_data.decode('utf-8')
            guild_data = yaml.safe_load(attachment_data)
            # 擴充 guild data
            if 'info' in guild_data and 'id' in guild_data['info']:
                guild_id = guild_data['info']['id']
                response = self.guilds[guild_id].UpdateBySetting(guild_data)
            else:
                response = '[Error] 更新公會資訊的過程沒有正確 ID，請確認 setting 中有 [info][id] 的資訊'
        elif command == 'get-guild-setting-file':
            # 取得 guild setting file
            self.guilds[guild_id].UpdateGuildFile()
            await channel.send(file=dFile(bot_utils.GetGuildDataFilePath(guild_id)))
            return
        self.guilds[guild_id].UpdateGuildFile()
        if response != '':
            if len(response) > 1500:
                await channel.send("[Warning] response 長度過長，請用 get-guild-setting-file 確認結果")
                return
            await channel.send(response)
            return
        await channel.send("看不懂的指令")
