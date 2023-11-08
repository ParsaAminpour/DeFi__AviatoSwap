
# Design Patterns

## ROLE-BASED Access controler
The **AviatoSwapV2** contract utilizes the Role-Based Access Control (RBAC) pattern provided by OpenZeppelin to manage permissions and access to contract functions.

RBAC allows assigning roles like **"ADMIN"** or **"LIQUIDITY_PROVIDER_ROLE"** to Ethereum accounts. Accounts with a role can then perform certain actions like remove liquidity.

On contract deployment, the deploying account is assigned the default admin role to bootstrap the permission setup. New roles and accounts can then be added programmatically based on business needs.

Overall this provides a transparent and efficient way to implement permissions compared to alternatives like access control lists. The admin account serves as the root of trust for role management which is has granted to contract's address and the contract owner in smart contract's constructor.

### centralization matter
In the **AviatoSwapV2** smart contract, The **"ADMIN"** role should transfer to a multi-sig wallet like Gnosis-Safe or a DAO like Aragon or XDAO, which will remove centralization power of one specified account to a bunch of accounts which privileged via the amount of liquidity they add before;
if the liquidity amount of that provider exceeds variance area of liquidity providers' balances, the "**LIQUIDITY_PROVIDER_ROLE"** role will grant to that provider.

- [x]  Function access modifier
- [x]  Decentralization matter
- [ ]  Security Flaws of Contract's role itself 


---

## Transparent Design Pattern

In this methodology ADMINs can’t call implementation contract’s functions and they only allow to call ADMIN contract functions and therefore Users can only call implementation contract’s functions **and this prevent function selector signature collision.**


### More Explanation about roles in Transparent architecture

In this pattern, there are three main roles:

1. **Proxy Contract**: The proxy contract is the one with a fixed address that users and other contracts interact with. It is responsible for forwarding function calls and data to an implementation contract. The proxy contract itself doesn't contain the business logic; it delegates calls to the implementation contract.

2. **Implementation Contract**: The implementation contract contains the actual business logic of the **AviatoSwapV1**. It can be replaced with **AviatoSwapV2** without changing the proxy's address. The implementation contract is not meant to be directly accessed by users or external applications. Instead, it is accessed through the proxy (that constant address).

3. **ProxyAdmin**: The ProxyAdmin is responsible for managing the upgradeability of the proxy contract in **AviatoSwapV2**. It has the authority to change the address of the implementation contract that the proxy points to. This role is generally controlled by the contract owner or the developer responsible for upgrading the smart contract, but in this smart contract role will be a multi-sig wallet.

Here's how these roles interact in AviatoSwap:

- Initially, the ProxyAdmin deploys the proxy contract and associates it with a specific **AviatoSwapV1** contract which is that implementation contract.

- Users and other smart contracts interact with the proxy contract as if it were the implementation contract. The proxy contract forwards all function calls and data to the **AviatoSwapV2** after the contract has been upgraded.

- When it's time to upgrade the contract (e.g., adding Role-Based access control system and variance calculation for grant and revok role), the ProxyAdmin deploys a new version of the implementation contract **(AviatoSwapV2)**. The new implementation contract can have improved or modified logic.

- The ProxyAdmin updates the proxy contract's implementation address to point to the new implementation contract, effectively upgrading the contract's logic.

- Users and external applications can continue to interact with the same proxy contract address, but now they are using the updated logic from the new implementation **AviatoSwapV2** contract.
