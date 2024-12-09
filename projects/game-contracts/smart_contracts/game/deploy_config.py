import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.game.game_client import (
        GameClient,
    )

    asset_fee = 1
    box_fee = 100

    game_client = GameClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
        newasset_fee=asset_fee,
        newbox_fee=box_fee,
    )

    game_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
