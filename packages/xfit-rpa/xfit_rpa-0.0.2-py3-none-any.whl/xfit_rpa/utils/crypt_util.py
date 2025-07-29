import base64, binascii, string, random


class CryptUtil:
    _random_str_idx = 8
    _random_str_len = 8

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def encrypt(self, data: str):
        data = self._random_str() + data
        if isinstance(data, str):
            data = data.encode('ascii')
        return base64.b64encode(binascii.hexlify(data)).decode('ascii')

    def decrypt(self, data: str):
        if isinstance(data, str):
            data = data.encode('ascii')
        return binascii.unhexlify(base64.b64decode(data)).decode('ascii')[self._random_str_len:]

    @classmethod
    def _random_str(cls, length=_random_str_len):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
