import subprocess
import time

def compile_and_deploy_contract(contract_name, contract_owner):
  f = open("deploy/args.js", "a")
  f.truncate(0)
  f.write("module.exports = [\n")
  f.write('"' + contract_name + '",\n')
  f.write('"' + contract_owner + '",\n')
  f.write("false,\n")
  f.write("]")
  f.close()


  cmd = ['ls']
  output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
  print(output)

  # cmd = ['npm', 'install', '--save-dev', 'hardhat']
  # output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
  # print(output)
  cmd = [ 'npx', 'hardhat', 'compile' ]
  output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
  print(output)
  cmd = ['npx', 'hardhat', 'run', 'deploy/deploy.js', '--network', 'goerli']
  output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
  output = str(output)
  ind = output.rstrip().rindex('0x')
  address = output[ind:-3]
  print("-----",address,"-----", output, "----")

  time.sleep(10)

  cmd = ['npx', 'hardhat', 'verify', '--network', 'goerli', '--constructor-args', 'deploy/args.js', address]
  output = subprocess.Popen( cmd, stdout=subprocess.PIPE ).communicate()[0]
  return address