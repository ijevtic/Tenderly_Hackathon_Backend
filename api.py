from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from web3 import Web3
import time
import json
import os
from dotenv import load_dotenv
import bson.json_util as json_util
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
api = Api(app)

db = None

def get_organizations(wallet_number):
  organizations = []
  if db.user_organization is None:
    return []
  user_organization_cursor = db.user_organization.find({"wallet_number": wallet_number})
  for user_organization in user_organization_cursor:
    organizations.append(user_organization["organization"])
  
  return organizations

class Object(object):
    pass

class USERS(Resource):

    def get(self):

      parser = reqparse.RequestParser()
      parser.add_argument('wallet_number', type=str)

      wallet_number = parser.parse_args()['wallet_number']
      users = []
      wallet_number = wallet_number.lower()
      db_user_organization = db.user_organization
      if db.users is None:
        return
      
      user = db.users.find_one({"wallet_number":wallet_number})
      if user == None:
        return json_util.dumps({"role": "None"})
      if user["role"] == "user":
        return json_util.dumps({"role": "user", "organizations": get_organizations(wallet_number)})
      if user["role"] == "organization":
        return json_util.dumps({"role": "organization"})
      # for user in user_cursor:
      #   if wallet_number == user["wallet_number"]:
      #     if user["role"] == "user":
      #       get_organizations(wallet_number)

      #   print("user ", user["wallet_number"], user["first_name"], user["last_name"], user["role"])
      #   users.append({"wallet_number": user["wallet_number"], "first_name": user["first_name"],
      #   "last_name": user["last_name"], "role": user["role"]})

      return json_util.dumps(None)

# api.add_resource(APY, '/apy')
api.add_resource(USERS, '/users', endpoint="users")


# provider_url = 'https://kovan.infura.io/v3/75fe0c9d66ad48a7ba1e3c5ca2ac94a9'

# w3 = Web3(Web3.HTTPProvider(provider_url))
# contract_aave = w3.eth.contract(
#     address="0xE0fBa4Fc209b4948668006B2bE61711b7f465bAe", abi=abi_aave)
# contract_main = w3.eth.contract(
#     address="0xb3d646985009Da7229338D027F0b447eC1BE8956", abi=abi_main_contract)


# transaction_filter = contract_main.events.Transaction.createFilter(
#     fromBlock='latest')
# withdraw_filter = contract_main.events.WithdrawInterest.createFilter(
#     fromBlock='latest')


def get_database():
  load_dotenv()
  CONNECTION_STRING = os.getenv('CONNECTION_STRING')
  client = MongoClient(CONNECTION_STRING)
  return client['UserData']


# def get_object(json_object):
#     return {
#         "user": json_object['args']['user'].lower(),
#         "amount": json_object['args']['amount'],
#         "event": json_object['args']['transactionType'],
#         "block_number": json_object['blockNumber'],
#         "oldAmount": json_object['args']['oldAmount'],
#         "newAmount": json_object['args']['newAmount'],
#         "old_c": json_object['args']['old_c'],
#         "new_c": json_object['args']['new_c']
#     }


# def create_transaction_object(jsonEvent, table, type):
#     x = Object()
#     json_object = json.loads(jsonEvent)
#     row = dict()
#     x = dict()
#     print(json_object)
#     if type == "transaction":
#         row = get_object(json_object)
#         x = get_object(json_object)
#     else:
#         row = {"event": "WithdrawInterest",
#                "block_number": json_object['blockNumber']}
#         x = {"event": "WithdrawInterest",
#              "block_number": json_object['blockNumber']}

#     if x["event"] == "Withdraw":
#         base, interest = calculate_base_interest(transactions, x)
#         x["base"] = base
#         x["interest"] = interest
#         row["base"] = base
#         row["interest"] = interest

#     if(x["user"] not in users_transaction_history):
#         users_transaction_history[x["user"]] = []
#     users_transaction_history[x["user"]].append(x)

#     transactions.append(x)

#     table.insert_one(row)


if __name__ == '__main__':
  db = get_database()
  app.run(use_reloader=False)
  
  # apy_table = dbname.apy
  # transactions_table = dbname.transactions
  # apy_cursor = apy_table.find()
  # transactions_cursor = transactions_table.find()

  # for apy in apy_cursor:
  #     array_apy.append({"time": apy["time"], "value": apy["value"]})

  # for t in transactions_cursor:
  #     if t["event"] == "WithdrawInterest":
  #         transactions.append(
  #             {"event": "WithdrawInterest", "block_number": t["block_number"]})
  #     else:
  #         if t["user"] not in users_transaction_history:
  #             users_transaction_history[t["user"]] = []
  #         transaction = {"amount": t["amount"],
  #                        "newAmount": t["newAmount"],
  #                        "oldAmount": t["oldAmount"],
  #                        "event": t["event"], "block_number": t["block_number"], "old_c": t["old_c"], "new_c": t["new_c"]}
  #         if t["event"] == "Withdraw":
  #             transaction["base"] = t["base"]
  #             transaction["interest"] = t["interest"]
  #         users_transaction_history[t["user"]].append(transaction)
  #         transactions.append(transaction)
  # for t in transactions:
  #     print(t["block_number"])
