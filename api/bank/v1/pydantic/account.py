from pydantic import BaseModel
from reboot.api import API, Field, Methods, Reader, StateModel, Type, Writer


class AccountState(StateModel):
    balance: float = Field(tag=1)


class BalanceRequest(BaseModel):
    pass


class BalanceResponse(BaseModel):
    amount: float = Field(tag=1)


class DepositRequest(BaseModel):
    amount: float = Field(tag=1)


class WithdrawRequest(BaseModel):
    amount: float = Field(tag=1)


class OverdraftError(BaseModel):
    amount: float = Field(tag=1)


class OpenRequest(BaseModel):
    pass


class InterestRequest(BaseModel):
    pass


AccountMethods = Methods(
    balance=Reader(
        request=BalanceRequest,
        response=BalanceResponse,
    ),
    deposit=Writer(
        request=DepositRequest,
        response=None,
    ),
    withdraw=Writer(
        request=WithdrawRequest,
        response=None,
        errors=[OverdraftError],
    ),
    open=Writer(
        request=OpenRequest,
        response=None,
        factory=True,
    ),
    interest=Writer(
        request=InterestRequest,
        response=None,
    ),
)

api = API(
    Account=Type(
        state=AccountState,
        methods=AccountMethods,
    ),
)
