import json
import boto3
from datetime import datetime, timedelta
import os

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
last_24_hour = datetime.now() - timedelta(hours=24)

def lambda_handler(event, context):
    # 'dev-demo-sketch-out-interim-files' This is the bucket with thousands
    # 'dev-interim-files-test' A test bucket
    interim_bucket =  "prod-demo-sketch-out-interim-files"
    non_consent_bucket = "beta-non-consent-uploads-test"
    consent_bucket = "prod-demo-sketch-out-consents"
    origin_bucket = s3.Bucket(source_bucket)
    page = event
    object_counter = 0
        for obj in page['Contents']:
        object_counter +=1 
        
        # Get the object with the consent_response.txt extension to open
        if obj['Key'].split('/')[-1] == 'consent_response.txt' :
            res = s3.Object(interim_bucket, obj['Key'])
            print(res)
            data = res.get()['Body'].read().decode('utf-8').splitlines()
            
            if data == ['1']:
                copy_source = {
                            'Bucket': source_bucket,
                            'Key': obj['Key']
                        }
                consent_bucket.copy(copy_source, obj['Key'])
                            
                print("Number of objects so far: " + str(object_counter))
        
    print('Done moving subfolders!')
    
# Helper function to call lambda asynchronously     
def invoke_lambda(function_name):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
    )