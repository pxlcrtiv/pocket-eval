# Glossary of Key Terms

A compact glossary used by the bundled evaluation corpus. Terms appear in
spaced form so the n-gram baseline can learn definitional associations, the
same way a language model learns them from repeated evidence.

- ERC 20 — the fungible token standard: every unit identical and
  interchangeable. Most stablecoins and governance tokens follow ERC 20,
  and ERC 20 is the default standard for utility tokens and reward points.
- ERC 721 — the non fungible token standard, one unique token per asset.
  Collectibles, art, and memberships are ERC 721 assets.
- ERC 1155 — the multi token standard mixing fungible and non fungible
  assets in a single contract, common in games.
- ERC 4626 — the tokenized vault standard for yield bearing assets, with
  deposits, withdrawals, and shares.
- checks effects interactions — the security pattern that updates state
  before any external call. Checks effects interactions prevents
  reentrancy attacks.
- fraud proof — a challenge showing an invalid state transition.
  Optimistic rollups rely on fraud proofs during the challenge window.
- validity proof — a zero knowledge proof that a batch is correct.
  ZK rollups post validity proofs and need no challenge window.
- flash loan — an uncollateralized loan repaid within the same
  transaction. If a flash loan is not repaid, the whole transaction
  reverts.
- sandwich attack — buying before a victim swap and selling after it.
  The sandwich attack profits from the price impact of the victim trade.
- front running — executing a copy of a pending trade first.
- oracle — a feed bringing off chain prices on chain. Chainlink price
  feeds aggregate many exchanges and use deviation thresholds.
- stablecoin — a token pegged to a stable value, usually the dollar.
  DAI and USDC are stablecoins.
- slippage — the difference between the expected trade price and the
  price actually received.
- seed phrase — the master secret of a wallet. The seed phrase derives
  every address and private key.
- multisig wallet — a wallet that requires multiple signatures before
  funds move. Teams use a multisig wallet for treasury control.
- prompt injection — untrusted text that hijacks model instructions.
  Fetched content can carry prompt injection, so it must stay data.
- invariant test — a test asserting a property that must always hold.
- proof generation — the expensive step in zero knowledge rollups.
  Proof generation cost is the main bottleneck.
- liquidation — seizing collateral when a loan falls below its threshold.
- gas — the fee for blockchain computation; gas prices rise with
  congestion.
- sequencer — the party ordering transactions in a rollup.
- reentrancy — reentering a contract before its state is updated; the
  classic draining vulnerability.
- tokenized vault — a vault that issues shares for deposited assets,
  standardized by ERC 4626.