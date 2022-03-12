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
        setting['text_channel'] = -1
    if 'thread_id' not in setting:
        setting['thread_id'] = ''
    if 'end_msg' not in setting:
        setting['end_msg'] = ''
    if 'start_msg' not in setting:
        setting['start_msg'] = ''
    if 'wait_msg' not in setting:
        setting['wait_msg'] = ''
    if 'target' not in setting:
        setting['target'] = -1
    if 'target_type' not in setting:
        setting['target_type'] = ''

class ChannelData:
    def __init__(self, setting: dict):
        _init_channel_setting(setting)
        self.id = setting['id']
        self.name = setting['name']
        self.last_stream_id = setting['last_stream_id']     # 最後追蹤到的直播 id
        self.text_channel = setting['text_channel']
        self.thread_id = setting['thread_id']
        self.target = setting['target']
        self.target_type = setting['target_type']
        # custom messages
        self.end_msg = setting['end_msg']
        self.start_msg = setting['start_msg']
        self.wait_msg = setting['wait_msg']
        # initialize other default values
        self.live = False
        self.stream_id = ''         # 正在 stream 的 id
    
    def GetSetting(self):
        setting = {
            "id": self.id,
            "name": self.name,
            "last_stream_id": self.last_stream_id,
            "text_channel": self.text_channel,
            "thread_id": self.thread_id,
            'end_msg': self.end_msg,
            'start_msg': self.start_msg,
            'wait_msg': self.wait_msg,
            'target': self.target,
            'target_type': self.target_type,
        }
        return setting

    def Reset(self):
        ''' Reset the channel status '''
        self.last_stream_id = ''
        self.stream_id = ''
