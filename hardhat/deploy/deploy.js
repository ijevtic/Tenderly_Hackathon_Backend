const path = require("path");
const args = require("./args");
const hre = require("hardhat");


async function main() {

  // ethers is available in the global scope
  const [deployer] = await hre.ethers.getSigners();
  const addr =  await deployer.getAddress(); 
  console.log(
    "Deploying the contracts with the account:",
    addr
  );

  console.log("Account balance:", (await deployer.getBalance()).toString());

  const Token = await hre.ethers.getContractFactory("CustomContract");
  const token = await Token.deploy(...args);
  await token.deployed();

  console.log("Token address:", token.address);

}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });