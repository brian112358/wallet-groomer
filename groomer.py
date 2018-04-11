#!/usr/bin/python2
# simple cleanup script, 2012-12-25 <greg@xiph.org>
# 2018: updated by brianmct
import sys
import operator
from decimal import *
from bitcoinrpc.authproxy import AuthServiceProxy
import argparse

parser = argparse.ArgumentParser(description='This script generates transaction(s) to cleanup your wallet.\n'
'It looks for the single addresses which have the most small confirmed payments made to them and merges\n'
'all those payments, along with those for any addresses which are all tiny payments, to a single txout.\n'
'It must connect to raven to inspect your wallet and to get fresh addresses to pay your coin to.')
parser.add_argument('rpc_server', type=str, help='Wallet RPC server info. '
                    'Example: http://user:password@127.0.0.1:8766')
parser.add_argument('-i', '--max_amt_input', type=float, default=25,
  help='The maximum input amount of a single transaction to consolidate (default: 25 RVN)')
parser.add_argument('-n', '--max_num_tx', type=int, default=500,
  help='The maximum number of transactions to consolidate at once. Lower this if you are getting a tx-size error (default: 500)')
parser.add_argument('-o', '--max_amt_per_output', type=float, default=10000,
  help='The maximum amount (in RVN) to send to a single output address (default: 10000 RVN)')
parser.add_argument('-f', '--fee', type=float, default=0.001,
  help='The amount of fees (in RVN) to use for the transaction')

args = parser.parse_args()

try:
  b = AuthServiceProxy(args.rpc_server)
  b.getinfo()
except:
  print "Couldn't connect to raven"
  exit(1)
min_fee=Decimal(args.fee)

# Loop until wallet is clean
while True:
  #Add up the number of small txouts and amounts assigned to each address.
  coins=b.listunspent(1,99999999)
  scripts={}
  for coin in coins:
    script=coin['scriptPubKey']
    if script not in scripts:
      scripts[script]=(0,Decimal(0),0)
    if (coin['amount']<Decimal(args.max_amt_input) and coin['amount']>=Decimal(0.01) and coin['confirmations']>100):
      scripts[script]=(scripts[script][0]+1,scripts[script][1]+coin['amount'],scripts[script][0]+1)
    else:
      scripts[script]=(scripts[script][0],scripts[script][1]+coin['amount'],scripts[script][0]+1)

  #which script has the largest number of well confirmed small but not dust outputs?
  most_overused = max(scripts.iteritems(), key=operator.itemgetter(1))[0]

  #If the best we can do doesn't reduce the number of txouts or just moves dust, give up.
  if(scripts[most_overused][2]<3 or scripts[most_overused][1]<Decimal(0.01)):
    print "Wallet already clean."
    exit(0)

  usescripts=set([most_overused])

  #Also merge in scripts that are all dust, since they can't be spent without merging with something.
  for script in scripts.keys():
    if scripts[script][1]<Decimal(0.00010000):
      usescripts.add(script)

  amt=Decimal(0)
  txouts=[]
  for coin in coins:
    if len(txouts) >= args.max_num_tx:
      break
    if coin['scriptPubKey'] in usescripts:
      amt+=coin['amount']
      txout={}
      txout['txid']=coin['txid']
      txout['vout']=coin['vout']
      txouts.append(txout)
  print 'Creating tx from %d inputs of total value %s:'%(len(txouts),amt)
  for script in usescripts:
    print '  Script %s has %d txins and %s RVN value.'%(script,scripts[script][2],str(scripts[script][1]))

  out={}
  na=amt-min_fee
  #One new output per max_amt_per_output RVN of value to avoid consolidating too much value in too few addresses.
  # But don't add an extra output if it would have less than args.max_amt_per_output RVN.
  while na>0:
    amount=min(Decimal(args.max_amt_per_output),na)
    if ((na-amount)<10):
      amount=na
    addr=b.getnewaddress('consolidate')
    if (Decimal(str(float(amount)))>0):
      if addr not in out:
        out[addr]=float(0)
      out[addr]+=float(amount)
    na-=Decimal(str(float(amount)))
  print 'Paying %s RVN (%s fee) to:'%(sum([Decimal(str(out[k])) for k in out.keys()]),amt-sum([Decimal(str(out[k])) for k in out.keys()]))
  for o in out.keys():
    print '  %s %s'%(o,out[o])

  txn=b.createrawtransaction(txouts,out)

  a = raw_input('Sign the transaction? y/[n]: ')
  if a != 'y':
    exit(0)

  signed_txn=b.signrawtransaction(txn)
  print signed_txn
  print 'Bytes: %d Fee: %s'%(len(signed_txn['hex'])/2,amt-sum([Decimal(str(out[x])) for x in out.keys()]))

  a = raw_input('Send the transaction? y/[n]: ')
  if a != 'y':
    exit(0)

  txid = b.sendrawtransaction(signed_txn['hex'])
  print 'Transaction sent! txid: %s\n' % txid
