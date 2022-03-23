import boto3   


def delete_objects(event, context):
    s3 = boto3.resource('s3')
    non_consent_bucket = s3.Bucket('prod-non-consent-uploads')
    non_consent_bucket.objects.all().delete()

    response = {
        'statusCode': 200,
    }

    return response