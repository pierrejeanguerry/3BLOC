from algosdk.v2client import algod
from algosdk import account, transaction, mnemonic


# Définir l'adresse et le token du nœud local, puis créer le client
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
algod_client = algod.AlgodClient(algod_token, algod_address)

# Définir l'adresse du gestionnaire
# algokit goal account list
# copier addresse de compte qui aura cette forme:
# "UZUCEIUYEWHNWIKBI2U5HCT7QJK6EN5C6MMIS5DJLFT6CES3UMN7VSGWTU"
account_address = "UZUCEIUYEWHNWIKBI2U5HCT7QJK6EN5C6MMIS5DJLFT6CES3UMN7VSGWTU"

# definir reuperer la phrase mnemonic
# algokit goal account export -a <address>
# copier le mnemonic passphrase qui aura cette forme:
# "weird steak hotel awake arctic observe combine dumb grocery judge radar snake excuse seminar shoot inside amazing plate key alone power ceiling bleak absorb happy"
mnemonic_phrase = "weird steak hotel awake arctic observe combine dumb grocery judge radar snake excuse seminar shoot inside amazing plate key alone power ceiling bleak absorb happy"
private_key = mnemonic.to_private_key(mnemonic_phrase)


sp = algod_client.suggested_params()
txn = transaction.AssetConfigTxn(
    sender=account_address,
    sp=sp,
    default_frozen=False,
    unit_name="GST",
    asset_name="GameShop Token",
    manager=account_address,
    reserve=account_address,
    freeze=account_address,
    clawback=account_address,
    url="",
    total=1000,
    decimals=0,
)

# Sign with secret key of creator
stxn = txn.sign(private_key)
# Send the transaction to the network and retrieve the txid.
txid = algod_client.send_transaction(stxn)
print(f"Sent asset create transaction with txid: {txid}")
# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

# grab the asset id for the asset we just created
created_asset = results["asset-index"]
print(f"Asset ID created: {created_asset}")
