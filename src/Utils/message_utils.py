'''
    this file describes some message processing issues
'''
import os
from datetime import timedelta

from ..Bot.Entity import ChannelData
from ..Bot.Entity.Stream import StreamInfo

def GetChannelRelatedMessage(ori_msg: str, channel_data: ChannelData, stream_info: StreamInfo)->str:
    utc_timezone = int(os.getenv("UTC_TIMEZONE"))
    notified_target = "Unknown Target"
    if channel_data.notified_target_type == 'tag':
        notified_target = f"<@&{channel_data.notified_target}>"
    elif channel_data.notified_target_type == 'id':
        notified_target = f"<@{channel_data.notified_target}>"
    # else:
    #     raise Exception(f"[Error] notified_target_type is invaildable fomr channel {channel_data.name}")
    # stream time related info
    start_time = str(round(stream_info.scheduled_start_time.timestamp()) + (utc_timezone * 3600))
    rel_start_time = f"<t:{start_time}:R>"
    act_start_time = f"<t:{start_time}:F>"
    rel_end_time, act_end_time, elapsed_time = None, None, None
    if stream_info.end_time != None:
        end_time = str(round(stream_info.end_time.timestamp()) + (utc_timezone * 3600))
        rel_end_time = f"<t:{end_time}:R>"
        act_end_time = f"<t:{end_time}:F>"
        elapsed_time = timedelta(seconds=round(stream_info.end_time.timestamp()) - round(stream_info.scheduled_start_time.timestamp()))
    ori_msg = ori_msg.replace("\\n", "\n")
    return ori_msg.format(
        name = channel_data.name,
        notified_target = notified_target,
        rel_start_time = rel_start_time if rel_start_time != None else "rel_start_time",
        act_start_time = act_start_time if act_start_time != None else "act_start_time",
        rel_end_time = rel_end_time if rel_end_time != None else "rel_end_time",
        act_end_time = act_end_time if act_end_time != None else "act_end_time",
        elapsed_time = elapsed_time if elapsed_time != None else "elapsed_time",
        title = stream_info.title,
        link = stream_info.link,
        desc = stream_info.desc
    )
