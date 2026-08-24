# Zero-Knowledge Proofs and Privacy

A zero-knowledge proof lets one party prove a statement is true without
revealing why. In cryptography terms, a prover convinces a verifier that
they know a secret or that a computation is correct, while the verifier
learns nothing beyond the truth of the statement. Zero-knowledge
succinct non-interactive arguments of knowledge — zk-SNARKs — are the most
widely deployed construction on blockchains.

The proving process turns a computation into an arithmetic circuit.
The prover generates a short proof; the verifier checks it in a fraction
of the time the computation itself would take. This is the engine of
zk-rollups: every batch of transactions is compressed into a single
validity proof that the base layer verifies. Privacy applications use the
same machinery to hide transaction details while proving validity —
balances, senders, and amounts stay encrypted.

Scaling and privacy converge in the same primitive, which is why zero
knowledge became a core layer-2 technology. Proof generation is the
bottleneck: circuits with millions of constraints need serious hardware.
Recursive proofs let a proof verify another proof, enabling proof of
proofs and unbounded composition.

The practical questions are trust and engineering. Trusted setup
ceremonies used to be required; newer schemes are transparent.
Circuit bugs are catastrophic and irreversible, so frameworks emphasize
formal verification of the relation being proven. ZK is mature enough for
production — and still young enough that audits matter.