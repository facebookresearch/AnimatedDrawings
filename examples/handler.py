from flask import Flask
import boto3
from botocore.exceptions import NoCredentialsError
from image_to_animation import image_to_animation
import threading

app = Flask(__name__)
sqs = boto3.resource('sqs', region_name='ap-northeast-1')
queue = sqs.get_queue_by_name(QueueName='dev-60yfmd-handler-sqs.fifo')

@app.route('/')
def poll_messages():
    """
    response = client.receive_message(
        QueueUrl='string',
        AttributeNames=[
            'All'|'Policy'|'VisibilityTimeout'|'MaximumMessageSize'|'MessageRetentionPeriod'|'ApproximateNumberOfMessages'|'ApproximateNumberOfMessagesNotVisible'|'CreatedTimestamp'|'LastModifiedTimestamp'|'QueueArn'|'ApproximateNumberOfMessagesDelayed'|'DelaySeconds'|'ReceiveMessageWaitTimeSeconds'|'RedrivePolicy'|'FifoQueue'|'ContentBasedDeduplication'|'KmsMasterKeyId'|'KmsDataKeyReusePeriodSeconds'|'DeduplicationScope'|'FifoThroughputLimit'|'RedriveAllowPolicy'|'SqsManagedSseEnabled',
        ],
        MessageAttributeNames=[
            'string',
        ],
        MaxNumberOfMessages=123,
        VisibilityTimeout=123,
        WaitTimeSeconds=123,
        ReceiveRequestAttemptId='string'
    )
    """
    while True:
        try:
            # receive message from SQS queue
            message = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=5)
            if message:
                # process the message
                # ...
                logger.info(message[0].body)

                # process the message and get the image URL from message body
                image_url = message[0].body

                # get the image from S3
                s3 = boto3.client('s3', region_name='ap-northeast-1')
                bucket_name = 'dev-60yfmd-input-drawings-bucket'
                key = image_url.split('/')[-1] # assume image URL is in the format of s3://bucket-name/image-file-name.jpg
                response = s3.get_object(Bucket=bucket_name, Key=key)
                image_content = response['Body'].read()

                # delete the message from queue
                # sqs.delete_message(
                #     QueueUrl=queue_url,
                #     ReceiptHandle=message['ReceiptHandle']
                # )
                message[0].delete()

        except NoCredentialsError:
            print('Credentials not available')

        return 'Received message successfully'

# 画像を受信して処理する関数
def process_image():
    image_content = receive_message()
    # do something with the image content
    # ...

# SQSメッセージのポーリングを開始
polling_thread = threading.Thread(target=poll_messages)
polling_thread.start()

if __name__ == '__main__':
    # app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
