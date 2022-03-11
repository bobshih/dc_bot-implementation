'''
    here describes the guild data that bot needs
'''
from typing import List
from discord import Guild as dGuild
from .Stream import StreamInfo

from ...Utils.bot_utils import SaveGuildData
from ...Utils.message_utils import GetChannelRelatedMessage

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
    if 'using_thread' not in guild_setting['channel']:              # 是否使用 thread
        guild_setting['channel']['using_thread'] = False
    return guild_setting

class Guild_cls:
    @classmethod
    def Init_wGuild(cls, discord_guild: dGuild)->'Guild_cls':
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
        self.using_thread: bool = guild_setting['channel']['using_thread']
        self.described_channels: List[ChannelData] = []
        for channel_setting in guild_setting['channel']['channel_list']:
            if 'text_channel' not in channel_setting:
                channel_setting['text_channel'] = self.notify_text_channel
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

    def GetStartNotifyMSG(self, channel_id: str, live_info: StreamInfo)->str:
        ''' 取得 開始直播 通知，要根據不同 channel 取得不同的訊息 '''
        msg, cid = '', -1
        for idx, channel_data in enumerate(self.described_channels):
            if channel_data.id == channel_id:
                msg = channel_data.start_msg
                cid = idx
                break
        if msg == '':
            msg = self.start_stream_msg
        assert cid != -1, f"[Error] in GetStartNotifyMSG, unable to find the channel with the channel id, {channel_id}"
        return GetChannelRelatedMessage(msg, self.described_channels[cid], live_info)

    def GetWaitingMSG(self, channel_id: str, live_info: StreamInfo)->str:
        ''' 取得 待機 的通知訊息，要根據不同 channel 取得不同的訊息 '''
        msg, cid = '', -1
        for idx, channel_data in enumerate(self.described_channels):
            if channel_data.id == channel_id:
                msg = channel_data.start_msg
                cid = idx
                break
        if msg == '':
            msg = self.waiting_msg
        assert cid != -1, f"[Error] in GetWaitingMSG, unable to find the channel with the channel id, {channel_id}"
        return GetChannelRelatedMessage(msg, self.described_channels[cid], live_info)

    def GetEndMSG(self, channel_id: str, live_info: StreamInfo)->str:
        ''' 取得 結束直播 的通知訊息，要根據不同 channel 取得不同的訊息 '''
        msg, cid = '', -1
        for idx, channel_data in enumerate(self.described_channels):
            if channel_data.id == channel_id:
                msg = channel_data.start_msg
                cid = idx
                break
        if msg == '':
            msg = self.end_stream_msg
        assert cid != -1, f"[Error] in GetEndMSG, unable to find the channel with the channel id, {channel_id}"
        return GetChannelRelatedMessage(msg, self.described_channels[cid], live_info)

    def DeleteChannel(self, channel_id: str)->str:
        ''' 刪除某個 channel '''
        found_idx = None
        for idx, channel_data in enumerate(self.described_channels):
            if channel_data.id == channel_id:
                found_idx = idx
        if found_idx != None:
            self.described_channels.pop(found_idx)
            self.UpdateGuildFile()
            return f"[Success] 成功刪除 Channel, {channel_id}"
        return "[Error] 沒有找到對應的頻道來刪除，請確認輸入的 Channel ID 是否正確"

    def ResetChannelStatus(self, channel_id: str)->str:
        ''' 重新設定 Channel 的狀態，這個動作執行完之後應該重新檢查一次所有 channel 狀態，藉此通知大家 '''
        for channel_data in self.described_channels:
            if channel_data.id == channel_id:
                channel_data.Reset()
                return "[Success] 成功重制了頻道狀態"
        return "[Error] 沒有找到對應的頻道，請確認輸入的 Channel ID 是否正確"

    def AddDescribedChannel(self, channel_id: str)->str:
        ''' 新增一個 channel，會輸出一個字串通知使用者結果如何 '''
        for channel_data in self.described_channels:
            if channel_data.id == channel_id:
                return "[Error] 已經有相同 ID 的 yt 頻道了，請使用修改的指令修改內容"
        self.described_channels.append(ChannelData({'id': channel_id}))
        self.UpdateGuildFile()
        return "[Success] 成功加入一個新頻道，請使用此 ID 去修改相關資訊"
    
    def UpdateChannelData(self, channel_id: str, data_type: str, new_content: str)->str:
        '''
            更新 Channel 資料，過程中會檢查是否有對應的 Channel
            最後輸出一個字串，表示結果
            若有錯，也會以字串形式輸出
        '''
        for channel_data in self.described_channels:
            if channel_data.id == channel_id:
                if not hasattr(channel_data, data_type):
                    return '[Error] channel data 中並沒有此設定可以被更新'
                ori_data = getattr(channel_data, data_type)
                if type(ori_data) == int:
                    if new_content.isdigit():
                        new_content = int(new_content)
                    else:
                        return f'[Error] {data_type} 只接受數字'
                setattr(channel_data, data_type, new_content)
                self.UpdateGuildFile()
                return f"[Success] 更新了 {channel_id} 的 {data_type} 為 {getattr(channel_data, data_type)}"
        return '[Error] 這個 channel id 並不在訂閱清單中，請先用 add-new-channel 進行訂閱'

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