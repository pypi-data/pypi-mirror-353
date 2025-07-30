# from __future__ import annotations
# from typing import Optional, TYPE_CHECKING
from epure import epure
from .currency import Currency
from ..tg_environment.t_member import TMember
# if TYPE_CHECKING:
from .taalc_transaction import TaalcTransaction
from datetime import datetime

@epure()
class CurrencyTransaction(TaalcTransaction):

    currency: Currency
    amount: float


    def __init__(self, sent_from, sent_to, currency, amount):

        self.sent_from = sent_from
        self.sent_to = sent_to
        self.currency = currency
        self.amount = amount
        self.transaction_time = datetime.now()