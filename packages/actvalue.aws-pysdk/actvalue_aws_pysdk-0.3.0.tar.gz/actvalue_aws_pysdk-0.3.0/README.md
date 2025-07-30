# AWS Python SDK

Simple wrapper for AWS boto3 sdk commonly used functions.

Provide the following environment variables:

- ENV: development | production | ...
- AWSPROFILE: A named profile (non default) in the credential file, e.g.: 'myprofile'
- AWSREGION: A region name, e.g.: 'eu-west-1

AWSPROFILE and AWSREGION are needed in development only, production uses the default session / client configuration.

## Installation

```bash
pip install actvalue.aws-pysdk
```

## Usage

```python
from aws_pysdk import s3_write, s3_read, ssm_load_parameters

# Get Bucket name from ssm parameters
params = [
        {'name': '/app/bucket/name', 'env_var_name': 'MY_BUCKET', 'decrypt': False},
        ]
# Load parameters into environment variables
ssm_load_parameters(params)
# Now you can access it via os.environ
my_bucket = os.environ['MY_BUCKET']

# Write to S3
s3_write(my_bucket, 'hello.txt', 'Hello World', 'text/plain')

# Read from S3
response = s3_read(my_bucket, 'hello.txt')
content = response['Body'].read()

# Get Signed url
params = {
    'Bucket': my_bucket,
    'Key': 'my-file.txt',
    'ContentType': 'text/plain'  # optional
}

# Get a read URL
read_url = s3_get_signed_url(params, 'READ', 3600)  # expires in 1 hour

# Get a write URL
write_url = s3_get_signed_url(params, 'WRITE', 3600)
```

## Develpment and test

### Create and activate virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### Install package in development mode
```bash
pip install -e .
```