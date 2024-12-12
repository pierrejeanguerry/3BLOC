from algosdk.v2client import algod
from algosdk import transaction, mnemonic
from algosdk.v2client.algod import AlgodClient


class Account:
    def __init__(self, address, mnemonic):
        self.address = address
        self.mnemonic = mnemonic
        self.private_key = mnemonic.to_private_key(mnemonic)


# Utilisation
receiver = Account(
    address="YCMAT6RCB2IJTA72PLHQZ2ZDUNTZC7EUYYOLXEFJNCEYZDG2ZJB6JBXVMM",
    mnemonic="net wrist nurse depend great price coil dignity trip weather chief tackle program license lamp gain worry build million object deposit fat setup absent pen",
)

sender = Account(
    sender_address="EGY4RDWYXN5TH3QMFZGLMYXW7EVLBNJNMK56Z45YXJSLYXMC6SP4I5XBGI",
    sender_mnemonic="away chronic point private recycle cross thing news bronze poet disorder climb about raise cement habit frozen antenna focus diary inflict cushion render about model",
)

asset_id = 1003

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)


def transfer_ASA(sender: Account, receiver: Account, algod_client: AlgodClient):

    sp = algod_client.suggested_params()
    # optin
    optin_txn = transaction.AssetOptInTxn(
        sender=receiver.address, sp=sp, index=asset_id
    )
    signed_optin_txn = optin_txn.sign(receiver.private_key)
    txid = algod_client.send_transaction(signed_optin_txn)
    results = transaction.wait_for_confirmation(algod_client, txid, 4)

    # transfer
    xfer_txn = transaction.AssetTransferTxn(
        sender=sender.address,
        sp=sp,
        receiver=receiver.address,
        amt=1,
        index=asset_id,
    )
    signed_xfer_txn = xfer_txn.sign(sender.private_key)
    txid = algod_client.send_transaction(signed_xfer_txn)
    results = transaction.wait_for_confirmation(algod_client, txid, 4)


transfer_ASA(sender, receiver, algod_client)
