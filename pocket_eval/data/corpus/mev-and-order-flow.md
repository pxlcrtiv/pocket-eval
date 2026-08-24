# MEV and Order Flow

Maximal extractable value, or MEV, is the profit a block producer can
capture by ordering, including, or excluding transactions within a block.
Because block producers decide the order, they can front-run trades,
sandwich swaps, or liquidate positions before anyone else can react.

A sandwich attack targets a large swap. The attacker buys the token first,
driving the price up, lets the victim's swap execute at the worse price,
then sells immediately after, profiting from the price difference the
victim paid. Frontrunning is simpler: an attacker sees a pending
transaction, copies it with a higher gas price, and executes their own
version first.

Liquidations are legitimate MEV: when a borrower's collateral falls below
the liquidation threshold, anyone can repay the debt and seize the
collateral plus a bonus. This keeps lending protocols solvent. The problem
is when MEV strategies harm users, as sandwich attacks do.

Mitigations include private transaction relays that send transactions
directly to block producers, commit-reveal schemes that hide the contents
of a trade, and decentralized order flow auctions that sell the right to
order transactions. Protocol design matters too: fair-ordering mechanisms
and batch auctions reduce the surface. MEV is not inherently evil — it is
an economic force that must be priced and channeled, not ignored.