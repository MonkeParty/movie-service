from enum import Enum

import json



class EventType(Enum):
    Invalid = 'erro'

    MovieRated = 'movr'


_event_type_members = EventType._member_map_.values()
class EventTypeConstants:
    event_type_to_prefix = {}
    prefix_to_event_type = {}

    for enum in _event_type_members:
        event_type_to_prefix[enum] = enum.value
        prefix_to_event_type[enum.value] = enum


class Event:
    def __init__(self, type: EventType, data):
        self.type = type
        self.data = data

    def __str__(self) -> str:
        return f'{EventTypeConstants.event_type_to_prefix[self.type]} {self.data}'


class EventFromMessage(Event):
    def __init__(self, kafka_message: str):
        prefix = kafka_message[:4]
        data = kafka_message[5:]

        try:
            event_type = EventTypeConstants.prefix_to_event_type[prefix]
        except:
            event_type = EventType.Invalid

        match event_type:
            case EventType.MovieRated:
                data = json.loads(data)
            case _:
                data = f'Error: got invalid message: {kafka_message}'

        return super().__init__(event_type, data)

