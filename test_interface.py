import json
import boto3
import psycopg2

if __name__ ==  "__main__":
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)

    # access the correct bucket
    # log chat from single user for now
