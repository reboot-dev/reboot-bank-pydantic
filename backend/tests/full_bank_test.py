import reboot.std.collections.v1.sorted_map
import unittest
from account_servicer import AccountServicer
from bank.v1.proto.customer_rbt import Customer
from bank.v1.pydantic.account import BalanceResponse
from bank.v1.pydantic.account_pb2 import OverdraftError
from bank.v1.pydantic.account_rbt import Account
from bank.v1.pydantic.bank_rbt import Bank
from bank_servicer import BankServicer
from customer_servicer import CustomerServicer
from google.protobuf.message import Message
from pydantic import BaseModel
from reboot.aio.applications import Application
from reboot.aio.contexts import WriterContext
from reboot.aio.tests import Reboot

BANK_ID = 'test-bank'


class AccountServicerWithNoInterest(AccountServicer):

    async def interest(
        self,
        context: WriterContext,
        request: Account.InterestRequest,
    ) -> None:
        # To avoid flakes remove the interest on the Account,
        # so the balance remains stable during tests.
        pass


class TestBank(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rbt = Reboot()
        await self.rbt.start()

    async def asyncTearDown(self) -> None:
        await self.rbt.stop()

    async def test_transfer(self) -> None:
        await self.rbt.up(
            Application(
                servicers=[
                    BankServicer,
                    AccountServicerWithNoInterest,
                    CustomerServicer,
                ] + reboot.std.collections.v1.sorted_map.servicers(),
            )
        )
        context = self.rbt.create_external_context(name=f"test-{self.id()}")
        bank, response = await Bank.create(context, BANK_ID)

        # Assert that the constructor returns 'None' as described in
        # Pydantic schema.
        assert response is None

        CUSTOMER_ID_1 = "test@reboot.dev"
        CUSTOMER_ID_2 = "test2@reboot.dev"

        sign_up_response_1 = await bank.sign_up(
            context,
            customer_id=CUSTOMER_ID_1,
        )

        # Assert that Transaction methods return 'None' as described in
        # Pydantic schema.
        assert sign_up_response_1 is None

        open_account_response_1 = await Customer.ref(
            CUSTOMER_ID_1
        ).open_account(context, initial_deposit=1000.0)

        # The 'Customer' servicer was described in Protobuf, so assert
        # that the response is a Protobuf message.
        assert isinstance(open_account_response_1, Message)

        sign_up_response_2 = await bank.sign_up(
            context,
            customer_id=CUSTOMER_ID_2,
        )

        # Assert that Transaction methods return 'None' as described in
        # Pydantic schema.
        assert sign_up_response_2 is None

        all_customer_ids_response = await bank.all_customer_ids(context)

        assert isinstance(all_customer_ids_response, BaseModel)

        open_account_response_2 = await Customer.ref(
            CUSTOMER_ID_2
        ).open_account(context, initial_deposit=0.0)

        # The 'Customer' servicer was described in Protobuf, so assert
        # that the response is a Protobuf message.
        assert isinstance(open_account_response_2, Message)

        transfer_response = await bank.transfer(
            context,
            from_account_id=open_account_response_1.account_id,
            to_account_id=open_account_response_2.account_id,
            amount=250.0,
        )

        # Assert that Transaction methods return 'None' as described in
        # Pydantic schema.
        assert transfer_response is None

        account_balances = await bank.account_balances(context)

        # Assert that the response is a Pydantic model as described in
        # the Pydantic schema.
        assert isinstance(account_balances, BaseModel)

        for account_balance in account_balances.balances:
            if account_balance.customer_id == CUSTOMER_ID_1:
                self.assertEqual(len(account_balance.accounts), 1)
                self.assertEqual(account_balance.accounts[0].balance, 750.0)
            elif account_balance.customer_id == CUSTOMER_ID_2:
                self.assertEqual(len(account_balance.accounts), 1)
                self.assertEqual(account_balance.accounts[0].balance, 250.0)
            else:
                self.fail(
                    f"Unexpected customer ID: {account_balance.customer_id}"
                )

        # Also test balances from the Account servicer.
        account_1 = Account.ref(open_account_response_1.account_id)
        account_2 = Account.ref(open_account_response_2.account_id)

        balance_response_1 = await account_1.balance(context)
        assert isinstance(balance_response_1, BaseModel)
        self.assertEqual(balance_response_1.amount, 750.0)

        balance_response_2 = await account_2.balance(context)
        assert isinstance(balance_response_2, BaseModel)
        self.assertEqual(balance_response_2.amount, 250.0)

    async def test_overdraft(self) -> None:
        await self.rbt.up(
            Application(
                servicers=[
                    BankServicer,
                    AccountServicerWithNoInterest,
                    CustomerServicer,
                ] + reboot.std.collections.v1.sorted_map.servicers(),
            )
        )
        context = self.rbt.create_external_context(name=f"test-{self.id()}")
        bank, _ = await Bank.create(context, BANK_ID)

        ACCOUNT_ID = "test-overdraft-account"
        account, _ = await Account.open(context, ACCOUNT_ID)
        try:
            await account.withdraw(context, amount=50.50)
            raise Exception("Expected OverdraftError to be thrown")
        except Account.WithdrawAborted as aborted:
            # For now it is Protobuf, until we have a clear Pydantic
            # story for errors.
            assert isinstance(aborted.error, OverdraftError)
            self.assertEqual(aborted.error.amount, 50.50)

    async def test_tasks(self) -> None:
        await self.rbt.up(
            Application(
                servicers=[
                    BankServicer,
                    AccountServicerWithNoInterest,
                    CustomerServicer,
                ] + reboot.std.collections.v1.sorted_map.servicers(),
            )
        )
        context = self.rbt.create_external_context(name=f"test-{self.id()}")
        bank, _ = await Bank.create(context, BANK_ID)

        ACCOUNT_ID = "test-overdraft-account"
        account, _ = await Account.open(context, ACCOUNT_ID)
        task = await account.spawn().deposit(context, amount=10.0)

        response = await task

        assert response is None

        balance_task = await account.spawn().balance(context)
        balance_response = await balance_task

        assert isinstance(balance_response, BalanceResponse)

        self.assertEqual(balance_response.amount, 10.0)
