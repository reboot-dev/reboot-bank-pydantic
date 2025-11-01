from pydantic import BaseModel
from reboot.api import (
    API,
    Field,
    Methods,
    Reader,
    StateModel,
    Transaction,
    Type,
)


class BankState(StateModel):
    customer_ids_map_id: str = Field(tag=1)


class CreateRequest(BaseModel):
    pass


class SignUpRequest(BaseModel):
    customer_id: str = Field(tag=1)


class AllCustomerIdsRequest(BaseModel):
    pass


class AllCustomerIdsResponse(BaseModel):
    customer_ids: list[str] = Field(tag=1)


class TransferRequest(BaseModel):
    from_account_id: str = Field(tag=1)
    to_account_id: str = Field(tag=2)
    amount: float = Field(tag=3)


class OpenCustomerAccountRequest(BaseModel):
    initial_deposit: float = Field(tag=1)
    customer_id: str = Field(tag=2)


class AccountBalancesRequest(BaseModel):
    pass


class CustomerAccount(BaseModel):
    account_id: str = Field(tag=1)
    balance: float = Field(tag=2)


class CustomerAccounts(BaseModel):
    customer_id: str = Field(tag=1)
    accounts: list[CustomerAccount] = Field(tag=2)


class AccountBalancesResponse(BaseModel):
    balances: list[CustomerAccounts] = Field(tag=1)


BankMethods = Methods(
    create=Transaction(
        request=CreateRequest,
        response=None,
        factory=True,
    ),
    sign_up=Transaction(
        request=SignUpRequest,
        response=None,
    ),
    all_customer_ids=Reader(
        request=AllCustomerIdsRequest,
        response=AllCustomerIdsResponse,
    ),
    transfer=Transaction(
        request=TransferRequest,
        response=None,
    ),
    open_customer_account=Transaction(
        request=OpenCustomerAccountRequest,
        response=None,
    ),
    account_balances=Reader(
        request=AccountBalancesRequest,
        response=AccountBalancesResponse,
    ),
)

api = API(
    Bank=Type(
        state=BankState,
        methods=BankMethods,
    ),
)
