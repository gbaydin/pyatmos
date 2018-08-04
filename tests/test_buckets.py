'''
Script to test IO with gcs buckets 
python3 please
'''

from google.cloud import storage 
import os

# connect to the google cloud storage client
gcs_storage_client = storage.Client() 
# This command relies on you having the correct permissions setup on the machine you are calling this from. 
# The VM's you create _might_ have this installed already

#############################
# Some basic filesystem operations 
#############################

# List available buckets 
print('Listing available buckets in the Astrobiology 1 project')
for bucket in list(gcs_storage_client.list_buckets()):
    print(' ' + bucket.name)

# Get specific gcs bucket that you want to write to  
bucket_name = 'astrobio' # PLEASE DON't 'astrobio' 
gcs_bucket = gcs_storage_client.get_bucket(bucket_name)

# List files inside bucket  
# commented out because we have A LOT of files in the astrobio bucket and that takes a long time
'''
print('Listing all the files inside the {0} bucket'.format(bucket_name))
file_list = list(gcs_bucket.list_blobs())
print(file_list)
for f in file_list:
    print(' ' + f.name)
'''

#############################
# Create the a new file in the google clout  
#############################
# 1. Can upload strings directly into a new file
# 2. Can upload existing files

# Get new blob object 
new_file_name = 'tempdir/new_file.txt' # notice this *doesn't* start with /astrobio/ 
blob = gcs_bucket.blob(new_file_name)

# Upload a string 
to_write ='this is a \n nice string \n with some text'
print('Uploading a file from a string, which will have the filename {0} on google cloud ... '.format(new_file_name))
blob.upload_from_string(to_write)

# Create a dummy file to upload 
tmp_filename = 'cool_file_name.txt'
tmp_file = open(tmp_filename, 'w')
tmp_file.write('Some awesome information\n')
tmp_file.close()


# Upload a file 
output_blob = gcs_bucket.blob('tempdir/cool_file_name.txt')  # notice this *doesn't* start with /astrobio/, doesn't have to have the same name as tmp_filename 
print('Uploading a file, which will have the filename tempdir/cool_file_name.txt on google cloud')
output_blob.upload_from_filename(tmp_filename) 



#############################
# Download a file 
#############################
filename_that_already_exists_in_the_bucket = 'tempdir/cool_file_name.txt'
filename_to_write_this_file_to = 'downloaded_cool_file_name.txt'

print('Downloading a file called {0} and putting it {1}'.format(filename_that_already_exists_in_the_bucket, filename_to_write_this_file_to))
input_photochem_blob = gcs_bucket.blob(filename_that_already_exists_in_the_bucket)
input_photochem_blob.download_to_filename(filename_to_write_this_file_to)
