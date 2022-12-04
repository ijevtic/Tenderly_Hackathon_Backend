from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from web3 import Web3
import os
from dotenv import load_dotenv
from flask_cors import CORS
from pymongo import MongoClient
from automate_deploy import compile_and_deploy_contract
# from compile_contract import compile

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

def get_all_organizations():
  organizations = []
  if db.organizations is None:
    return []
  organization_cursor = db.organizations.find()
  for organization in organization_cursor:
    organizations.append(organization)
  
  return organizations

def get_user(wallet_number):
  if not db.users:
    return None
  user = db.users.find_one({"wallet_number":wallet_number})
  return user

def get_org_from_owner(owner):
  if not db.organizations:
    return None
  org = db.organizations.find_one({"owner":owner})
  return org

def put_user(data):
  row = dict()
  row["role"] = data["role"]
  row["first_name"] = data["first_name"]
  row["last_name"] = data["last_name"]
  row["wallet_number"] = data["wallet_number"].lower()
  db.users.insert_one(row)
  return {"message": "User succesfully created!"}, 201

def put_organization(data):
  row = dict()
  row["role"] = data["role"]
  row["name"] = data["name"]
  row["wallet_number"] = compile_and_deploy_contract(data["name"], data["wallet_number"])
  row["owner"] = data["wallet_number"].lower()
  
  db.organizations.insert_one(row)
  return {"message": "Organization succesfully created!"}, 201

class Object(object):
    pass

class USERS(Resource):

    def get(self):

      wallet_number = request.args.get('wallet_number').lower()
      
      user = get_user(wallet_number)
      org = get_org_from_owner(wallet_number)
      if user == None and org == None:
        return {"role": "None", "message": "User/Organization doesnt exist!"}, 400
      if user:
        return {"role": "user", "organizations": get_organizations(wallet_number)}, 200
      
      return {"role": "organization"}, 200

    
    def post(self):
      parser = reqparse.RequestParser()
      parser.add_argument('wallet_number', type=str)
      parser.add_argument('role', type=str)
      parser.add_argument('first_name', type=str)
      parser.add_argument('last_name', type=str)
      parser.add_argument('name', type=str)

      data = parser.parse_args()
      # print(data, "data")

      wallet_number = data['wallet_number'].lower()

      if (get_user(wallet_number) is not None) or (get_org_from_owner(wallet_number) is not None):
        return {"message": "User already exists!"}, 400

      role = data['role']
      if role == "user":
        return put_user(data)
      if role == "organization":
        return put_organization(data)
      return {"message": "Wrong role!"}, 400

class ORGANIZATIONS(Resource):
    def get(self):
      if db.users is None:
        return {"message": "db not working yet..."}, 403
      wallet_number = request.args.get('wallet_number').lower()
      member = request.args.get('member')
      if member == 'true':
        member = True
      else:
        member = False
      user = get_user(wallet_number)
      if user is None:
        return {"role": "None", "message": "User doesnt exist!"}, 400
      organizations = get_all_organizations()
      user_organizations = get_organizations(wallet_number)
      open_organizations = []
      for org in organizations:
        if ((not member) and (org["wallet_number"] not in user_organizations)) or \
           (member and (org["wallet_number"] in user_organizations)):
          open_organizations.append({"wallet_number": org["wallet_number"], "name": org["name"]})
      
      return {"organizations": open_organizations}, 200


# api.add_resource(APY, '/apy')
api.add_resource(USERS, '/users', endpoint="users")
api.add_resource(ORGANIZATIONS, '/organizations', endpoint="organizations")

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


if __name__ == '__main__':
  db = get_database()
  # compile()
  # serve(app, host="0.0.0.0", port=5000)
  app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 5000)))

  # app.run(use_reloader=False)
  
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
