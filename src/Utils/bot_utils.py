'''
    dc bot 相關的動作
'''
# from typing import Union
from pathlib import Path
from datetime import datetime
import yaml

from ..Bot.Entity import StreamInfo

data_folder = Path('data')
data_folder.mkdir(exist_ok=True)
guild_folder = data_folder/"Guilds"
guild_folder.mkdir(exist_ok=True)

def LoadGuildData(guild_id: str=None)->dict:
    ''' 從 data 資料夾取得 guild 的資料，如果沒有提供 ID，就全部載入 '''
    if guild_id != None:
        target_file = guild_folder/f"{guild_id}.yaml"
        with target_file.open("r", encoding='utf8') as fp:
            return yaml.safe_load(fp)
    total_guilds = {}
    for file in guild_folder.glob("*.yaml"):
        guild_id = file.stem
        with file.open("r", encoding='utf8') as fp:
            guild_data = yaml.safe_load(fp)
        total_guilds[int(guild_id)] = guild_data
    return total_guilds

def SaveGuildData(guild_id: int, guild_data: dict):
    ''' 把 guild data 儲存到對應的檔案中 '''
    guild_data_file = guild_folder/f"{guild_id}.yaml"
    with guild_data_file.open('w', encoding='utf8') as fp:
        yaml.dump(guild_data, fp, allow_unicode=True)

# def LoadChannelData(guild_id: str=None)->dict:
#     ''' 從 data 資料夾取得 channel 的資料 '''
#     if guild_id != None:
#         target_file = guild_folder/f"{guild_id}.yaml"
#         with target_file.open("r", encoding='utf8') as fp:
#             return yaml.safe_load(fp)
#     total_guilds = {}
#     for file in guild_folder.glob("*.yaml"):
#         guild_id = file.stem
#         with file.open("r", encoding='utf8') as fp:
#             guild_data = yaml.safe_load(fp)
#         total_guilds[int(guild_id)] = guild_data
#     return total_guilds

def SaveGuildData(guild_id: int, guild_data: dict):
    ''' 把 guild data 儲存到對應的檔案中 '''
    guild_data_file = guild_folder/f"{guild_id}.yaml"
    with guild_data_file.open('w', encoding='utf8') as fp:
        yaml.dump(guild_data, fp, allow_unicode=True)

def GetLiveStreamInfo(stream_data: dict)->StreamInfo:
    ''' stream data 來自於 google yt api v3 '''
    video_title = stream_data['items'][0]['snippet'].get('title')
    # 提供此影片是否正在直播或是 upcoming 的資訊
    live_broadcast_content = stream_data['snippet'].get("liveBroadcastContent")
    description = stream_data['snippet'].get("description")
    scheduled_start_time = datetime.strptime(stream_data['liveStreamingDetails'].get("scheduledStartTime"), "%Y-%m-%dT%H:%M:%SZ")
    actual_end_time = stream_data['items'][0]['liveStreamingDetails'].get("actualEndTime")
    return StreamInfo(
        title=video_title,
        live_status=live_broadcast_content,
        description=description,
        scheduled_start_time=scheduled_start_time,
        actual_end_time=actual_end_time,
    )