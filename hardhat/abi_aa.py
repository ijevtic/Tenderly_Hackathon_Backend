import requests
import json
from dotenv import load_dotenv
import os

def get_abi(address):
  # ABI_ENDPOINT = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey=YourApiKeyToken'

  load_dotenv()
  ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
  ABI_ENDPOINT = f'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}'

  response = requests.get(ABI_ENDPOINT)
  response_json = response.json()
  print("---------------------------")
  print(response_json['result'])
  # abi_json = json.loads(response_json['result'])
  return response_json['result']