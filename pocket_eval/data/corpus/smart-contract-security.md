# Smart Contract Security

Smart contracts hold real value and run forever, so security is the
difference between a protocol that survives and one that gets drained.
The most famous vulnerability class is reentrancy: a contract calls an
external contract while its own state is still outdated, letting the
attacker re-enter and repeat the call before the balance is updated.
The classic fix is checks-effects-interactions: update internal state
before any external call, never after.

Access control is the second pillar. Functions that move funds must verify
who may call them. The Ownable pattern restricts critical functions to the
owner address, while role-based access control grants finer permissions.
A single missing modifier can let anyone withdraw the treasury.

Upgradeable contracts use proxy patterns. The proxy delegates calls to an
implementation contract via delegatecall. Storage lives in the proxy, logic
lives in the implementation. Timelocks give users time to inspect a pending
upgrade and exit before it executes. A contract with no timelock can be
changed overnight.

Auditing is layered: static analysis tools like Slither scan the bytecode
and source for known patterns, fuzzing throws random inputs at functions to
find edge cases, and manual review traces every state transition. Invariant
tests assert properties that must always hold, such as total supply
equaling the sum of all balances. Even audited contracts get exploited, so
defense in depth matters: pause switches, emergency withdrawal functions,
and conservative risk limits.