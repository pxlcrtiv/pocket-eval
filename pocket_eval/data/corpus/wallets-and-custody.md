# Wallets and Custody

A wallet is a keypair, not a container of coins: the private key signs
transactions and the public address receives funds. An externally owned
account, or EOA, is controlled directly by its private key. Smart contract
wallets add logic instead: multisig wallets require M-of-N signatures
before funds move, and social recovery lets trusted guardians restore
access if a key is lost.

The seed phrase is the master key. Twelve or twenty-four words derived
from a standard (BIP-39) can regenerate every address in the wallet. Anyone
with the seed phrase owns everything derived from it. Hardware wallets
keep private keys in a secure chip so signing happens offline; the
computer only ever sees the signature. This defeats most remote malware
because the key never touches the internet-connected device.

Custody is the trade-off between convenience and control. Exchanges hold
users' keys, which is why exchange hacks drain user funds. Self-custody
means holding the seed phrase, which protects against exchange failure but
exposes the user to their own operational risk: losing the phrase, or
signing a malicious transaction.

Transaction security is about what gets signed. A wallet should show the
exact amount, recipient, and network before signing. Blind signing of
opaque payloads is how approvals get abused. Allowances let contracts
spend tokens up to a limit; revoking unused allowances is a core hygiene
practice. Modern wallets simulate transactions first and surface the
state changes they would cause.