# Databricks notebook source
import os
import json
import tempfile
import boto3
 
bucket = os.environ.get("BUCKET")
original_breadcrumb = 'landing/isin_msid_mapping/landing/'
new_breadcrumb = 'landing/isin_msid_mapping/'
path = 's3a://'+bucket+'/'+original_breadcrumb
filename = 'isin_msid_mapping.csv'
news3key = new_breadcrumb+filename
client = boto3.client('s3')
s3 = boto3.resource('s3')
Bucket = s3.Bucket(bucket)
 
df = spark.sql("select * from general.asset_isin_msid_mapping") 
df.coalesce(1).write.mode('overwrite').format('csv').option("Header",True).save(path)

for obj in Bucket.objects.filter(Prefix=original_breadcrumb):
    if obj.key.endswith('.csv'):
        s3key = obj.key
        
s3.Object(bucket,news3key).copy_from(CopySource={'Bucket':bucket,'Key':s3key})
# s3.Object(bucket,s3key).delete()
Bucket.objects.filter(Prefix=original_breadcrumb).delete()