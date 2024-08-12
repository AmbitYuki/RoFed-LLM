class PRPKey:

    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv
