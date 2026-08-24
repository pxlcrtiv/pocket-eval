# Gas, Fees, and Account Abstraction

Every transaction on a public blockchain costs gas: a fee paid to the
network for the computation the transaction triggers. Gas is priced per
unit of work, and the total cost is gas used times the price per unit.
Congestion raises prices; calm lowers them. Fee markets use priority fees
to let users jump the queue, and EIP-1559 burned a base fee to make fee
inflation visible.

Gas optimization is a craft. Storage is the most expensive resource:
every slot written costs thousands of gas, so packing variables and
writing only on state change matters. Calldata, events, loops, and
external calls all cost. Optimizers shrink bytecode at deploy time, but
the real savings come from design — fewer writes, fewer calls, less data.

Account abstraction rewrites who can pay. Traditional accounts must hold
the native token for gas. Smart accounts let third parties pay the fee,
allow token-denominated gas, sponsor transactions for users, and set
custom validation rules — paying with a stablecoin or having an app cover
the first hundred transactions. This is the UX unlock that lets
non-crypto users use crypto apps without ever touching native tokens.

User operations decouple intent from execution: a user signs an intent,
and any executor can bundle and submit it, paying gas on the user's
behalf. Bundlers compete to execute, and inclusion lists protect users
from censorship. The fee market is becoming a market for intents, not
just transactions.