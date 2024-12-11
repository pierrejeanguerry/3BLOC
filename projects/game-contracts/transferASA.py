from algosdk.v2client import algod
from algosdk import transaction, mnemonic

address2 = "YCMAT6RCB2IJTA72PLHQZ2ZDUNTZC7EUYYOLXEFJNCEYZDG2ZJB6JBXVMM"
mnemonic_phrase2 = "net wrist nurse depend great price coil dignity trip weather chief tackle program license lamp gain worry build million object deposit fat setup absent pen"
private_key2 = mnemonic.to_private_key(mnemonic_phrase2)

address1 = "EGY4RDWYXN5TH3QMFZGLMYXW7EVLBNJNMK56Z45YXJSLYXMC6SP4I5XBGI"
mnemonic_phrase1 = "away chronic point private recycle cross thing news bronze poet disorder climb about raise cement habit frozen antenna focus diary inflict cushion render about model"
private_key1 = mnemonic.to_private_key(mnemonic_phrase1)

algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)


sp = algod_client.suggested_params()
# Create transfer transaction
xfer_txn = transaction.AssetTransferTxn(
    sender=address1,
    sp=sp,
    receiver=address2,
    amt=1,
    index=1003,
)
signed_xfer_txn = xfer_txn.sign(private_key1)
txid = algod_client.send_transaction(signed_xfer_txn)
print(f"Sent transfer transaction with txid: {txid}")

results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")
