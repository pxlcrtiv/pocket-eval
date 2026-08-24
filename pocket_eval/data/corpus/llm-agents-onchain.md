# LLM Agents On-Chain

Large language model agents are starting to hold wallets and act on
blockchains. An agent parses a goal, breaks it into steps, chooses tools,
and signs transactions. Common tools include reading balances, simulating
transfers, querying on-chain data, and executing swaps on testnets or
mainnet. The agent's model, memory, and tool harness form the system.

Tool use is where agents meet crypto. The model emits structured calls —
transfer funds, check allowance, approve, swap — and the harness executes
them against a wallet. Safety requires boundaries: agents should run on
testnets until proven, require confirmation for irreversible actions, and
never hold more than a small budget. A dry-run layer that simulates the
transaction before signing catches most mistakes.

Prompt injection is the sharpest risk. An agent fetches web pages, reads
emails, or ingests untrusted text; that text can contain instructions that
redirect the agent. The fetched content must be treated as data, isolated
from the system prompt, and scanned before use. An agent that signs
transactions adds real stakes to a text-level vulnerability.

The roadmap is encouraging: agents that verify transactions with
simulation, that split keys across guardians, that log every decision for
audit, and that escalate to a human when a goal requires large value.
On-chain agents are a frontier where LLM engineering and security
engineering must merge, and the tools are still young.