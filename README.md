# wallet-groomer
Collects small transactions in a QT wallet into larger ones. This tool has been updated for Ravencoin, but should work on other coins using a BTC-forked QT wallet.

## Requirements:

This tool only works with Python 2. You will need to install the `bitcoinrpc` Python package. This can be done using `pip` by:

`sudo pip2 install python-bitcoinrpc`

You will also need to set up your QT wallet to start a RPC server, since this is how the tool interacts with the wallet. You can do so by editing your `raven.conf` file (or `bitcoin.conf`, `pigeon.conf`, etc depending on what wallet you're using). Feel free to edit the user/pass/port.

```
rpcuser=user
rpcpassword=password
rpcallowip=127.0.0.1
rpcport=8766
server=1
```

## Usage:

You should be able to simply run:

`python2 groomer.py http://user:password@127.0.0.1:8766`

(replace the user, password, and port if you've changed it from the `raven.conf` example above)

## Optional Arguments

Normally, there should be no need to use any of the optional arguments. Simply run `python2 groomer.py -h` to get the help page:

```
usage: groomer.py [-h] [-i MAX_AMT_INPUT] [-n MAX_NUM_TX]
                  [-o MAX_AMT_PER_OUTPUT] [-f FEE]
                  rpc_server

This script generates transaction(s) to cleanup your wallet. It looks for the
single addresses which have the most small confirmed payments made to them and
merges all those payments, along with those for any addresses which are all
tiny payments, to a single txout. It must connect to raven to inspect your
wallet and to get fresh addresses to pay your coin to.

positional arguments:
  rpc_server            Wallet RPC server info. Example:
                        http://user:password@127.0.0.1:8766

optional arguments:
  -h, --help            show this help message and exit
  -i MAX_AMT_INPUT, --max_amt_input MAX_AMT_INPUT
                        The maximum input amount of a single transaction to
                        consolidate (default: 25 RVN)
  -n MAX_NUM_TX, --max_num_tx MAX_NUM_TX
                        The maximum number of transactions to consolidate at
                        once. Lower this if you are getting a tx-size error
                        (default: 500)
  -o MAX_AMT_PER_OUTPUT, --max_amt_per_output MAX_AMT_PER_OUTPUT
                        The maximum amount (in RVN) to send to a single output
                        address (default: 10000 RVN)
  -f FEE, --fee FEE     The amount of fees (in RVN) to use for the transaction
```


## Donation Addresses:
If you've found this tool helpful, please consider donating to the following addresses:

- RVN: RWoSZX6j6WU6SVTVq5hKmdgPmmrYE9be5R

- BTC: 1FHLroBZaB74QvQW5mBmAxCNVJNXa14mH5

- ETH: 0x7255ba772ee18bdb8b9af0bdeae2e41f5874fb0b
