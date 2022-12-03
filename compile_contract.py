# import json
# from solcx import compile_standard, install_solc
# from deployment import deploy

# def compile():

#   install_solc("0.8.0")

#   contact_list_file = None
#   with open("proba.sol", "r") as file:
#     contact_list_file = file.read()
  
#   compiled_sol = compile_standard(
#     {
#         "language": "Solidity",
#         "sources": {"ContactList.sol": {"content": contact_list_file}},
#         "settings": {
#             "outputSelection": {
#                 "*": {
#                     "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
#                 }
#             }
#         },
#     },
#     solc_version="0.8.0",
#   )
#   # print(compiled_sol)
#   with open("compiled_code.json", "w") as file:
#     json.dump(compiled_sol, file)
  
#   # get bytecode
#   bytecode = compiled_sol["contracts"]["ContactList.sol"]["ContactList"]["evm"]["bytecode"]["object"]# get abi
#   abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["ContactList"]["metadata"])["output"]["abi"]
#   deploy(abi, bytecode)
