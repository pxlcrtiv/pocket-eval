# Flash Loans and DeFi Composability

A flash loan lets you borrow an unlimited amount of assets with no
collateral, as long as the loan is repaid within the same transaction.
If the borrowed funds are not returned by the end, the whole transaction
reverts. Flash loans are atomic: borrow, use, repay, all in one block.
They are the purest example of DeFi composability.

Legitimate uses include refinancing positions, arbitrage between
decentralized exchanges, and recapitalizing undercollateralized loans.
An arbitrageur can flash borrow a million dollars, buy a token at a lower
price on one exchange, sell it at a higher price on another, repay the
loan, and keep the profit — all without holding any capital.

Flash loans also supercharge attacks. Reentrancy attacks and oracle
manipulation attacks frequently use flash loans to get the capital needed
to move the price or to drain a contract that mishandles external calls.
The capital requirement for an exploit drops to zero, so every economic
constraint a protocol assumed must actually be enforced by code.

Defending against flash-loan-enabled attacks means removing price
dependence on manipulable liquidity. Time-weighted average prices resist
single-block manipulation. Minimum liquidity requirements make it
expensive to move a price. And any invariant that can be broken with one
transaction's worth of capital is not an invariant at all.