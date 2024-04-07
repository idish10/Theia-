import os

# Environment variables (required for each respective report)

ALGO_HIST_INDEXER_NODE = os.environ.get("STAKETAX_ALGO_HIST_INDEXER_NODE", "https://indexer.algoexplorerapi.io")
ALGO_INDEXER_NODE = os.environ.get("STAKETAX_ALGO_INDEXER_NODE", "https://algoindexer.algoexplorerapi.io")
ALGO_NFDOMAINS = os.environ.get("STAKETAX_ALGO_NFDOMAINS", "https://api.nf.domains")
ATOM_NODE = os.environ.get("STAKETAX_ATOM_NODE", "https://api.cosmos.network")
AKASH_NODE = os.environ.get("STAKETAX_AKS_NODE", "https://akash-api.polkachu.com:443")
BLD_NODE = os.environ.get("STAKETAX_BLD_NODE", "https://main.api.agoric.net")
BTSG_NODE = os.environ.get("STAKETAX_BTSG_NODE", "https://lcd.explorebitsong.com")
COVALENT_NODE = os.environ.get("STAKETAX_COVALENT_NODE", "https://api.covalenthq.com")
DVPN_LCD_NODE = os.environ.get("STAKETAX_DVPN_LCD_NODE", "https://lcd.sentinel.co") # sentinel blockchain
DVPN_RPC_NODE = os.environ.get("STAKETAX_DVPN_RPC_NODE", "https://rpc.sentinel.co")
EVMOS_NODE = os.environ.get("STAKETAX_EVMOS_NODE", "https://evmos-lcd.stakely.io")
FET_NODE = os.environ.get("STAKETAX_FET_NODE", "https://rest-fetchhub.fetch.ai")
HUAHUA_NODE = os.environ.get("STAKETAX_HUAHUA_NODE", "")
JUNO_NODE = os.environ.get("STAKETAX_JUNO_NODE", "")
KAVA_NODE = os.environ.get("STAKETAX_KAVA_NODE", "https://api.kava.io")
KUJI_NODE = os.environ.get("STAKETAX_KUJI_NODE", "")
NGM_NODE = os.environ.get("STAKETAX_NGM_NODE", "https://emoney.validator.network/api/")   # emoney blockchain
OSMO_NODE = os.environ.get("STAKETAX_OSMO_NODE", "https://lcd.osmosis.zone")
REGEN_NODE = os.environ.get("STAKETAX_REGEN_NODE", "")
SCRT_NODE = os.environ.get("STAKETAX_SCRT_NODE", "https://api.scrt.network")
STARS_NODE = os.environ.get("STAKETAX_STARS_NODE", "")
SOL_NODE = os.environ.get("STAKETAX_SOL_NODE", "https://api.mainnet-beta.solana.com")
SOM_NODE = os.environ.get("STAKE_SOM_NODE","https://api.sommelier.pupmos.network") # sommelier blockchain
TERRA_LCD_NODE = os.environ.get("STAKETAX_TERRA_LCD_NODE", "")
LUNA2_LCD_NODE = os.environ.get("STAKETAX_LUNA2_LCD_NODE", "https://phoenix-lcd.terra.dev")

# Optional environment variables
COVALENT_API_KEY = os.environ.get("STAKETAX_COVALENT_API_KEY", "")

# #############################################################################

TICKER_ALGO = "ALGO"
TICKER_ATOM = "ATOM"
TICKER_BLD = "BLD"
TICKER_BTSG = "BTSG"
TICKER_DVPN = "DVPN"
TICKER_EVMOS = "EVMOS"
TICKER_FET = "FET"
TICKER_HUAHUA = "HUAHUA"
TICKER_IOTEX = "IOTX"
TICKER_JUNO = "JUNO"
TICKER_KUJI = "KUJI"
TICKER_LUNA1 = "LUNA1"
TICKER_LUNA2 = "LUNA2"
TICKER_OSMO = "OSMO"
TICKER_REGEN = "REGEN"
TICKER_SOL = "SOL"
TICKER_STARS = "STARS"

DONATION_WALLETS = set([v for k, v in os.environ.items() if k.startswith("DONATION_WALLET_")])

MESSAGE_ADDRESS_NOT_FOUND = "Wallet address not found"
MESSAGE_STAKING_ADDRESS_FOUND = "Staking address found.  Please input the main wallet address instead."

REPORTS_DIR = os.path.dirname(os.path.realpath(__file__)) + "/_reports"

MINTSCAN_LABEL = {
    'EVMOS': 'evmos',
}