from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from collections import defaultdict

from typing import List, Tuple
from ep_mpd.eg_psi.utils import encode_element, decode_element
from ep_mpd.eg_psi.type1.prp_key import PRPKey
from ep_mpd.eg_psi.utils import EgPsiDataType


class ClientType1:

    def __init__(self, client_id: int, data_type: EgPsiDataType):
        self.v = defaultdict(list)  # stores the intersection with clients in other group
        self.keys = None  # keys with every client in other group. list of tuples (client_id, key)
        self.s = None  # plaintext elements
        self.s_dirty_bits = {}  # key is plaintext elements and value is 0/1 where 0 if element is deleted
        self.s_bytes = {}  # plaintext ele to padded bytes
        self.id = client_id
        self.data_type = data_type
        self.group = None
        self.ciphers = {}  # cipher objects corresponding to keys of clients in other groups
        self.s_prime = []  # encrypted elements

    def set_group(self, client_group: int):
        self.group = client_group

    def set_keys(self, keys: List[Tuple[int, PRPKey]]):
        self.keys = keys
        for key in self.keys:
            cipher = Cipher(algorithms.AES(key[1].key), modes.CBC(key[1].iv))
            self.ciphers[key[0]] = cipher

    def create_set(self, data_set: List[int]):
        # self.s = data_set
        self.s = data_set
        for ele in self.s:
            self.s_dirty_bits[ele] = 1
            ele_bytes = encode_element(ele)
            padder = padding.PKCS7(128).padder()
            ele_bytes = padder.update(ele_bytes) + padder.finalize()
            self.s_bytes[ele] = ele_bytes

    def update_key(self):
        pass

    def encrypt_elements(self, other_client_ids: List[int]):

        # for key in self.keys:
        for client_id in other_client_ids:
            for idx, ele in enumerate(self.s):
                if self.s_dirty_bits[ele] == 1:
                    ele_bytes = self.s_bytes[ele]

                    # encrypt element
                    # encryptor = self.ciphers[key[0]].encryptor()
                    encryptor = self.ciphers[client_id].encryptor()
                    enc_ele = encryptor.update(ele_bytes) + encryptor.finalize()

                    self.s_prime.append((idx, enc_ele))
                    # self.ct_pt[enc_ele] = ele

    def set_intersection(self, r: List[bytes]):

        for enc_idx in r:
            ele = self.s[enc_idx]
            if self.group == 0:
                if self.s_dirty_bits[ele] == 1:
                    self.s_dirty_bits[ele] = 0

        self.reset_client()

    def get_deduplicated_dataset(self):
        new_s = []
        for ele in self.s_dirty_bits:
            if self.s_dirty_bits[ele] == 1:
                new_s.append(ele)

        return new_s

    def reset_client(self):
        """
        We recursively create groups up the binary tree, so reset everything except the updated client set
        :return:
        """
        self.group = None
        self.s_prime.clear()  # encrypted elements
        # self.ct_pt.clear()  # stores cipher text and corresponding plain text

    def __str__(self) -> str:
        return "Client ID: {}, Client Group: {}".format(self.id, self.group)
