from collections import defaultdict
from typing import List, Tuple


class SemiTrustedThirdPartyType1:

    def __init__(self):
        self.client_s_primes = defaultdict(list)  # stores encrypted elements of all clients. key is group
        self.superset_s_primes = defaultdict(int)  # set of all clients encrypted elements list. key is encrypted
        # element and value is number of times it occurs

    def receive_from_client(self, client_group: int, client_id: int, client_data: List[Tuple[int, bytes]]):
        # self.client_s_primes[(client_group, client_id)] = client_data
        for _, ele in client_data:
            self.superset_s_primes[ele] += 1

        # clear group 1 immediately
        # if client_group == 1:
        #     self.client_s_primes[(client_group, client_id)].clear()

    # Lazy eval when client requests its vector
    def send_to_client(self, client_group: int, client_id: int, client_data: List[Tuple[int, bytes]]) -> List[bytes]:
        r_idx = []

        # for idx, ele in self.client_s_primes[(client_group, client_id)]:
        #     if self.superset_s_primes[ele] > 1:
        #         r_idx.append(idx)

        for idx, ele in client_data:
            if self.superset_s_primes[ele] > 1:
                r_idx.append(idx)

        # self.client_s_primes[(client_group, client_id)].clear()

        return r_idx

    # Reset the for next EG PSI computation
    def clear_all(self):
        self.client_s_primes.clear()
        self.superset_s_primes.clear()
