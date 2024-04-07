In this file I will explain how the cosmos trading history log works:

# Node Configuration
* Inside staketaxcsv/settings_csv.py you will find the list of nodes that are used in oreder to get blockchain access,
  most blockchains need to have an lcd node in order for it to works (e.g. AKASH,EVMOS,SCRT)

# Transaction History
* Inside staketaxcsv/common/ibc/api_lcd.py the function get_txs_all returns our transactions using the node, query parameters based on the need (transaction list)
* After getting the transaction list we want to process the transaction to be written in our needed format, this is found in staketaxcsv/common/ibc/processor.py