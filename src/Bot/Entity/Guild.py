'''
    here describes the guild data that bot needs
'''
from typing import List
from discord import Guild as dGuild

from src.Utils.bot_utils import SaveGuildData

from . import Member

def _init_guild_setting(guild_setting: dict={}, discord_guild: dGuild = None)->dict:
    ''' 初始化 guild setting '''
    if guild_setting == {}:
        guild_setting = {
            'info':{},
            'setting': {},
        }
    # guild related info
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
    return guild_setting

class Guild:
    @classmethod
    def Init_wGuild(cls, discord_guild: dGuild)->'Guild':
        new_setting = _init_guild_setting(discord_guild=discord_guild)
        return cls(new_setting)

    def __init__(self, guild_setting: dict={}):
        # guild info
        self.name = guild_setting['info']['name']
        self.id = guild_setting['info']['id']
        # settings
        self.welcome_text: str = guild_setting['setting']['welcome_text']
        self.welcome_channel: int = guild_setting['setting']['welcome_channel']
        self.leave_text: str = guild_setting['setting']['leave_text']
        self.leave_channel: int = guild_setting['setting']['leave_channel']
    
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

    def GetSetting(self)->dict:
        ''' 取出 setting dict '''
        result = {
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