from typing import TypeAlias

from algopy import (
    Account,
    ARC4Contract,
    BoxMap,
    Bytes,
    Global,
    Txn,
    UInt64,
    arc4,
    gtxn,
    op,
)

Hash: TypeAlias = Bytes
Quantity: TypeAlias = UInt64


class User(arc4.Struct):
    registered_at: arc4.UInt64
    name: arc4.String
    balance: arc4.UInt64


class GameAsset(arc4.Struct):
    name: arc4.String
    description: arc4.String
    price: arc4.UInt64


class Game(ARC4Contract):
    def __init__(self) -> None:
        self.user = BoxMap(Account, User)
        self.asset = BoxMap(Hash, GameAsset)
        self.user_asset = BoxMap(Hash, Quantity)
        self.nft_assets = BoxMap(Hash, GameAsset)

    @arc4.abimethod
    def register(self, name: arc4.String) -> User:
        """Registers a user and returns their profile information.

        Args:
            name (arc4.String): The user's name.

        Returns:
            User: The user's profile information.
        """
        if Txn.sender not in self.user:
            self.user[Txn.sender] = User(
                registered_at=arc4.UInt64(Global.latest_timestamp),
                name=name,
                balance=arc4.UInt64(0),
            )
        return self.user[Txn.sender]

    @arc4.abimethod
    def fund_account(self, payment: gtxn.PaymentTransaction) -> arc4.UInt64:
        """Funds a user's account.

        Args:
            payment (gtxn.PaymentTransaction): The payment transaction.

        Returns:
            arc4.UInt64: The user's updated balance.
        """
        assert (
            payment.receiver == Global.current_application_address
        ), "Payment receiver must be the application address"
        assert payment.sender in self.user, "User must be registered"

        self.user[payment.sender].balance = arc4.UInt64(
            self.user[payment.sender].balance.native + payment.amount
        )
        return self.user[payment.sender].balance

    @arc4.abimethod
    def buy_asset(self, asset_id: Hash, quantity: Quantity) -> None:
        """Buys a game asset.

        Args:
            asset_id (Hash): The hash of the asset name.
            quantity (Quantity): The quantity to purchase.
        """
        assert Txn.sender in self.user, "User must be registered"
        assert asset_id in self.asset, "Invalid asset ID"

        user_balance = self.user[Txn.sender].balance.native
        asset_price = self.asset[asset_id].price.native

        asset_bytes_length = self.asset[asset_id].bytes.length + asset_id.length
        mbr_per_unit = 2_500 + (400 * (asset_bytes_length))

        assert user_balance >= (
            total := asset_price * quantity + mbr_per_unit * quantity
        ), "Insufficient funds"

        # Update user balance
        self.user[Txn.sender].balance = arc4.UInt64(user_balance - total)

        # Insert or update user-asset box
        user_asset_id = op.sha256(Txn.sender.bytes + asset_id)
        if user_asset_id in self.user_asset:
            self.user_asset[user_asset_id] += quantity
        else:
            self.user_asset[user_asset_id] = quantity

    @arc4.abimethod
    def admin_upsert_asset(self, asset: GameAsset) -> None:
        """Updates or inserts a game asset.

        Args:
            asset (GameAsset): The game asset information.
        """
        assert (
            Txn.sender == Global.creator_address
        ), "Only the creator can call this method"
        self.asset[op.sha256(asset.name.bytes)] = asset.copy()

    @arc4.abimethod
    def sellback_asset(self, asset_id: Hash, quantity: Quantity) -> None:
        """Sell back a game asset to the application.

        Args:
            asset_id (Hash): The hash of the asset name.
            quantity (Quantity): The quantity to purchase.
        """
        assert Txn.sender in self.user, "User must be registered"
        assert asset_id in self.asset, "Invalid asset ID"

        user_balance = self.user[Txn.sender].balance.native
        asset_price = self.asset[asset_id].price.native

        asset_bytes_length = self.asset[asset_id].bytes.length + asset_id.length
        mbr_per_unit = 2_500 + (400 * (asset_bytes_length))

        user_asset_id = op.sha256(Txn.sender.bytes + asset_id)
        assert user_asset_id in self.user_asset, "No assets found"
        assert (
            self.user_asset[user_asset_id] >= quantity
        ), "Insufficient amount of assets"

        # update or remove user-asset box
        self.user_asset[user_asset_id] -= quantity
        if self.user_asset[user_asset_id] == 0:
            del self.user_asset[user_asset_id]

        # Update user balance
        self.user[Txn.sender].balance = arc4.UInt64(
            user_balance + (asset_price * quantity) + mbr_per_unit
        )
