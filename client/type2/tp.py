import oblivious.ristretto
from oblivious.ristretto import scalar
import oprf


class SemiTrustedThirdPartyType2:

    def __init__(self):
        self.secret = scalar()

    def get_salted_data(self, client_data: oprf.oprf.data) -> oprf.oprf.data:
        return self.secret * client_data

    # def reset_secret(self) -> oblivious.ristretto.scalar:
    #     self.secret = scalar()
