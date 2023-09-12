import os
import xarray as xr
import numpy as np
import pandas as pd
import s3fs
import json

# Available columns for FEGS
CRS_columns = ('time', 'gatesp', 'missing', 'range', 'incid', 'lat', 'lon',
                'roll', 'pitch', 'track', 'height', 'head', 'evel', 'nvel',
                'wvel', 'vacft', 'pwr', 'ref', 'dop', 'frequency')

def start(filename="GOESR_CRS_L1B_20170517_v0.nc", coord_type='range'):
    """
    Description
    get coordinate values in CRS. Needed to index out a point in 3d coordinate to get a 2d dataset, for histogram visualization

    Args:
        filename (string): string filename.nc
        coord_type (string): coodinate name to get the value of.

    Returns:
        coordinate_value: array with coordinate data
    """
    
    request_columns = [coord_type]
    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False
    
    # use s3fs to mount s3 as fs and load data in xarray
    fs = s3fs.S3FileSystem(anon=False)

    # before loading, seperate out the columns that is not necessary
    nonRequestColumns = np.setdiff1d(CRS_columns, request_columns)
    with fs.open(s3path) as crsfile:
        # if okay, proceed to the necessary data
        DS = xr.open_dataset(crsfile, engine="scipy", drop_variables=nonRequestColumns) # need to install scipy, a xr dependency to open crs file.
        processed_data = {
            "coordinate_value": DS[coord_type].values.tolist()
        }
    # return the processed data for render, in JSON api specification format.
    return json.dumps(processed_data)
    
# helper functions

def get_file_path(filename):
    # bucket_src = "fcx-raw-data-temp"
    bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    path_to_file="CRS/data"
    # path_to_file = os.environ.get('PATH_TO_FEGS')
    return f"s3://{bucket_src}/{path_to_file}/{filename}"

def validate(request_columns): 
    # validation
    for request_column in set(request_columns):
        if(not request_column in CRS_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)