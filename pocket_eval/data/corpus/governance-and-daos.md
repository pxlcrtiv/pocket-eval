# Governance and DAOs

A decentralized autonomous organization is a community with shared funds
and on-chain rules. Governance tokens grant voting power, usually
proportional to holdings. Proposals describe a change — a fee adjustment,
a contract upgrade, a treasury grant — and token holders vote over a fixed
window. If the proposal passes, the timelock delays execution so users can
inspect and exit.

Voting power concentration is the central problem. Whales dominate
polls, and delegated voting lets a few delegates control many votes.
Sybil resistance — stopping one person from creating infinite identities —
is a constant war. Quadratic voting and conviction voting soften
concentration instead of removing it.

Governance attacks are economic: an attacker borrows tokens to vote,
passes a malicious proposal, withdraws the treasury, and returns the
loans. Lending markets and flash loans make governance capture cheap.
Mitigations include delegated-checkpointing that ignores freshly borrowed
tokens, proposal delays, and emergency response teams with limited power.

The mature view: DAOs work best for low-stakes coordination and worst for
emergencies. On-chain governance is slow, transparent, and irreversible;
off-chain forums and multisig execution teams bridge the gap between
deliberation and action.