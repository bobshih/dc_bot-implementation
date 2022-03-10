'''
    here describes the guild data that bot needs
'''
from typing import List
from discord import Guild as dGuild
from src.Bot.Entity.Stream import StreamInfo

from src.Utils.bot_utils import SaveGuildData

from . import ChannelData

def _init_guild_setting(guild_setting: dict={}, discord_guild: dGuild = None)->dict:
    ''' 初始化 guild setting '''
    if guild_setting == {}:
        guild_setting = {
            'info':{},
            'setting': {},
        }
    # guild related info
    if discord_guild != None:
        guild_setting['info']['name'] = discord_guild.name
        guild_setting['info']['id'] = discord_guild.id
    # guild setting
    if 'welcome_channel' not in guild_setting:
        guild_setting['setting']['welcome_channel'] = -1
    if 'welcome_text' not in guild_setting:
        guild_setting['setting']['welcome_text'] = "default welcome message: {user}"
    if 'leave_channel' not in guild_setting:
        guild_setting['setting']['leave_channel'] = -1
    if 'leave_text' not in guild_setting:
        guild_setting['setting']['leave_text'] = "default leave message: {user}"
    # channel-related properties
    if 'channel' not in guild_setting:
        guild_setting['channel'] = {}
    if 'channel_list' not in guild_setting['channel']:
        guild_setting['channel']['channel_list'] = []
    if 'notify_text_channel' not in guild_setting['channel']:      # 通知直播的文字頻道
        guild_setting['channel']['notify_text_channel'] = -1
    if 'waiting_msg' not in guild_setting['channel']:              # 待機通知
        guild_setting['channel']['waiting_msg'] = ''
    if 'start_stream_msg' not in guild_setting['channel']:         # 開始直播通知
        guild_setting['channel']['start_stream_msg'] = ''
    if 'end_stream_msg' not in guild_setting['channel']:           # 結束直播通知
        guild_setting['channel']['end_stream_msg'] = ''
    return guild_setting

class Guild_cls:
    @classmethod
    def Init_wGuild(cls, discord_guild: dGuild)->'Guild':
        new_setting = _init_guild_setting(discord_guild=discord_guild)
        return cls(new_setting)

    def __init__(self, guild_setting: dict={}):
        guild_setting = _init_guild_setting(guild_setting=guild_setting)
        # guild info
        self.name = guild_setting['info']['name']
        self.id = guild_setting['info']['id']
        # message settings
        self.welcome_text: str = guild_setting['setting']['welcome_text']
        self.welcome_channel: int = guild_setting['setting']['welcome_channel']
        self.leave_text: str = guild_setting['setting']['leave_text']
        self.leave_channel: int = guild_setting['setting']['leave_channel']
        self.notify_text_channel: int = guild_setting['channel']['notify_text_channel']
        self.waiting_msg: str = guild_setting['channel']['waiting_msg']
        self.start_stream_msg: str = guild_setting['channel']['start_stream_msg']
        self.end_stream_msg: str = guild_setting['channel']['end_stream_msg']
        # described channels
        self.described_channels: List[ChannelData] = []
        for channel_setting in guild_setting['channel']['channel_list']:
            if 'text_channel' not in channel_setting:
                # channel_setting['text_channel'] = self.notify_text_channel
                channel_setting['text_channel'] = ''
            self.described_channels.append(ChannelData(channel_setting))
    
    def UpdateGuildFile(self)->None:
        ''' 更新 Guild File '''
        setting = self.GetSetting()
        SaveGuildData(self.id, setting)

    def SetWelcomeChannel(self, channel_id: int)->None:
        self.welcome_channel = channel_id
        self.UpdateGuildFile()

    def SetWelcomeTxt(self, welcome_txt: List[str])->None:
        self.welcome_text = ' '.join(welcome_txt)
        self.UpdateGuildFile()

    def SetLeaveChannel(self, channel_id: int)->None:
        self.leave_channel = channel_id
        self.UpdateGuildFile()

    def SetLeaveTxt(self, leave_txt: List[str])->None:
        self.leave_text = ' '.join(leave_txt)
        self.UpdateGuildFile()

    def GetStartNotifyMSG(self, live_info: StreamInfo)->str:
        ''' 取得 開始直播 通知 '''
        return self.start_stream_msg.format(
            title=live_info.title,
            link=live_info.link
        )

    def GetWaitingMSG(self, live_info: StreamInfo)->str:
        ''' 取得 待機 的通知訊息 '''
        return self.waiting_msg.format(
            title=live_info.title,
            link=live_info.link
        )
    
    def GetEndMSG(self, live_info: StreamInfo)->str:
        ''' 取得 結束直播 的通知訊息 '''
        return self.end_stream_msg.format(
            title=live_info.title,
            link=live_info.link
        )

    def GetSetting(self)->dict:
        ''' 取出 setting dict '''
        result = {
            'channel': {
                'channel_list': [ele.GetSetting() for ele in self.described_channels],
                'notify_text_channel': self.notify_text_channel,
                'waiting_msg': self.waiting_msg,
                "start_stream_msg": self.start_stream_msg,
                "end_stream_msg": self.end_stream_msg,
            },
            'setting':{
                'welcome_text': self.welcome_text,
                'welcome_channel': self.welcome_channel,
                'leave_text': self.leave_text,
                'leave_channel': self.leave_channel,
            },
            'info': {
                'name': self.name,
                'id': self.id
            }
        }
        return result