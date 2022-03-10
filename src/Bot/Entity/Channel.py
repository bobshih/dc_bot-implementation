'''
    here describes the channel data that bot needs
    除了一些會從 setting 裡初始化的資料之外，也會初始化一些資訊
'''

def _init_channel_setting(setting):
    assert 'id' in setting, '[Error] 沒有設定 channel ID 阿!!!'
    if 'name' not in setting:
        setting['name'] = ''
    if 'last_stream_id' not in setting:
        setting['last_stream_id'] = ''
    if 'text_channel' not in setting:
        setting['text_channel'] = ''
    if 'thread_id' not in setting:
        setting['thread_id'] = ''

class ChannelData:
    def __init__(self, setting: dict):
        _init_channel_setting(setting)
        self.id = setting['id']
        self.name = setting['name']
        self.last_stream_id = setting['last_stream_id']     # 最後追蹤到的直播 id
        self.text_channel = setting['text_channel']
        self.thread_id = setting['thread_id']
        # initialize other default values
        self.live = False
        self.stream_id = ''         # 正在 stream 的 id
    
    def GetSetting(self):
        setting = {
            "id": self.id,
            "name": self.name,
            "last_stram_id": self.last_stream_id,
            "text_channel": self.text_channel,
            "thread_id": self.thread_id,
        }
        return setting
