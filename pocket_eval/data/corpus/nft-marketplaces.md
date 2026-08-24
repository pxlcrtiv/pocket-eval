# NFT Marketplaces and Digital Ownership

Non-fungible tokens turned digital goods into verifiable, transferable
assets. A marketplace lists items, matches buyers and sellers, and takes a
fee from each sale. On-chain marketplaces execute the trade in one
transaction: the NFT transfers to the buyer, the payment transfers to the
seller, and the fee goes to the protocol.

Royalties are the controversial piece. Creators traditionally received a
percentage of every secondary sale, enforced by marketplace policy rather
than by the token standard. As marketplaces compete, some made royalties
optional, and creators lost income. New standards experiment with
on-chain royalty enforcement at the transfer level.

Lending against NFTs introduced new primitives: floor-price loans,
fractionalization, and NFT collateral in lending protocols. The risk is
liquidity — an NFT has no guaranteed market price, so liquidation engines
must accept slow exits. Culture and finance collide in NFT lending far
more than in token lending.

The durable lesson is metadata: the token points to metadata that can
live on centralized servers, on IPFS, or fully on-chain. When the pointer
breaks, the art is gone even though the token remains. Fully on-chain
storage is the only version that survives its creators.