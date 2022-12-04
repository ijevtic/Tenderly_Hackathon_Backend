// require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();


const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY;
const GOERLI_RPC_URL = process.env.GOERLI_RPC_URL;
const ACCOUNT = process.env.PRIVATE_KEY;
//npx hardhat verify --network goerli --constructor-args deploy/args.js 0x06bC8fA1F3a18D3e26b29B31Ec969aF2890196E9
// npx hardhat verify --constructor-args deploy/args.js 0x06bC8fA1F3a18D3e26b29B31Ec969aF2890196E9

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.17",
  networks: {
    hardhat: {
      chainId: 1337 // We set 1337 to make interacting with MetaMask simpler
    },
    goerli: {
      url: GOERLI_RPC_URL,
      accounts: [ACCOUNT],
      chainId: 5
    },
    local: {
        url: "https://127.0.0.1:8545",
        allowUnlimitedContractSize: true
    },
  },
  etherscan:{
    apiKey: ETHERSCAN_API_KEY
  }
};