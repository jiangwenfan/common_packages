from abc import ABCMeta, abstractmethod


class SendSms(metaclass=ABCMeta):
    @abstractmethod
    def send(self, send_phone_number: str, veri_code: str):
        ...
