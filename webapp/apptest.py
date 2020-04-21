import pytest
import json
from solc import compile_source
from web3 import (
    EthereumTesterProvider,
    Web3,
)


@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


@pytest.fixture
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester


@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)


@pytest.fixture
def foo_contract(eth_tester, w3):
   
    contract_source_code = None
    contract_source_code_file = 'Poll.sol'

    with open(contract_source_code_file, 'r') as file:
        contract_source_code = file.read()

    contract_compiled = compile_source(contract_source_code)
    contract_interface = contract_compiled['<stdin>:Poll']
    CoinFlip = w3.eth.contract(abi=contract_interface['abi'], 
                              bytecode=contract_interface['bin'])

    deploy_address = eth_tester.get_accounts()[0]



    # w3.personal.unlockAccount(w3.eth.accounts[0], '') #  Not needed with Ganache
    tx_hash = CoinFlip.constructor().transact({'from':deploy_address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    # Contract Object
    lottery = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])
    # abi = """[{"anonymous":false,"inputs":[{"indexed":false,"name":"_bar","type":"string"}],"name":"barred","type":"event"},{"constant":false,"inputs":[{"name":"_bar","type":"string"}],"name":"setBar","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"bar","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]"""  # noqa: E501
    # # This bytecode is the output of compiling with
    # # solc version:0.5.3+commit.10d17f24.Emscripten.clang
    # bytecode = """608060405234801561001057600080fd5b506040805190810160405280600b81526020017f68656c6c6f20776f726c640000000000000000000000000000000000000000008152506000908051906020019061005c929190610062565b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b6103bb806101166000396000f3fe608060405234801561001057600080fd5b5060043610610053576000357c01000000000000000000000000000000000000000000000000000000009004806397bc14aa14610058578063febb0f7e14610113575b600080fd5b6101116004803603602081101561006e57600080fd5b810190808035906020019064010000000081111561008b57600080fd5b82018360208201111561009d57600080fd5b803590602001918460018302840111640100000000831117156100bf57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610196565b005b61011b61024c565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561015b578082015181840152602081019050610140565b50505050905090810190601f1680156101885780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b80600090805190602001906101ac9291906102ea565b507f5f71ad82e16f082de5ff496b140e2fbc8621eeb37b36d59b185c3f1364bbd529816040518080602001828103825283818151815260200191508051906020019080838360005b8381101561020f5780820151818401526020810190506101f4565b50505050905090810190601f16801561023c5780820380516001836020036101000a031916815260200191505b509250505060405180910390a150565b60008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102e25780601f106102b7576101008083540402835291602001916102e2565b820191906000526020600020905b8154815290600101906020018083116102c557829003601f168201915b505050505081565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061032b57805160ff1916838001178555610359565b82800160010185558215610359579182015b8281111561035857825182559160200191906001019061033d565b5b509050610366919061036a565b5090565b61038c91905b80821115610388576000816000905550600101610370565b5090565b9056fea165627a7a72305820ae6ca683d45ee8a71bba45caee29e4815147cd308f772c853a20dfe08214dbb50029"""  # noqa: E501

    # Create our contract class.
    # FooContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    # issue a transaction to deploy the contract.
    # tx_hash = FooContract.constructor().transact({
    #     'from': deploy_address,
    # })
    # wait for the transaction to be mined
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    # instantiate and return an instance of our contract.
    return lottery


def test_owner(eth_tester,foo_contract):
    hw = foo_contract.caller.getOwner()
    assert hw == eth_tester.get_accounts()[0]


def test_submit_headline_success(eth_tester, foo_contract,w3):
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[1]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)

    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"

def test_submit_headline_fail_cause_poll_is_ongoing(eth_tester, foo_contract,w3):
    with pytest.raises(Exception) as e_info:
        tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[1]})
        w3.eth.waitForTransactionReceipt(tx_hash, 180)
        tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[1]})
        w3.eth.waitForTransactionReceipt(tx_hash, 180)

        hw = foo_contract.caller.getCurrentHeadline()
        assert hw == "asdasd"

def test_submit_headline_fail_cause_empty_params(eth_tester, foo_contract,w3):
    # print(eth_tester.get_accounts()[1])
    with pytest.raises(Exception) as e_info:
        tx_hash = foo_contract.functions.submitHeadline("","").transact({'from': eth_tester.get_accounts()[1]})
        w3.eth.waitForTransactionReceipt(tx_hash, 180)

def test_submit_headline_and_check_if_total_news_is_incremented(eth_tester, foo_contract,w3):
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[1]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)

    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"
    hw = foo_contract.caller.getTotalNumberOfNews()
    assert hw == 1

