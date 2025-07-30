from .taalc_nft import TaalcNft
from epure import epure

@epure()
class TaalcNftToken:
    nft_state: str
    taalc_nft: TaalcNft