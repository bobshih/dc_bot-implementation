'''
    stream 相關的資訊
'''

class StreamInfo:
    def __init__(
        self,
        title,
        live_status,            # 直播狀態: upcoming, live, none
        description,
        scheduled_start_time,
        actual_end_time,
    ):
        self.title = title
        self.desc = description
        self.live_status = live_status
        self.scheduled_start_time = scheduled_start_time
        self.end_time = actual_end_time
