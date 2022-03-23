import json
import boto3
from datetime import datetime, timedelta
import os
import time
import io

import base64



startTime = time.time()
print(startTime)

startTime = time.time()
print(startTime)
lambda_client = boto3.client('lambda', region_name='us-east-2')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
last_24_hour = datetime.now() - timedelta(hours=24)
interim_bucket =  "prod-demo-sketch-out-interim-files"
devops_bucket = "ml-devops"
page_list = []
object_list = []
consents_function_arn = os.environ['consents_upload_function_arn']   
page_count = os.environ['page_count']    

# SAVE STARTING TOKEN AS FILE TO S3
def save_starting_token(StartingToken):
    s3.Object(devops_bucket, 'startToken').put(Body=StartingToken)
    print("Save `startToken` in S3")

# GET STARTING TOKEN FROM FILE IN S3
def starting_token_file():
    obj = s3_client.get_object(Bucket=devops_bucket, Key='startToken')
    StartingToken = obj['Body'].read().decode('utf8')
    print("Starting Token From File: {}".format(StartingToken))
    return StartingToken
    
# RETURNS LIST OFF UUIDS BASED OFF OF PAGES SET
def s3_paginator(page_count):
    # Create paginator and store 20 pages in `page_list` list
    StartingToken = starting_token_file()
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=interim_bucket, Delimiter="consent_response.txt", PaginationConfig={'StartingToken': StartingToken}) 
    
    counter = 0
    for page in pages:
        if not page or 'Contents' not in page :
            return
        if counter == int(page_count):
            break
        counter +=1
        page_list.append(page)
    for contents in page_list:
        for key in contents['Contents']:
            object_list.append(key['Key'])
    objects = [obj.split('/')[:1] for obj in object_list]
    key_list = [item for sublist in objects for item in sublist]
    UUIDS = list(set(key_list))
    print("Proccessed {} UUIDS".format(len(UUIDS)))
    return UUIDS
        
# PULLS THE MOST RECENT TOKEN FROM S3
def get_most_recent_token_from_s3():
    # Create paginator and store 20 pages in `page_list` list
    #StartingToken = get_start_token()
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=interim_bucket, Delimiter="consent_response.txt", PaginationConfig={'MaxItems': 1000})
    
    counter = 0
    for page in pages:
        if not page or 'Contents' not in page :
            return
        if counter > 2:
            break
        counter +=1
        if not page or 'Contents' not in page :
            return
        page_list.append(page)
        for contents in page_list:
            for key in contents['Contents']:
                key_list.append(key['Key'])
    return page_list[-1]['NextContinuationToken']

def lambda_handler(event, context):
    # GET UUIDS AS LIST
    UUIDS = s3_paginator(page_count)
    print("\n")
    print("{} PAGES FROM S3 DOWNLOADED".format(len(page_list))) 
    print("\n")
    print("{} UUIDS COLLECTED".format(len(UUIDS)))
    print("\n")
    print("INVOKING {} LAMBDAS".format(len(UUIDS)))
    print("\n")
    # save uuuid
    for uuid in UUIDS:
        payload = json.dumps({"UUID":uuid})
        response = lambda_client.invoke(FunctionName=consents_function_arn,InvocationType='Event',Payload=payload)
        print("UUID %s passed as event with %s status code" % (uuid, response['StatusCode']))
    # SAVE `NextContinuationToken` TO S3
    NextContinuationToken = page_list[-1]['NextContinuationToken']
    save_starting_token(NextContinuationToken)
    print("\n")
    print("SAVED TOKEN: {}".format(NextContinuationToken))
    print("\n")
    print("{} UUIDS COLLECTED".format(len(UUIDS)))


def invoke_lambda(function_name):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
    )


