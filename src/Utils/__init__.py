import os

from ..Bot.Setting import BotSetting

def Load_Setting()->BotSetting:
    '''
        load the settings from environment variables
    '''
    env_vars = os.environ
    if 'dc_bot_token' not in env_vars:
        with open(".env", 'r', encoding='utf8') as fp:
            for line in fp:
                segs = line.strip().split('=')
                env_vars[segs[0]] = segs[1]
    return BotSetting(env_vars)