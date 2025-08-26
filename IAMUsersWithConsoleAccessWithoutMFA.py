# This script creates a list a IAM users with AWS Management Console access and not having MFA enabled.

import boto3
from pprint import pprint

users_with_console_access_no_mfa = []
iam_users_list_with_user_details = []

# get login profile for each user. If there is a "NoSuchEntityException" then user DOES NOT have console access
# and thus DOES NOT have MFA enabled
def does_user_have_console_access(user):
    try:
        iam_client.get_login_profile(UserName = user['UserName'])
        user ['has_console_access'] = True
    except iam_client.exceptions.NoSuchEntityException:
        pprint(f'User {user["UserName"]} DOES NOT have console access.')
        user ['has_console_access'] = False
        user ['has_mfa_enabled'] = False
    return user


iam_client = boto3.client('iam')
iam_users_list = iam_client.list_users()

# Get list of IAM users in the account, create a new list of users with details including username, user id, whether
# user has console access, and whether user has mfa enabled

for iam_user in iam_users_list['Users']:
    iam_user = does_user_have_console_access(iam_user)
    if 'has_mfa_enabled' in iam_user:
        iam_users_list_with_user_details.append({'iam_username': iam_user['UserName'], 'iam_userid': iam_user['UserId'],
                                                 'has_console_access': iam_user['has_console_access'],
                                                 'has_mfa_enabled': iam_user['has_mfa_enabled']})
    else:
        iam_users_list_with_user_details.append({'iam_username': iam_user['UserName'], 'iam_userid': iam_user['UserId'],
                                                 'has_console_access': iam_user['has_console_access']})

# For users with console access, call list_mfa_devices to check if MFA is enabled. If MFA device in response is empty
# then user does not have MFA enabled
for iam_user in iam_users_list_with_user_details:
    if iam_user['has_console_access']:
        mfa_devices = iam_client.list_mfa_devices(UserName = iam_user['iam_username'])
        if len(mfa_devices['MFADevices']) > 0:
            iam_user ['has_MFA_enabled'] = True
        else:
            iam_user ['has_MFA_enabled'] = False

# create list of users with console access and MFA not enabled
for iam_user in iam_users_list_with_user_details:
    if iam_user['has_console_access'] == True and iam_user['has_MFA_enabled'] == False:
        users_with_console_access_no_mfa.append(iam_user)

# print list of users with console access and MFA not enabled
print("List of users with console access AND no MFA")
pprint(users_with_console_access_no_mfa)







