'''
    這裡處理所有 OnReady 時要載入的動作
'''
from typing import Dict
from discord import Guild, Member

def GetGuildData(guild: Guild)->Dict:
    ''' 取得 guild 相關的資料，並且輸出成字典 '''
    guild_data = {}
    guild_data['member_count'] = guild.member_count
    guild_data['name'] = guild.name
    guild_data['members'] = {}
    for member in guild.members:
        member: Member
        guild_data['members'][member.id] = {
            "nickname": member.display_name,
            "name": member.name,
        }
    return guild_data