'''
    dc bot 相關的動作
'''
# from typing import Union
from pathlib import Path

import yaml

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
