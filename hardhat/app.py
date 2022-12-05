from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from web3 import Web3
import os
from dotenv import load_dotenv
from flask_cors import CORS
from pymongo import MongoClient
from automate_deploy import compile_and_deploy_contract
from abi_aa import get_abi
import json
import collections.abc
from apscheduler.schedulers.background import BackgroundScheduler
from get_functions import get_organizations, get_all_organizations, get_user, get_org_from_owner, get_pending_for_organization

load_dotenv()

app = Flask(__name__)
CORS(app)
api = Api(app)
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
  row["wallet_number"] = compile_and_deploy_contract(data["name"], data["wallet_number"]).lower()
  row["owner"] = data["wallet_number"].lower()
  row['abi'] = 'not'

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
      if user is not None:
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

      data['wallet_number'] = data['wallet_number'].lower()


      if (get_user(data['wallet_number'],db) is not None) or (get_org_from_owner(data['wallet_number'],db) is not None):
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
      
      print("wallet_number", wallet_number)
      user_organizations = get_organizations(wallet_number,db)
      print("org1",organizations)
      print("org2",user_organizations)
      # if member:
      #   return user_organizations, 200
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
        return {"message": "no such organization"}, 403
      
      users = db.org_pending.find({'organization': wallet_number})
      ret_users = []
      for user in users:
        ret_users.append(user["user"])
      return ret_users, 200




# api.add_resource(APY, '/apy')
api.add_resource(USERS, '/users', endpoint="users")
api.add_resource(ORGANIZATIONS, '/organizations', endpoint="organizations")
api.add_resource(PENDING, '/organizations_pending', endpoint="organizations/pending")

w3 = Web3(Web3.HTTPProvider(os.getenv('GOERLI_RPC_URL')))


def update_pending():
  global w3
  organizations = get_all_organizations(db)
  for org in organizations:
    if 'not' == org["abi"]:
      org["abi"] = get_abi(org["wallet_number"])
      if 'not' in org["abi"]:
        continue
      org["abi"] = json.loads(org["abi"])
      
    contract_main = w3.eth.contract(
      address=Web3.toChecksumAddress(org["wallet_number"]), abi=org["abi"])
    org_filter_leave = contract_main.events.Join.createFilter(
      fromBlock=1)
    org_filter_join = contract_main.events.JoinRequest.createFilter(
      fromBlock=1)
    for row in org_filter_join.get_all_entries():
      print("join")
      if db.org_pending.find_one({"organization" : row["address"].lower(), "user": row["args"]["adr"].lower()}) is None:
        db.org_pending.insert_one({"organization" : row["address"].lower(), "user": row["args"]["adr"].lower()})
    for row in org_filter_leave.get_all_entries():
      print("leave")
      db.org_pending.delete_one({"organization" : row["address"].lower(), "user": row["args"]["adr"].lower()})
      if db.user_organization.find_one({"organization" : row["address"].lower(), "wallet_number":row["args"]["adr"].lower()}) is None:
        db.user_organization.insert_one({"organization" : row["address"].lower(), "wallet_number":row["args"]["adr"].lower()})

    db.organizations.update_one({"wallet_number": org["wallet_number"].lower()}, { "$set": { 'abi': org["abi"] }})

def get_database():
  CONNECTION_STRING = os.getenv('CONNECTION_STRING')
  client = MongoClient(CONNECTION_STRING)
  return client[os.getenv('DATABASE')]


if __name__ == '__main__':
  db = get_database()

  # compile()
  # serve(app, host="0.0.0.0", port=5000)

  scheduler = BackgroundScheduler()
  scheduler.add_job(lambda: update_pending(), trigger="interval", seconds=25)
  scheduler.start()

  app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 5000)))

  # app.run(use_reloader=False)
