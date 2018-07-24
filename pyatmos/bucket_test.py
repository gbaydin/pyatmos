'''
Script to test IO with gcs buckets 
'''

from google.cloud import storage 


def main():

    # list available buckets 
    gcs_storage_client = storage.Client()
    for bucket in list(gcs_storage_client.list_buckets()):
        print(' ' + bucket.name)

    # get specific gcs bucket 
    bucket_name = 'astrobio'
    gcs_bucket = gcs_storage_client.get_bucket(bucket_name)

    # list files inside bucket  
    file_list = list(gcs_bucket.list_blobs())
    print(file_list)
    for f in file_list:
        print(' ' + f.name)

    # get new blob object 
    blob = gcs_bucket.blob('new_file.txt')
    print(blob)

    # load a new file into the blob 
    '''
    blob.upload_from_file(
            '/home/willfaw/pyatmos/pyatmos/test_file.txt'
            ) 
    '''

    # string to wrte
    to_write ='this is a \n nice string \n with some text'
    blob.upload_from_string(to_write)

    # create a new file 




    

if __name__ == "__main__":
    main()
