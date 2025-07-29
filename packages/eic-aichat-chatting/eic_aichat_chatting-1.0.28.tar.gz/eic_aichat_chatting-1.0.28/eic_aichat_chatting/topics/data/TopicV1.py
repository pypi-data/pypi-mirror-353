# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, List
from pip_services4_data.data import IStringIdentifiable


class TopicV1(IStringIdentifiable):
    def __init__(self, id: str = None, owner_id: str = None, name: str = None, access_list: List[str] = None,
                 created_time: datetime = None, updated_time: datetime = None, model_id: str = None,
                 tailored_model_id: str = None, messages: List = None, total: int = None):
        self.id = id
        self.owner_id = owner_id
        self.name = name
        self.access_list = access_list
        self.created_time = created_time
        self.updated_time = updated_time
        self.model_id = model_id
        self.tailored_model_id = tailored_model_id
        self.messages = []
        self.total = 0

    def to_dict(self) -> Dict[str, any]:
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'access_list': self.access_list,
            'created_time': self.created_time.isoformat() if isinstance(self.created_time, datetime) else self.created_time,
            'updated_time': self.updated_time.isoformat() if isinstance(self.updated_time, datetime) else self.updated_time,
            'model_id': self.model_id,
            'tailored_model_id': self.tailored_model_id,
            'messages': self.messages,
            'total': self.total
        }
    