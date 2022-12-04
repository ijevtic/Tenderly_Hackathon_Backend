from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from web3 import Web3
import os
from dotenv import load_dotenv
from flask_cors import CORS
from pymongo import MongoClient
from automate_deploy import compile_and_deploy_contract
from abi_aa import get_abi
import json
from apscheduler.schedulers.background import BackgroundScheduler
from get_functions import get_organizations, get_all_organizations, get_user, get_org_from_owner, get_pending_for_organization

# from compile_contract import compile

load_dotenv()

app = Flask(__name__)
CORS(app)
api = Api(app)
pending_org_mapping = dict()
pending_filters = dict()

db = None

def make_event_filter():
  pass

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
  row['abi'] = 'not'
  # abi = get_abi(data["wallet_number"])
  # if 'not' in abi:
    # row["abi"] = abi
  # else:
    # row["abi"] = json.loads(abi)
  db.organizations.insert_one(row)
  return {"message": "Organization succesfully created!"}, 201

class Object(object):
    pass

class USERS(Resource):

    def get(self):

      wallet_number = request.args.get('wallet_number').lower()
      
      user = get_user(wallet_number, db)
      org = get_org_from_owner(wallet_number,db)
      if user == None and org == None:
        return {"role": "None", "message": "User/Organization doesnt exist!"}, 400
      if user:
        return {"role": "user", "organizations": get_organizations(wallet_number, db)}, 200
      
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

      if (get_user(wallet_number,db) is not None) or (get_org_from_owner(wallet_number,db) is not None):
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
      user = get_user(wallet_number,db)
      if user is None:
        return {"role": "None", "message": "User doesnt exist!"}, 400
      organizations = get_all_organizations(db)
      user_organizations = get_organizations(wallet_number,db)
      open_organizations = []
      for org in organizations:
        if ((not member) and (org["wallet_number"] not in user_organizations)) or \
           (member and (org["wallet_number"] in user_organizations)):
          open_organizations.append({"wallet_number": org["wallet_number"], "name": org["name"]})
      
      return {"organizations": open_organizations}, 200

class PENDING(Resource):
    def get(self):
      owner = request.args.get('wallet_number').lower()

      wallet_number = get_org_from_owner(owner,db)
      if wallet_number is None:
        return {"message", "no such organization"}, 403
      
      users = get_pending_for_organization(wallet_number,db)
      return users, 200



# api.add_resource(APY, '/apy')
api.add_resource(USERS, '/users', endpoint="users")
api.add_resource(ORGANIZATIONS, '/organizations', endpoint="organizations")
api.add_resource(PENDING, '/organizations/pending', endpoint="organizations/pending")

w3 = Web3(Web3.HTTPProvider(os.getenv('GOERLI_RPC_URL')))


def update_pending():
  global w3
  organizations = get_all_organizations(db)
  for org in organizations:
    if 'not' in org["abi"]:
      org["abi"] = get_abi(org["wallet_number"])
      if 'not' in org["abi"]:
        continue
      org["abi"] = json.loads(org["abi"])
    contract_main = w3.eth.contract(
      address=org["wallet_number"], abi=org["abi"])
    org_filter_leave = contract_main.events.Join.createFilter(
      fromBlock='latest')
    org_filter_join = contract_main.events.JoinRequest.createFilter(
      fromBlock='latest')
    for row in org_filter_join.get_all_entries():
      print(row, "join")
    for row in org_filter_leave.get_all_entries():
      print(row, "leave")
    db.organizations.update_one({"wallet_number": org["wallet_number"]}, { "$set": { 'abi': org["abi"] }})

def restore_pending():
  global pending_org_mapping
  if db.org_pending is None:
    return
  pending_users_cursor = db.org_pending.find()
  for pending_user in pending_users_cursor:
    pending_org_mapping[pending_user["organization"]].append(pending_user["user"])


def get_database():
  CONNECTION_STRING = os.getenv('CONNECTION_STRING')
  client = MongoClient(CONNECTION_STRING)
  return client['UserData']


if __name__ == '__main__':
  db = get_database()

  restore_pending()


  # compile()
  # serve(app, host="0.0.0.0", port=5000)

  scheduler = BackgroundScheduler()
  scheduler.add_job(lambda: update_pending(), trigger="interval", seconds=15)
  scheduler.start()

  app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 5000)))

  # app.run(use_reloader=False)
