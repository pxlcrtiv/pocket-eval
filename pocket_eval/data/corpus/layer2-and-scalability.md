# Layer 2 and Scalability

Public blockchains trade speed for security. Layer 2 networks inherit the
security of the base layer while moving computation off it, drastically
cutting gas costs and increasing throughput. Rollups are the dominant
design: they execute transactions off-chain, post compressed data to the
base layer, and rely on the base layer for settlement and availability.

Optimistic rollups assume transactions are valid until challenged. A
sequencer orders transactions and posts state roots. Any party can submit
a fraud proof within a challenge window, showing that a state transition
was invalid. If the fraud proof succeeds, the sequencer is slashed. The
challenge window is what makes withdrawals slow: users wait days to
finalize, though fast exit markets bridge the gap.

Zero-knowledge rollups, or zk-rollups, post validity proofs instead.
Each batch arrives with a cryptographic proof that the state transition is
correct, so there is no challenge window and withdrawals can be near
instant. The trade-off is the cost and complexity of generating proofs,
though proving hardware keeps improving.

Sidechains are separate blockchains with their own consensus and security,
bridged to the base layer. They are faster but weaker: a sidechain failure
does not take the base layer down, but it can strand bridged funds.
Aggregation layers, shared sequencers, and native rollups continue to
reshape the landscape. The metric that matters is finality: how quickly a
transaction is guaranteed to be irreversible.