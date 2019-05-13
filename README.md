# video_save_boto3
Video clip extraction and storage to AWS S3 buckets using boto3

#### Configure user for AWS S3 access
Create a credentials file, `~/.aws/credentials`, with the user's access key ID 
and secret access key, and a confguration file, `~/.aws/config`, containing the 
default region.

```
$ cat ~/.aws/credentials
[default]
aws_access_key_id = SOMEACCESSKEYIDOTHERTHANTHIS
aws_secret_access_key = SECRETACCESSKEYFORTHEUSER

$ cat ~/.aws/config 
[default]
region=us-east-3

```

#### Find an existing S3 bucket
```
$ python
>>> import boto3
>>> s3 = boto3.client('s3')
>>> response = s3.list_buckets()
>>> s3 = boto3.client('s3')
>>> response = s3.list_buckets()
>>> for bucket in response['Buckets']:
...     print(f'  {bucket["Name"]}')
... 
  elasticbeanstalk-us-east-2-867324276890
>>>
```
