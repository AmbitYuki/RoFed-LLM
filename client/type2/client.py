import time
from collections import defaultdict
from typing import List, Tuple
from oprf import mask, data
import oprf

from ep_mpd.eg_psi.utils import EgPsiDataType
from ep_mpd.eg_psi.utils import encode_element, decode_element
from ep_mpd.eg_psi.type2.tp import SemiTrustedThirdPartyType2


class ClientType2:

    def __init__(self, client_id: int, data_type: EgPsiDataType):
        self.v = defaultdict(list)  # stores the intersection with clients in other group
        self.mask = mask()
        self.s = None  # plaintext elements
        self.s_dirty_bits = {}  # key is plaintext elements and value is 0/1 where 0 if element is deleted
        self.hash_s = {}  # hashed elements. key is plaintext hash and value is plaintext
        self.s_hash = {}  # key is plaintext ele and value is hash
        self.other_client_salt_ele = {}  # store encrypted elements of other clients. value is hash
        self.r = defaultdict(list)  # stores the indices of the intersection with every other client. key is client
        # id and value is indices
        self.client_id = client_id
        self.data_type = data_type
        self.group = None
        self.s_prime = []  # stores the encrypted elements
        self.ct_pt_hash = {}  # stores ciphertext and corresponding plaintext hash

    def set_group(self, client_group: int):
        self.group = client_group

    def create_set(self, data_set: List[int]):
        self.s = data_set
        for ele in self.s:
            self.s_dirty_bits[ele] = 1
            ele_bytes = encode_element(ele)
            ele_hash = data.hash(ele_bytes)
            self.hash_s[ele_hash] = ele
            self.s_hash[ele] = ele_hash

    def encrypt_elements(self, tp: SemiTrustedThirdPartyType2) -> float:
        # this function returns the TP execution time
        tp_time = 0
        # encode, hash, and encrypt elements
        for ele in self.s:
            if self.s_dirty_bits[ele]:
                ele_hash = self.s_hash[ele]
                mask_ele = self.mask(ele_hash)

                start = time.perf_counter()
                salt_mask_ele = tp.get_salted_data(mask_ele)  # get salted data from tp
                end = time.perf_counter()
                tp_time += end - start

                salt_ele = self.mask.unmask(salt_mask_ele)  # finally, unmask
                self.s_prime.append(salt_ele)
                self.ct_pt_hash[salt_ele] = ele_hash

        return tp_time

    def send_to_client(self) -> Tuple[int, List[bytes]]:
        return self.client_id, self.s_prime

    def receive_from_client(self, client_id: int, s_prime: List[bytes]):
        self.other_client_salt_ele[client_id] = s_prime

    def set_intersection(self):

        # find intersecting elements
        for other_client_id in self.other_client_salt_ele:
            other_s_prime = self.other_client_salt_ele[other_client_id]
            for other_salt_ele in other_s_prime:
                # check if other client's element is in the data set
                if other_salt_ele in self.ct_pt_hash:
                    if self.group == 0:
                        pt_hash = self.ct_pt_hash[other_salt_ele]
                        ele = self.hash_s[pt_hash]
                        self.s_dirty_bits[ele] = 0

        self.reset_client()

    def get_deduplicated_dataset(self):
        new_s = []
        for ele in self.s_dirty_bits:
            if self.s_dirty_bits[ele] == 1:
                new_s.append(ele)

        return new_s

    def reset_client(self):
        self.group = None
        self.other_client_salt_ele.clear()

    def __str__(self) -> str:
        return "Client ID: {}, Client Group: {}".format(self.id, self.group)
