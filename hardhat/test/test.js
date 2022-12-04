const { expect, assert } = require("chai");
const BigNumber = require('big-number');


// We use `loadFixture` to share common setups (or fixtures) between tests.
// Using this simplifies your tests and makes them run faster, by taking
// advantage or Hardhat Network's snapshot functionality.
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const { ethers } = require("hardhat");


describe("Token contract", function () {
    
  async function deployContractFixture() {
    // Get the ContractFactory and Signers here.
    const CustomContract = await ethers.getContractFactory("CustomContract");
    const owner = (await ethers.getSigners())[0];
    const [ ,...senderAccounts] = (await ethers.getSigners());
    const customContract = await CustomContract.deploy("CustomContract", owner.address, false);

    await customContract.deployed();

    // Fixtures can return anything you consider useful for your tests
    return { CustomContract, customContract, owner, senderAccounts };
  }

  async function deployContractWithVerificationFixture() {
    // Get the ContractFactory and Signers here.
    const CustomContract = await ethers.getContractFactory("CustomContract");
    const owner = (await ethers.getSigners())[0];
    const [ ,...senderAccounts] = (await ethers.getSigners());
    const customContract = await CustomContract.deploy("CustomContract", owner.address, true);

    await customContract.deployed();

    // Fixtures can return anything you consider useful for your tests
    return { CustomContract, customContract, owner, senderAccounts };
  }

  // You can nest describe calls to create subsections.
    describe("Deployment", function () {

        it("Should set the right owner", async function () {
        const { customContract, owner } = await loadFixture(deployContractFixture);

        expect(await customContract.owner()).to.equal(owner.address);
        });

        it("Should withdraw funds to owner", async function(){

        const { customContract, owner,senderAccounts } = await loadFixture(deployContractFixture);
        //   console.log(senderAccounts[0].address)
        //   console.log(owner.address)

        const oldBalance = await ethers.provider.getBalance(owner.address);

        await senderAccounts[0].sendTransaction({
            to: customContract.address,
            value: ethers.utils.parseEther("1") // 1 ether
        });

        await customContract.withdrawFunds(ethers.utils.parseEther("1"));

        const newBalance = await ethers.provider.getBalance(owner.address);
        const diff = newBalance-oldBalance;

        assert.isTrue(BigNumber(diff.toString()).lt(1e18));
        assert.isTrue(BigNumber(diff.toString()).gt(999*1e14));
        // console.log(newBalance-oldBalance);

        });
    });

    describe("Join Community", function () {

        it("Should join ", async function () {
            const { customContract, owner, senderAccounts } = await loadFixture(deployContractFixture);
    
            await expect(customContract.connect(senderAccounts[0]).join("")).to.emit(customContract, "Join").withArgs(senderAccounts[0].address);
        });
        
        it("Should join after verification ", async function () {
            const { customContract, owner, senderAccounts } = await loadFixture(deployContractWithVerificationFixture);
    
            await expect(customContract.connect(senderAccounts[0]).join("poruka")).to.emit(customContract, "JoinRequest").withArgs(senderAccounts[0].address,"poruka");
            // console.log(await customContract.members(senderAccounts[0].address));
            assert.isFalse( await customContract.members(senderAccounts[0].address));
            assert.isTrue( await customContract.verificationWaitlist(senderAccounts[0].address));

            await expect(customContract.verify(senderAccounts[0].address)).to.emit(customContract, "Join").withArgs(senderAccounts[0].address);

            assert.isTrue( await customContract.members(senderAccounts[0].address));
            assert.isFalse( await customContract.verificationWaitlist(senderAccounts[0].address));
        });
    });


});