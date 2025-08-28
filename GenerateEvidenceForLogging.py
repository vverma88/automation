# Script to verify whether AWS CloudTrail is enabled in the AWS account and log retention is for 365 days.
# Output: List of dictionaries with name of AWS CloudTrail, CloudTrail Logging Start Time, CloudTrail Logging Stop time
# and retention period

import boto3
from pprint import pprint

cloud_trail_details = []

session = boto3.Session(profile_name="default")

cloudtrail_client = boto3.client('cloudtrail')

# get list of trails in an account. We will pull the trail arns from the response to this call.
list_of_trails = cloudtrail_client.list_trails()['Trails']

list_of_trail_arns = []

for trail in list_of_trails:
    trail_arn = trail['TrailARN']
    list_of_trail_arns.append(trail_arn)

# List to pull initial details about CloudTrails in account
trails_in_account_with_details = []

# List which contains all relevant details about CloudTrails including whether logging is enabled,
# logging start time, logging stop time. The data in this list can be shared with auditors to demonstrate whether
# logging is enabled in the account, logging start time, logging stop time etc.
cloud_trail_details = []

# use get_trail() function. We do not use describe_trail() as it only returns details about trails in the current
# region. While get_trail() returns details about all trails for which the arn is provided
for trail_arn in list_of_trail_arns:
    trail_details = cloudtrail_client.get_trail(Name = trail_arn)['Trail']
    trails_in_account_with_details.append(trail_details)

print("Details for CloudTrails provided by get_trail() : ")
pprint(trails_in_account_with_details)

#Pulling only relevant details that we need to demonstrate that logging is enabled in the account
for trail in trails_in_account_with_details:
    trail_name = trail['Name']
    trail_arn = trail['TrailARN']
    trail_home_region = trail['HomeRegion']
    if 'CloudWatchLogsLogGroupArn' in trail:
        trails_cloudwatch_log_group_arn = trail['CloudWatchLogsLogGroupArn']
    else:
        trails_cloudwatch_log_group_arn = None

    cloud_trail_details.append({'trail_name': trail_name, 'trail_arn': trail_arn, 'trail_home_region': trail_home_region,
                                    'trail_cloudwatch_log_group_arn': trails_cloudwatch_log_group_arn})


# call get_trail_status() to get information about status of logging via CloudTrail. To get trail status
# from all regions, get_trail_status() has to be called for each region. We only call get_trail_status()
# for regions that are "Home_Region" for cloud trails in the account.
for trail in cloud_trail_details:
    trail_home_region = trail['trail_home_region']
    cloudtrail_regional_client = session.client('cloudtrail', region_name=trail_home_region)
    trail_status = cloudtrail_regional_client.get_trail_status(Name = trail['trail_name'])
    is_logging = trail_status['IsLogging']
    if 'StartLoggingTime' in trail_status:
        logging_start_time = trail_status['StartLoggingTime']
    else:
        logging_start_time = None
    if 'StopLoggingTime' in trail_status:
        logging_stopped_time = trail_status['StopLoggingTime']
    else:
        logging_stopped_time = None
    index = cloud_trail_details.index(trail)
    enhanced_cloud_trail_details = {'trail_name': trail['trail_name'], 'trail_arn': trail['trail_arn'],
                                    'trail_home_region': trail['trail_home_region'],
                                    'trail_cloudwatch_log_group_arn': trail['trail_cloudwatch_log_group_arn'],
                                    'is_logging_enabled': is_logging, 'logging_start_time': logging_start_time,
                                    'logging_stopped_time': logging_stopped_time}
    cloud_trail_details[index] = enhanced_cloud_trail_details

print("Details about trails in account WITH logging flag and logging start/stop time: ")
pprint(cloud_trail_details)