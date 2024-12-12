from base64 import b64decode
from hashlib import sha256

import algokit_utils
import pytest
from algokit_utils import (
    Account,
    TransactionParameters,
    TransferParameters,
    get_account,
    transfer,
)
from algokit_utils.config import config
from algosdk import abi, transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    TransactionWithSigner,
)
from algosdk.encoding import decode_address
from algosdk.error import AlgodHTTPError
from algosdk.transaction import PaymentTxn
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.artifacts.game.game_client import GameClient

from create_ASA import create_asa


@pytest.fixture(scope="session")
def account(algod_client: AlgodClient) -> Account:
    account = get_account(algod_client, "ACCOUNT", fund_with_algos=100_000_000)
    print(account.address)
    return account


@pytest.fixture(scope="session")
def app_client(
    account: Account, algod_client: AlgodClient, indexer_client: IndexerClient
) -> GameClient:
    config.configure(
        debug=True,
        # trace_all=True,
    )
    print(account)
    client = GameClient(
        algod_client,
        creator=account,
        indexer_client=indexer_client,
    )

    client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    transfer(
        algod_client,
        TransferParameters(
            from_account=account,
            to_address=client.app_address,
            micro_algos=100_000_000,
        ),
    )

    return client


def test_register(
    algod_client: AlgodClient, app_client: GameClient, account: Account
) -> None:
    """Tests the `register` method."""
    box_abi = abi.ABIType.from_string("(uint64,string,uint64)")
    box_name = b"user" + decode_address(account.address)

    # Test application call return value
    user = app_client.register(
        name="Alice",
        transaction_parameters=TransactionParameters(boxes=[(0, box_name)]),
    ).return_value

    assert isinstance(user.registered_at, int) and user.registered_at > 0
    assert user.name == "Alice"
    assert isinstance(user.balance, int) and user.balance == 0

    # Test box value fetched from Algod
    box_value = b64decode(
        algod_client.application_box_by_name(app_client.app_id, box_name)["value"]
    )
    registered_at, name, balance = box_abi.decode(box_value)

    assert isinstance(registered_at, int) and registered_at == user.registered_at
    assert name == "Alice"
    assert isinstance(balance, int) and balance == 0


def test_fund_account(algod_client: AlgodClient, app_client: GameClient) -> None:
    """Tests the `fund_account` method."""
    # Generate new account
    account = get_account(app_client.algod_client, "test")
    app_client.signer = AccountTransactionSigner(account.private_key)

    box_abi = abi.ABIType.from_string("(uint64,string,uint64)")
    box_name = b"user" + decode_address(account.address)

    # Register a new user
    user = app_client.register(
        name="Bob",
        transaction_parameters=TransactionParameters(boxes=[(0, box_name)]),
    ).return_value

    # Store balance before funding
    balance_before = user.balance

    # Construct payment transaction
    ptxn = PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=app_client.app_address,
        amt=10_000,
    )

    # Fund the user's account
    balance_returned = app_client.fund_account(
        payment=TransactionWithSigner(
            ptxn, AccountTransactionSigner(account.private_key)
        ),
        transaction_parameters=TransactionParameters(boxes=[(0, box_name)]),
    ).return_value

    # Test the value returned from the app call
    assert balance_before + 10_000 == balance_returned

    # Parse user's box from Algod
    box_value = b64decode(
        algod_client.application_box_by_name(app_client.app_id, box_name)["value"]
    )
    _, _, box_balance = box_abi.decode(box_value)

    # Test box value balance
    assert balance_before + 10_000 == box_balance


def test_admin_upsert_asset(
    algod_client: AlgodClient, app_client: GameClient, account: Account
) -> None:
    """Tests the `admin_upsert_asset` method."""
    # Switch back to creator account
    app_client.signer = AccountTransactionSigner(account.private_key)

    for asset in (
        ("POKEBALL", "Catches Pokemon", 200),
        ("POTION", "Restores 20 HP", 300),
        ("BICYCLE", "Allows you to travel faster", 1_000_000),
    ):
        name, _, _ = asset
        box_name = b"asset" + sha256(abi.StringType().encode(name)).digest()

        # Call app client
        app_client.admin_upsert_asset(
            asset=asset,
            transaction_parameters=TransactionParameters(boxes=[(0, box_name)]),
        )

        # Test box value fetched from Algod
        box_value = b64decode(
            algod_client.application_box_by_name(app_client.app_id, box_name)["value"]
        )
        box_abi = abi.ABIType.from_string("(string,string,uint64)")

        # Test box value balance
        assert asset == tuple(box_abi.decode(box_value))


