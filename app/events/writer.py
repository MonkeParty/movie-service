from kafka import KafkaProducer
from .events import Event


class KafkaEventWriter:
    '''
    Класс, который превращает ивенты в сообщения и отправляет их в кафку
    '''

    def __init__(self, kafka_producer: KafkaProducer, topic: str):
        '''
        Инициализация класса
        '''
        self.topic = topic
        self.producer = kafka_producer

    def send_event(self, event: Event):
        '''
        Отправка ивента превращенного в сообщение
        '''
        message = str(event)
        self.producer.send(self.topic, message.encode('utf-8'))

    def release(self):
        '''
        Отключение от кафки
        '''
        self.producer.close()