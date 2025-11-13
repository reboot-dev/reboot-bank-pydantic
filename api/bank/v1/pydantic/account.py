from pydantic import BaseModel
from reboot.api import API, Field, Methods, Reader, StateModel, Type, Writer


class AccountState(StateModel):
    balance: float = Field(tag=1)


class BalanceResponse(BaseModel):
    amount: float = Field(tag=1)


class DepositRequest(BaseModel):
    amount: float = Field(tag=1)


class WithdrawRequest(BaseModel):
    amount: float = Field(tag=1)


AccountMethods = Methods(
    balance=Reader(
        request=None,
        response=BalanceResponse,
    ),
    deposit=Writer(
        request=DepositRequest,
        response=None,
    ),
    withdraw=Writer(
        request=WithdrawRequest,
        response=None,
    ),
    open=Writer(
        request=None,
        response=None,
        factory=True,
    ),
    interest=Writer(
        request=None,
        response=None,
    ),
)

api = API(
    Account=Type(
        state=AccountState,
        methods=AccountMethods,
    ),
)
