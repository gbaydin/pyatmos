'''
Script to test IO with gcs buckets 
'''

from google.cloud import storage 

gcs_storage_client = storage.Client()

# get specific gcs bucket 
bucket_name = 'astrobio'
gcs_bucket = gcs_storage_client.get_bucket(bucket_name)

# get new blob object 
blob = gcs_bucket.blob('tempdir/new_file_will2.txt')
print(blob)

# string to wrte
to_write ='this is a \n nice string \n with some text'
blob.upload_from_string(to_write)
