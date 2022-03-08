# 載入 bot setting

class BotSetting:
    def __init__(self, setting_dict: dict):
        self.port = setting_dict['PORT']
        print(f"port: {self.port}")
        self.dc_bot_token = setting_dict['dc_bot_token']
        # 我用第三個 google 帳號來開啟此 API 的
        self.google_api_key = setting_dict['google_api_key']
