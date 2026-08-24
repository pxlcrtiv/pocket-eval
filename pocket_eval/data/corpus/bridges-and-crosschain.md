# Bridges and Cross-Chain Transactions

Bridges move assets between blockchains. A user locks tokens on the source
chain and receives equivalent tokens on the destination chain, with a
custodian or a set of validators guaranteeing the peg. Bridges are the
most attacked category in crypto: billions have been lost to compromised
validators, smart contract bugs, and social engineering.

The security model defines the risk. A federated bridge trusts a group of
signers; if enough keys are stolen, funds are stolen. An optimistic bridge
posts transactions and waits for watchers to challenge them. A
zero-knowledge bridge proves the source-chain state transition to the
destination chain, inheriting the security of the source chain without
trusting custodians.

Canonical bridges are the safest pattern: a lightweight client on the
destination chain verifies proofs of source-chain consensus directly. The
trade-off is implementation complexity and upgrade risk. Every bridge
node, relayer, and watcher is a potential point of failure.

For users, the practical advice is boring: prefer canonical bridges on
major chains, move small amounts first, and never bridge to unknown
networks. Cross-chain technology is improving, but the safest bridge is
the one you do not need.