def test_buy_asset(
    algod_client: AlgodClient, app_client: GameClient, account: Account
) -> None:
    """Tests the `buy_asset` method with mbr included."""
    box = lambda name: b64decode(
        algod_client.application_box_by_name(app_client.app_id, name)["value"]
    )

    # Generate new account
    account = get_account(app_client.algod_client, "test_buyer")
    app_client.signer = AccountTransactionSigner(account.private_key)

    # Register new user
    user_box_name = b"user" + decode_address(account.address)
    app_client.register(
        name="Ash",
        transaction_parameters=TransactionParameters(boxes=[(0, user_box_name)]),
    )

    # Get asset price from box storage
    asset_name = "POKEBALL"
    asset_box_name = b"asset" + (
        asset_id := sha256(abi.StringType().encode(asset_name)).digest()
    )
    _, _, asset_price = abi.ABIType.from_string("(string,string,uint64)").decode(
        box(asset_box_name)
    )
    asset = abi.ABIType.from_string("(string,string,uint64)").decode(
        box(asset_box_name)
    )

    # Calculate mbr for one unit of asset
    asset_bytes_length = len(box(asset_box_name)) + len(asset_id)
    # Assume asset bytes length is based on asset name length
    mbr_per_unit = 2_500 + (400 * (asset_bytes_length))

    # Construct payment transaction to fund the user's game account
    ptxn = PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=app_client.app_address,
        amt=asset_price * 2 + mbr_per_unit * 2,
    )

    # Fund the user's account
    app_client.fund_account(
        payment=TransactionWithSigner(
            ptxn, AccountTransactionSigner(account.private_key)
        ),
        transaction_parameters=TransactionParameters(
            boxes=[(0, b"user" + decode_address(account.address))]
        ),
    )

    # Get user balance before buying asset
    user_box_abi = abi.ABIType.from_string("(uint64,string,uint64)")
    _, _, balance_before = user_box_abi.decode(box(user_box_name))
    user_asset_box_name = (
        b"user_asset" + sha256(decode_address(account.address) + asset_id).digest()
    )

    # Get user-asset quantity before buying
    try:
        quantity_before = abi.UintType(64).decode(box(user_asset_box_name))
    except AlgodHTTPError:
        quantity_before = 0

    buy = lambda: app_client.buy_asset(
        asset_id=asset_id,
        quantity=1,
        transaction_parameters=TransactionParameters(
            boxes=[
                (0, asset_box_name),
                (0, user_box_name),
                (0, user_asset_box_name),
            ]
        ),
    )

    # Buy one unit of asset
    buy()
    # Buy another unit of asset
    buy()

    # Get user balance after buying two units of the asset
    _, _, balance_after = user_box_abi.decode(box(user_box_name))

    # Test user balance after deduction of asset price and mbr
    total_spent = asset_price * 2 + mbr_per_unit * 2
    assert balance_before - total_spent == balance_after

    # Test user-asset box value
    quantity_after = abi.UintType(64).decode(box(user_asset_box_name))
    assert quantity_after - 2 == quantity_before


def test_sellback_asset(
    algod_client: AlgodClient, app_client: GameClient, account: Account
) -> None:
    """Tests the `sellback_asset` method."""
    box = lambda name: b64decode(
        algod_client.application_box_by_name(app_client.app_id, name)["value"]
    )

    # Génère un nouvel utilisateur pour le test
    account = get_account(app_client.algod_client, "test_seller")
    app_client.signer = AccountTransactionSigner(account.private_key)

    # Enregistre un nouvel utilisateur
    user_box_name = b"user" + decode_address(account.address)
    app_client.register(
        name="Seller",
        transaction_parameters=TransactionParameters(boxes=[(0, user_box_name)]),
    )

    # Ajoute un asset et obtient son ID et son prix
    asset_name = "POKEBALL"
    asset_box_name = b"asset" + (
        asset_id := sha256(abi.StringType().encode(asset_name)).digest()
    )
    _, _, asset_price = abi.ABIType.from_string("(string,string,uint64)").decode(
        box(asset_box_name)
    )

    # Calculate mbr for one unit of asset
    asset_bytes_length = len(box(asset_box_name)) + len(asset_id)
    # Assume asset bytes length is based on asset name length
    mbr_per_unit = 2_500 + (400 * (asset_bytes_length))

    # Finance le compte de l'utilisateur pour l'achat de l'asset
    ptxn = PaymentTxn(
        sender=account.address,
        sp=algod_client.suggested_params(),
        receiver=app_client.app_address,
        amt=asset_price * 2 + mbr_per_unit * 2,
    )
    app_client.fund_account(
        payment=TransactionWithSigner(
            ptxn, AccountTransactionSigner(account.private_key)
        ),
        transaction_parameters=TransactionParameters(
            boxes=[(0, b"user" + decode_address(account.address))]
        ),
    )

    # Achat de l'asset pour simuler la possession
    user_asset_box_name = (
        b"user_asset" + sha256(decode_address(account.address) + asset_id).digest()
    )
    app_client.buy_asset(
        asset_id=asset_id,
        quantity=2,
        transaction_parameters=TransactionParameters(
            boxes=[(0, asset_box_name), (0, user_box_name), (0, user_asset_box_name)],
        ),
    )

    # Obtenir le solde de l'utilisateur et la quantité d'asset avant la revente
    _, _, balance_before = abi.ABIType.from_string("(uint64,string,uint64)").decode(
        box(user_box_name)
    )

    quantity_before = abi.UintType(64).decode(box(user_asset_box_name))

    # Effectue la revente de l'asset
    app_client.sellback_asset(
        asset_id=asset_id,
        quantity=1,
        transaction_parameters=TransactionParameters(
            boxes=[(0, asset_box_name), (0, user_box_name), (0, user_asset_box_name)],
        ),
    )

    # Vérifie les quantités et les soldes après la revente
    _, _, balance_after = abi.ABIType.from_string("(uint64,string,uint64)").decode(
        box(user_box_name)
    )
    quantity_after = abi.UintType(64).decode(box(user_asset_box_name))

    # Calcul du remboursement attendu (sans frais de box si encore un asset restant)
    expected_refund = asset_price + mbr_per_unit

    # Assert solde mis à jour
    assert balance_after == balance_before + expected_refund
    # Assert quantité d'asset mis à jour
    assert quantity_after == quantity_before - 1


def test_set_asa_id(
    algod_client: AlgodClient, app_client: GameClient, account: Account
) -> None:
    app_client.signer = AccountTransactionSigner(account.private_key)

    created_asa = create_asa(algod_client, account)

    # asa_id = sha256(str(created_asa).encode("utf-8")).digest()
    asa_id = sha256(abi.StringType().encode(str(created_asa))).digest()
    app_client.set_asa_id(
        asa_id=asa_id,
    )
