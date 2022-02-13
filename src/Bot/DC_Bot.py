'''
    this class used to describe the actions of a bot in this project
'''
from discord import (
    Guild as dGuild,
    Message as dMessage,
)

from .Entity import Guild, Member
from ..Utils import bot_utils

BotPrefix = '+='

class Bot:
    def __init__(self):
        guild_settings = bot_utils.LoadGuildData()
        self.guilds = {
            gid: Guild(setting) for gid, setting in guild_settings.items()
        }

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
