from typing import TYPE_CHECKING
from ..finance.taalc_nft import TaalcNft
from .t_user import TUser
from .t_chat import TChat
from .. import bidding
# if TYPE_CHECKING:
#     from ..bidding.t_offer import TOffer
from epure import epure
from aiogram import types

@epure()
class TMessage():
    owner: TUser
    creator: TUser
    # if TYPE_CHECKING:
    taalc_offer: 'bidding.t_offer.TOffer' = None
    taalc_nft: TaalcNft = None
    taalc_chat: TChat
    tg_chat_id: int
    tg_message_id: int

    def __init__(self, message: types.Message):
        
        self.creator = TUser.user_by_tg_user(message.from_user)
        self.owner = TUser.user_by_tg_user(message.from_user)
        self.tg_chat_id=message.chat.id
        self.tg_message_id=message.message_id

        taalc_chat = TChat.resource.read(tg_chat_id=self.tg_chat_id)
        if taalc_chat:
            taalc_chat = taalc_chat[0]
        else:
            taalc_chat = TChat()
            taalc_chat.tg_chat_id = message.chat.id
            taalc_chat.shifted_id = message.chat.shifted_id
        self.taalc_chat = taalc_chat

    @classmethod
    def get_t_message(cls, message: types.Message):
        res = cls.resource.read(tg_chat_id=message.chat.id, \
                                tg_message_id=message.message_id)
        if not res:
            res = cls(message)
            res.save()
        else:
            res = res[0]
        
        return res
    
    def get_url(self):
        res = f"https://t.me/c/{self.taalc_chat.shifted_id}/{self.tg_message_id}"
        return res
    

        