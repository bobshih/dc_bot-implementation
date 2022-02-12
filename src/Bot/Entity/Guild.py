'''
    here describes the guild data that bot needs
'''
from typing import List
from discord import Guild as dGuild

from . import Member

def _init_guild_setting(ori_setting: dict)->None:
    if 'members' not in ori_setting:
        ori_setting['members'] = []
    if 'welcome_text' not in ori_setting:
        ori_setting['welcome_text'] = ''
    if 'leave_text' not in ori_setting:
        ori_setting['leave_text'] = ''

class Guild:
    @classmethod
    def Init_wGuild(cls, discord_guild: dGuild):
        new_guild_dict = {
            'members': [],
            'member_count': discord_guild.member_count
        }
        for member in discord_guild.members:
            new_member = Member.Init_wMember(member)
            new_guild_dict['members'].append(new_member.GetSetting())
        return cls(new_guild_dict)

    def __init__(self, guild_setting: dict={}):
        self.members: List[Member] = []
        for member_setting in guild_setting['members']:
            self.members.append(Member(member_setting))
        self.welcome_text = guild_setting['welcome_text']
        self.leave_text = guild_setting['leave_text']
        self.member_count = guild_setting['member_count']
