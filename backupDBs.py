import boto3
import shutil

from botocore.config import Config
from datetime import datetime


class S3Worker():
    def __init__(self, access_key_id, secret_key, default_bucket):
        self.client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_key,
                                   config=Config(signature_version='s3v4'))
        self.resource = boto3.resource('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_key,
                                       config=Config(signature_version='s3v4'))
        self.default_bucket_name = default_bucket
        self.default_bucket = self.resource.Bucket(default_bucket)

    def saveAsArchive(self, fromPath, toPath, name, format="zip"):
        shutil.make_archive(base_name=fromPath, format=format, root_dir=fromPath)
        with open(fromPath + "." + format, 'rb') as data:
            self.client.upload_fileobj(data, self.default_bucket_name, toPath + "/" + name)

    def downloadArchive(self, fromPath, toPath, name, format="zip"):
        archive_name = name + "." + format
        with open(archive_name, 'wb') as data:
            self.default_bucket.download_fileobj(fromPath, data)
        shutil.unpack_archive(filename=archive_name, format=format, extract_dir=toPath)

if __name__ == '__main__':
    s3 = S3Worker('AKIAI24V3VGEAEFSBPGQ', '3UkkuN0ccrNIVqaiMS2MDaqN/2GB2mW5TFZEmRCe', 'socialgraph.data')

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # s3.saveAsArchive("redis", "redis")
    # s3.downloadArchive("redis/redis", "./redis", "redis" + now)
