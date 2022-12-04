def get_organizations(wallet_number, db):
  organizations = []
  if db.user_organization is None:
    return []
  user_organization_cursor = db.user_organization.find({"wallet_number": wallet_number})
  for user_organization in user_organization_cursor:
    organizations.append(user_organization["organization"])
  
  return organizations

def get_all_organizations(db):
  organizations = []
  if db.organizations is None:
    return []
  organization_cursor = db.organizations.find()
  for organization in organization_cursor:
    organizations.append(organization)
  
  return organizations

def get_user(wallet_number,db):
  if not db.users:
    return None
  user = db.users.find_one({"wallet_number":wallet_number})
  return user

def get_org_from_owner(owner,db):
  if not db.organizations:
    return None
  org = db.organizations.find_one({"owner":owner})
  return org

def get_pending_for_organization(wallet_number,db):
  users = []
  if not db.org_pending:
    return []
  users_cursor = db.org_pending.find({"organization": wallet_number})
  for user in users_cursor:
    users.append({"first_name":user["first_name"],"last_name":user["last_name"], "wallet_number":user["wallet_number"]})
  return users