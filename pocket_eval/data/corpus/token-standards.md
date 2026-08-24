# Token Standards

Token standards are shared interfaces that make assets interoperable across
wallets, exchanges, and applications. ERC-20 defines fungible tokens:
every unit is identical and interchangeable, like dollars or utility points.
Its functions include transfer, approve, and transferFrom, and its events
include Transfer and Approval. Most stablecoins and governance tokens are
ERC-20.

ERC-721 defines non-fungible tokens, where each token has a unique
identifier and distinct metadata. Collectibles, art, and membership cards
use it. ERC-1155 is a multi-token standard that bundles fungible and
non-fungible assets in one contract, saving gas in games where items come
in multiples and rarities.

ERC-4626 is the tokenized vault standard. It standardizes how yield-bearing
vaults interact with deposits, withdrawals, and shares. A vault holds
underlying assets, issues shares to depositors, and reports the exchange
rate between shares and assets. Standardization lets aggregators and
wallets plug into any vault without custom integration.

Choosing the right standard matters. A fungible asset as ERC-721 breaks
wallets that batch transfer. An ERC-20 with a flawed approve flow opens the
classic approval phishing attack, where a malicious contract gets
permission to spend a user's tokens. Standards reduce integration cost but
never remove the need for careful review of the implementation.