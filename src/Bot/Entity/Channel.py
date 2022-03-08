'''
    here describes the channel data that bot needs
    除了一些會從 setting 裡初始化的資料之外，也會初始化一些資訊
'''

def _init_channel_setting(setting):
    assert 'id' in setting, '[Error] 沒有設定 channel ID 阿!!!'
    if 'name' not in setting:
        setting['name'] = ''
    if 'desc' not in setting:
        setting['desc'] = ''
    if 'last_stream_id' not in setting:
        setting['last_stream_id'] = ''

class ChannelData:
    def __init__(self, setting: dict):
        _init_channel_setting(setting)
        self.id = setting['id']
        self.name = setting['name']
        self.description = setting['desc']
        self.last_stream_id = setting['last_stream_id']     # 最後追蹤到的直播 id
        # initialize other default values
        self.live = False
    
    def GetSetting(self):
        setting = {
            "id": self.id,
            "name": self.name,
            "desc": self.description,
            "last_stram_id": self.last_stream_id
        }
        return setting
