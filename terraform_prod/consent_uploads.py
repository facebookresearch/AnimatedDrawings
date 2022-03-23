import json
import boto3
from datetime import datetime, timedelta
import os
import time

startTime = time.time()
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
last_24_hour = datetime.now() - timedelta(hours=24)
interim_bucket =  "prod-demo-sketch-out-interim-files"
consent_bucket_destination = s3.Bucket("prod-demo-sketch-out-consents")
non_consent_bucket_destination = s3.Bucket("prod-non-consent-uploads")
uuid_bucket = s3.Bucket(interim_bucket)
def lambda_handler(event, context):

    lambda_function_time = time.time()
    uuid = event['UUID']
    uuid_objects = [obj.key for obj in uuid_bucket.objects.filter(Prefix=uuid)]   
    
    consent_file = uuid +'/consent_response.txt'
    #consent_file = uuid.split('/')[0]+'/consent_response.txt'
    if consent_file in uuid_objects:
        print("Consent File: {}".format(consent_file))
        consent_object = s3.Object(interim_bucket, consent_file)
        consent_data = consent_object.get()['Body'].read().decode('utf-8').splitlines()
        if consent_data == ['1']:
            for obj in uuid_objects:
                print("CONSENTED DATA, MOVING FILE: {} TO CONSENT BUCKET: {}".format(obj, "prod-demo-sketch-out-consents"))
                copy_data = {'Bucket': interim_bucket,
                                'Key': obj}
                consent_bucket_destination.copy(copy_data, obj)
                # Delete the obj after copying
                s3.Object(interim_bucket, obj).delete()
        else:
            for obj in uuid_objects:
                print("NOT CONSENTED DATA, MOVING FILE: {} TO NONCONSENT BUCKET: {} FOR DELETION".format(obj, "beta-non-consent-uploads-test"))
                copy_data = {'Bucket': interim_bucket,
                                    'Key': obj}
                non_consent_bucket_destination.copy(copy_data, obj)
                # Delete the obj after copying
                s3.Object(interim_bucket, obj).delete()
    else:
        # MOVE TO NONCONSENT
        for obj in uuid_objects:
                print("NOT CONSENTED DATA, MOVING FILE: {} TO NONCONSENT BUCKET: {} FOR DELETION".format(obj, "beta-non-consent-uploads-test"))
                copy_data = {'Bucket': interim_bucket,
                                    'Key': obj}
                non_consent_bucket_destination.copy(copy_data, obj)
                # Delete the obj after copying
                s3.Object(interim_bucket, obj).delete()
        pass


    print("PROCESSED UUID: {}".format(uuid))
    
    # EXECUTION TIME
    print("LAMBDA INVOKATION COMPLETED IN: %s seconds ---" % (time.time() - lambda_function_time))
            
# Helper function to call lambda asynchronously     
def invoke_lambda(function_name):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
    )