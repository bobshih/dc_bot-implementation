'''
    here describes the channel data that bot needs
    除了一些會從 setting 裡初始化的資料之外，也會初始化一些資訊
'''

class ChannelData:
    def __init__(self, setting: dict):
        self.id = setting['id']
        self.name = setting['name']
        self.description = setting['desc']
        self.last_stream_id = setting['last_stream_id']     # 最後追蹤到的直播 id
        # initialize other default values
        self.live = False
