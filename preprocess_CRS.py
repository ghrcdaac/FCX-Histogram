import pandas as pd
import xarray as xr
import s3fs
import json

def start(filename="GOESR_CRS_L1B_20170517_v0.nc", request_columns=['ref']):
    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False
    
    # use s3fs to mount s3 as fs and load data in xarray
    fs = s3fs.S3FileSystem(anon=False)

    with fs.open(s3path) as crsfile:
        # if okay, proceed to the necessary data
        DS = xr.open_dataset(crsfile, engine="scipy") # need to install scipy, a xr dependency to open crs file.
    print(DS)

    # preprocess the data, into appropriate format.
    processed_data = {}
    # return the processed data for render, in JSON api specification format.
    return json.dumps(processed_data)
    
# helper functions

def get_file_path(filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    path_to_file="CRS/data"
    # path_to_file = os.environ.get('PATH_TO_FEGS')
    return f"s3://{bucket_src}/{path_to_file}/{filename}"

def validate(request_columns):
    # Available columns for FEGS
    CRS_columns = ('ref')
    
    # validation
    for request_column in set(request_columns):
        if(not request_column in CRS_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)