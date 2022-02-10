import os

from ..Bot.Setting import BotSetting

def Load_Setting()->BotSetting:
    '''
        load the settings from environment variables
    '''
    env_vars = os.environ
    return BotSetting(env_vars)