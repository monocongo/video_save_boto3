# video_utils

## Deploy RESTful API for video clip extraction to MP4 and storage to AWS S3

Login to the Amazon EC2 instance with `ssh` using the appropriate `*.pem` key file 
and public IP address (`52.15.182.126` in this example):
```
$ ssh -i ~/.ssh/aws_keys/james.pem ubuntu@52.15.182.126
```

Update and upgrade Ubuntu packages and install `ffmpeg`:
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install ffmpeg
```

Create an Anaconda environment by downloading the Miniconda package for Linux, 
running the installer, and adding the required modules:
```
$ chmod +x Miniconda3-latest-Linux-x86_64.sh
$ ./Miniconda3-latest-Linux-x86_64.sh
$ rm Miniconda3-latest-Linux-x86_64.sh

(Log out and back in to make the changes take effect)

$ conda config --set auto_activate_base false

(Log out and back in to make the changes take effect)

$ conda create -n mp4_to_s3 python=3.7 boto flask
$ conda activate mp4_to_s3
$ pip install ffmpeg-python
```

Clone this repository. NOTE: This will probably require adding an SSH key to the 
repository for this EC2 instance, described 
[here](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
```
$ mkdir ~/git
$ cd ~/git
$ git clone git@github.com:SecurityCameraWarehouse/video_utils.git
```

Set the `PYTHONPATH` environment variable to the `~/git/video_utils` directory:
```
$ cd ~/git/video_utils
$ export PYTHONPATH=`pwd`
```

Add AWS credentials and configuration information relevant to the S3 bucket(s) 
where we'll be storing the MP4 clips:
```
$ mkdir ~/.aws
$ echo "[default]
> aws_access_key_id = AWS_ACCESS_KEY_ID
> aws_secret_access_key = AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
$ echo "[default]
region=us-east-2" >> ~/.aws/config
```

In order to run the application on port 80 we'll need to run the Flask application 
with `sudo` (this is a current requirement until we can work out how to configure 
security group rules to allow for inbound traffic to port 5000). For this to work
we'll need to set the environment variables `PYTHONPATH`, `AWS_SHARED_CREDENTIALS_FILE`, 
and `AWS_CONFIG_FILE`, as well as specifically referencing the path to the Python 
interpreter of the conda environment. We'll also run the command using `nohup` in 
order to prevent the application from terminating if we log out of the shell, and 
we redirect standard error and output to a log file:
```
$ nohup sudo -HE env PYTHONPATH=$PYTHONPATH AWS_SHARED_CREDENTIALS_FILE=/home/ubuntu/.aws/credentials AWS_CONFIG_FILE=/home/ubuntu/.aws/config /home/ubuntu/miniconda3/envs/mp4_to_s3/bin/python /home/ubuntu/git/video_utils/video_utils/restful_api.py --port 80  2>&1 >> ~/restful_api_mp4_to_s3.log &
```

Now the application should be available via port 80. We can test from another 
(remote) machine for a simple "hello" response as well as the actual/intended usage 
for triggering an MP4 extraction with storage on an S3 bucket which should result 
in the URL to the S3 bucket file for the extracted clip MP4 file: 
```
$ curl http://52.15.182.126/hello
Hello!
$ curl http://52.15.182.126/clip?rtsp=rtsp://user:password@171.185.14.155:554&start=1559077593&duration=10&bucket=scw.james.adams&prefix=test
s3://scw.james.adams/test.clip_b1559077593_e1559077603.mp4
```



## Video clip extraction and storage to AWS S3 buckets using boto3

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
#### Run script
```
$ python save_extract.py --source /home/james/video/big_buck_bunny_720p_2mb.mp4 --dest_s3_bucket elasticbeanstalk-us-east-2-867324276890 --dest_s3_key bunny_clip.mp4 --start 2 --end 7
```
