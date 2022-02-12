'''
    Here describes the member methods
'''
from discord import Member as dMember

class Member:
    @classmethod
    def Init_wMember(cls, member: dMember)->'Member':
        new_member_setting = {
            'name': member.name,
            'nicky_name': member.display_name,
            'id': member.id,
        }
        return cls(new_member_setting)

    def __init__(self, member_setting: dict={}):
        self.name: str = member_setting['name'] if 'name' in member_setting else ""
        self.nicky_name: str = member_setting['nicky_name'] if 'nicky_name' in member_setting else ""
        self.id: int = member_setting['id'] if 'id' in member_setting else None

    def GetSetting(self)->dict:
        ''' 輸出 Setting Config '''
        res_dict = {
            'name': self.name,
            'nicky_name': self.nicky_name,
            'id': self.id
        }
        return res_dict