def test_successful_vote_with_submitted_headline(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)

    logs = foo_contract.events.Voted.getLogs()
    assert len(logs) == 1
    event = logs[0]
    assert event.blockHash == receipt.blockHash
    assert event.args.voter == eth_tester.get_accounts()[1]
    assert event.args.voted == True


def test_failed_vote_because_poll_is_empty(eth_tester,w3, foo_contract):
    # send transaction that votes
    with pytest.raises(Exception) as e_info: # THIS CHECKS IF CALL FAILS
        tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)


def test_failed_vote_because_value_sent_is_less_than_fees_required(eth_tester,w3, foo_contract):
    with pytest.raises(Exception) as e_info:
        tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
        w3.eth.waitForTransactionReceipt(tx_hash, 180)
        tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(0.001, 'ether')})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)


def test_successful_vote_and_that_voter_is_rewarded_with_vote_balance(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    # print(hw)
    assert hw == 1

    logs = foo_contract.events.Voted.getLogs()
    assert len(logs) == 1
    event = logs[0]
    assert event.blockHash == receipt.blockHash
    assert event.args.voter == eth_tester.get_accounts()[1]
    assert event.args.voted == True


def test_failed_vote_because_msg_value_insufficient(eth_tester,w3, foo_contract):
    with pytest.raises(Exception) as e_info:
        tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
        w3.eth.waitForTransactionReceipt(tx_hash, 180)
        hw = foo_contract.caller.getCurrentHeadline()
        assert hw == "asdasd"


        tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(0.001, 'ether')})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
        hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
        # print(hw)
        assert hw == 0


def test_successful_vote_and_that_publisher_is_rewarded_with_ether(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()

    balance = eth_tester.get_balance(eth_tester.get_accounts()[2])
    assert hw == "asdasd"


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    assert hw == 1

    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[3],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[3]})
    assert hw == 1


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[4],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[4]})
    assert hw == 1

    ## checks if balance is added
    assert balance == (eth_tester.get_balance(eth_tester.get_accounts()[2])-w3.toWei(2,'ether'))



def test_successful_poll_ending_and_that_publisher_is_rewarded_with_ether_because_real_news(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()

    balance = eth_tester.get_balance(eth_tester.get_accounts()[2])
    assert hw == "asdasd"


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    assert hw == 1

    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[3],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[3]})
    assert hw == 1


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[4],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[4]})
    assert hw == 1

    ## checks if balance is added
    assert balance == (eth_tester.get_balance(eth_tester.get_accounts()[2])-w3.toWei(2,'ether'))


def test_successful_poll_ending_and_that_publisher_is_rewarded_with_ether_and_submit_headline_again(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"

    balance = eth_tester.get_balance(eth_tester.get_accounts()[2])



    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    assert hw == 1

    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[3],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[3]})
    assert hw == 1


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[4],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[4]})
    assert hw == 1

    ## checks if balance is added
    assert balance == (eth_tester.get_balance(eth_tester.get_accounts()[2])-w3.toWei(2,'ether'))

    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()

    assert hw == "asdasd"


def test_successful_poll_ending_and_that_publisher_is_NOT_rewarded_because_fake_news(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"

    balance = eth_tester.get_balance(eth_tester.get_accounts()[2])



    tx_hash = foo_contract.functions.Vote(False).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    assert hw == 1

    tx_hash = foo_contract.functions.Vote(False).transact({'from': eth_tester.get_accounts()[3],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[3]})
    assert hw == 1


    tx_hash = foo_contract.functions.Vote(False).transact({'from': eth_tester.get_accounts()[4],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[4]})
    assert hw == 1

    ## checks if balance is added
    assert balance == eth_tester.get_balance(eth_tester.get_accounts()[2])



def test_successful_poll_ending_and_that_publisher_is_rewarded_and_poll_reset_with_empty_headline(eth_tester,w3, foo_contract):
    # send transaction that votes
    tx_hash = foo_contract.functions.submitHeadline("asdasd","asdasd").transact({'from': eth_tester.get_accounts()[2]})
    w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.caller.getCurrentHeadline()
    assert hw == "asdasd"

    balance = eth_tester.get_balance(eth_tester.get_accounts()[2])



    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[1],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[1]})
    assert hw == 1

    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[3],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[3]})
    assert hw == 1


    tx_hash = foo_contract.functions.Vote(True).transact({'from': eth_tester.get_accounts()[4],'value':w3.toWei(1, 'ether')})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    hw = foo_contract.functions.getVoterBalance().call({'from': eth_tester.get_accounts()[4]})
    assert hw == 1

    ## checks if balance is added
    assert balance == (eth_tester.get_balance(eth_tester.get_accounts()[2])-w3.toWei(2,'ether'))

    hw = foo_contract.caller.getCurrentHeadline()

    assert hw == ""

