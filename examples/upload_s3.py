import boto3
from pathlib import Path
import logging
import sys
import datetime
boto3.set_stream_logger()

def upload_s3(char_dir: str):
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    target_dir = str(Path(char_dir, 'video.gif').resolve())

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = 'image_{}.gif'.format(timestamp)
    logging.info(file_name)

    s3.upload_file(target_dir, 'dev-60yfmd-input-drawings-bucket', file_name)

if __name__ == '__main__':
    upload_s3(sys.argv[1])