# Stablecoins and Oracles

A stablecoin is a token designed to hold a stable value, usually pegged to
the US dollar. The dominant category is collateralized: DAI is backed by
crypto collateral deposited in vaults, and USDC is backed by reserves held
by its issuer. Overcollateralization absorbs price swings: a vault must
hold more collateral than the value of the debt it mints, or it gets
liquidated.

Collateralization ratio is the buffer between the debt and the collateral
value. If the ratio falls below the liquidation threshold, liquidation
seizes collateral to repay the debt. This mechanism keeps the peg intact
under stress. Algorithmic stablecoins without backing have historically
failed: when confidence drops, the self-referential mechanism cannot
support the price.

Oracles bring off-chain data on-chain. Price oracles feed asset prices
into lending protocols, derivatives, and prediction markets. If an oracle
is wrong, liquidation engines misfire and positions get wrongly seized.
Oracle manipulation attacks change the source of truth — for example, by
taking a flash loan, selling enough tokens to move a spot price, and
trading against the corrupted price inside the same transaction.

Robust oracle design uses multiple sources, time-weighted average prices,
and deviation thresholds that flag suspicious moves. Chainlink price feeds
aggregate many exchanges and update on deviation; they are the industry
standard for critical price data. Centralization is the trade-off: more
decentralized oracles are slower and more expensive. Trust in a protocol
is largely trust in its oracles.