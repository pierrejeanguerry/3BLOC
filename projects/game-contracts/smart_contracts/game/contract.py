from typing import TypeAlias

from algopy import (
    Account,
    ARC4Contract,
    BoxMap,
    Box,
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


# class TradeOffer(arc4.Struct):
#     creator: Account
#     offered_asset: Hash
#     offered_quantity: Quantity
#     requested_asset: Hash
#     requested_quantity: Quantity
#     active: arc4.Bool


class Game(ARC4Contract):
    def __init__(self) -> None:
        self.user = BoxMap(Account, User)
        self.asset = BoxMap(Hash, GameAsset)
        self.user_asset = BoxMap(Hash, Quantity)
        self.user_asa = BoxMap(Hash, Quantity)
        self.asa_id = Box(Hash, key=b"a")
        # self.trade_offers = BoxMap(Hash, TradeOffer)

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

    # Question 1
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

    # Question 2
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

    # Question 3
    @arc4.abimethod
    def exchange_assets(
        self,
        sender_asset_id: Hash,
        sender_quantity: Quantity,
        receiver: Account,
        receiver_asset_id: Hash,
        receiver_quantity: Quantity,
    ) -> None:
        """Permet aux utilisateurs d'échanger leurs actifs.

        Args:
            sender_asset_id (Hash): ID de l'actif de l'expéditeur.
            sender_quantity (Quantity): Quantité de l'actif de l'expéditeur.
            receiver (Account): Compte du destinataire.
            receiver_asset_id (Hash): ID de l'actif du destinataire.
            receiver_quantity (Quantity): Quantité de l'actif du destinataire.
        """
        # Vérifications de base
        assert Txn.sender in self.user, "L'expéditeur doit être enregistré"
        assert Txn.receiver in self.user, "Le destinataire doit être enregistré"

        sender_asset_key = op.sha256(Txn.sender.bytes + sender_asset_id)
        receiver_asset_key = op.sha256(receiver.bytes + receiver_asset_id)

        assert sender_asset_key in self.user_asset, "Sender do not own the asset"
        assert (
            self.user_asset[sender_asset_key] >= sender_quantity
        ), "Quantité insuffisante pour l'expéditeur"

        assert (
            receiver_asset_key in self.user_asset
        ), "Le destinataire ne possède pas cet actif"
        assert (
            self.user_asset[receiver_asset_key] >= receiver_quantity
        ), "Quantité insuffisante pour le destinataire"

        # Mise à jour des actifs
        self.user_asset[sender_asset_key] -= sender_quantity
        if self.user_asset[sender_asset_key] == 0:
            del self.user_asset[sender_asset_key]

        self.user_asset[receiver_asset_key] -= receiver_quantity
        if self.user_asset[receiver_asset_key] == 0:
            del self.user_asset[receiver_asset_key]

        sender_new_asset_key = op.sha256(receiver.bytes + sender_asset_id)
        receiver_new_asset_key = op.sha256(Txn.sender.bytes + receiver_asset_id)

        if sender_new_asset_key in self.user_asset:
            self.user_asset[sender_new_asset_key] += sender_quantity
        else:
            self.user_asset[sender_new_asset_key] = sender_quantity

        if receiver_new_asset_key in self.user_asset:
            self.user_asset[receiver_new_asset_key] += receiver_quantity
        else:
            self.user_asset[receiver_new_asset_key] = receiver_quantity

    # @arc4.abimethod
    # def create_trade_offer(
    #     self,
    #     offered_asset: Hash,
    #     offered_quantity: Quantity,
    #     requested_asset: Hash,
    #     requested_quantity: Quantity,
    # ) -> Hash:
    #     """Crée une offre d'échange.

    #     Args:
    #         offered_asset (Hash): L'actif proposé.
    #         offered_quantity (Quantity): La quantité proposée.
    #         requested_asset (Hash): L'actif demandé.
    #         requested_quantity (Quantity): La quantité demandée.

    #     Returns:
    #         Hash: L'ID de l'offre créée.
    #     """
    #     assert Txn.sender in self.user, "L'utilisateur doit être enregistré"

    #     offer_key = op.sha256(
    #         Txn.sender.bytes + Global.latest_timestamp.bytes
    #     )
    #     sender_asset_key = op.sha256(Txn.sender.bytes + offered_asset)

    #     assert sender_asset_key in self.user_asset, "Vous ne possédez pas cet actif"
    #     assert (
    #         self.user_asset[sender_asset_key] >= offered_quantity
    #     ), "Quantité insuffisante pour proposer l'offre"

    #     # Geler les actifs offerts dans l'offre
    #     self.user_asset[sender_asset_key] -= offered_quantity

    #     self.trade_offers[offer_key] = TradeOffer(
    #         creator=Txn.sender,
    #         offered_asset=offered_asset,
    #         offered_quantity=offered_quantity,
    #         requested_asset=requested_asset,
    #         requested_quantity=requested_quantity,
    #         active=arc4.Bool(True),
    #     )

    #     return offer_key

    # @arc4.abimethod
    # def accept_trade_offer(self, offer_id: Hash) -> None:
    #     """Accepte une offre d'échange.

    #     Args:
    #         offer_id (Hash): L'ID de l'offre à accepter.
    #     """
    #     assert Txn.sender in self.user, "L'utilisateur doit être enregistré"
    #     assert offer_id in self.trade_offers, "Offre invalide"

    #     offer = self.trade_offers[offer_id]
    #     assert offer.active, "Offre déjà acceptée ou annulée"

    #     receiver_asset_key = op.sha256(Txn.sender.bytes + offer.requested_asset)
    #     creator_asset_key = op.sha256(offer.creator.bytes + offer.offered_asset)

    #     assert (
    #         receiver_asset_key in self.user_asset
    #     ), "Vous ne possédez pas l'actif demandé"
    #     assert (
    #         self.user_asset[receiver_asset_key] >= offer.requested_quantity
    #     ), "Quantité insuffisante pour accepter l'offre"

    #     # Échange des actifs
    #     self.user_asset[receiver_asset_key] -= offer.requested_quantity
    #     self.user_asset[creator_asset_key] += offer.requested_quantity

    #     if creator_asset_key in self.user_asset:
    #         self.user_asset[creator_asset_key] += offer.offered_quantity
    #     else:
    #         self.user_asset[creator_asset_key] = offer.offered_quantity

    #     if receiver_asset_key in self.user_asset:
    #         self.user_asset[receiver_asset_key] += offer.requested_quantity
    #     else:
    #         self.user_asset[receiver_asset_key] = offer.requested_quantity

    #     # Désactiver l'offre
    #     offer.active = arc4.Bool(False)
    #     self.trade_offers[offer_id] = offer

    # @arc4.abimethod
    # def cancel_trade_offer(self, offer_id: Hash) -> None:
    #     """Annule une offre d'échange.

    #     Args:
    #         offer_id (Hash): L'ID de l'offre à annuler.
    #     """
    #     assert Txn.sender in self.user, "L'utilisateur doit être enregistré"
    #     assert offer_id in self.trade_offers, "Offre invalide"

    #     offer = self.trade_offers[offer_id]
    #     assert (
    #         offer.creator == Txn.sender
    #     ), "Vous ne pouvez annuler que vos propres offres"
    #     assert offer.active, "Offre déjà désactivée"

    #     # Rendre les actifs gelés
    #     creator_asset_key = op.sha256(offer.creator.bytes + offer.offered_asset)
    #     self.user_asset[creator_asset_key] += offer.offered_quantity

    #     # Désactiver l'offre
    #     offer.active = arc4.Bool(False)
    #     self.trade_offers[offer_id] = offer

    # Question 4
    @arc4.abimethod
    def set_asa_id(self, asa_id: Hash) -> None:
        """Sets the ASA ID for the game currency."""
        if not self.asa_id:
            self.asa_id.value = asa_id
        else:
            assert self.asa_id.value == asa_id, "ASA ID mismatch"

    @arc4.abimethod
    def distribute_asa(self, quantity: Quantity) -> None:
        """Updates or inserts an ASA.

        Args:
            quantity (Quantity): The quantity to distribute.
        """
        assert self.asa_id, "ASA ID not set"
        assert (
            Txn.sender == Global.creator_address
        ), "Only the creator can call this method"
        assert Txn.receiver in self.user, "Receiver must be registered"

        user_asa_id = op.sha256(Txn.receiver.bytes + op.sha256(self.asa_id.value))
        if user_asa_id in self.user_asset:
            self.user_asset[user_asa_id] += quantity
        else:
            self.user_asset[user_asa_id] = quantity

    # Question 5
    @arc4.abimethod
    def register_nft(
        self, nft_id: Hash, name: arc4.String, description: arc4.String
    ) -> None:
        """Registers a new NFT in the contract.

        Args:
            nft_id (Hash): The ASA ID representing the NFT.
            name (arc4.String): The name of the NFT.
            description (arc4.String): A description of the NFT.
        """
        assert nft_id not in self.asset, "NFT already registered"
        self.asset[nft_id] = GameAsset(
            name=name, description=description, price=arc4.UInt64(0)
        )

    @arc4.abimethod
    def assign_nft(self, nft_id: Hash, receiver: Account) -> None:
        """Assigns an NFT to a user.

        Args:
            nft_id (Hash): The ASA ID of the NFT.
            receiver (Account): The user's account.
        """
        assert nft_id in self.asset, "NFT not registered"
        assert Txn.receiver in self.user, "Receiver must be a registered user"

        user_nft_id = op.sha256(Txn.receiver.bytes + nft_id)
        assert user_nft_id not in self.user_asset, "NFT already assigned to user"

        self.user_asset[user_nft_id] = Quantity(1)

    @arc4.abimethod
    def check_nft_ownership(self, nft_id: Hash, user: Account) -> arc4.Bool:
        """Checks if a user owns a specific NFT.

        Args:
            nft_id (Hash): The ASA ID of the NFT.
            user (Account): The user's account.

        Returns:
            arc4.Bool: True if the user owns the NFT, False otherwise.
        """
        user_nft_id = op.sha256(user.bytes + nft_id)
        return arc4.Bool(user_nft_id in self.user_asset)
