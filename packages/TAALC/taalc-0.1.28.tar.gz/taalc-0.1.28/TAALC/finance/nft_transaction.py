from epure import epure
from .taalc_transaction import TaalcTransaction
from .taalc_nft import TaalcNft
from .taalc_nft_token import TaalcNftToken

@epure()
class NftTransaction(TaalcTransaction):
    taalc_nft: TaalcNft
    taalc_nft_token: TaalcNftToken