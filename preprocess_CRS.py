import xarray as xr
import numpy as np
import pandas as pd
import s3fs
import json

# Available columns for FEGS
CRS_columns = ('time', 'gatesp', 'missing', 'range', 'incid', 'lat', 'lon',
                'roll', 'pitch', 'track', 'height', 'head', 'evel', 'nvel',
                'wvel', 'vacft', 'pwr', 'ref', 'dop', 'frequency')

def start(filename="GOESR_CRS_L1B_20170517_v0.nc", coord_type='time', data_type='ref', param="1011.825"):
    """
    Description

    Args:
        filename (string): string filename.nc
        coord_type (string): either time or range
        param (string): string if coord type is date, param has value of range, else if coord type is range, param has value of time.

    Returns:
        processed_data: json with data and their coordinate labels (index)
    """
    request_columns = [data_type, 'time', 'range']
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

    # preprocess the data, into appropriate format.
    processed_data = {} # format in the form of split oriented json of pandas.
    if (coord_type == 'time'):
        # for a given range, time will be the label, and values will be value of 'ref', accross that range
        processed_data = {
            "columns": [data_type],
            "index": DS['time'].values.tolist(),
            "data": DS['ref'].sel(range=param).values.tolist() # accross all the date time, get values of data_type, for a given range
            # "data": json.dumps(DS['ref'].loc["8913001154400":"27323641778400", param].values.tolist())
        }
    elif (coord_type == 'range'):
        # for a given time, range will be the label, and values will be value of 'ref', accross that time
        processed_data = {
            "columns": [data_type],
            "index": DS['range'].values.tolist(),
            "data": DS['ref'].sel(time=param).values.tolist() # accross all the range, get values of data_type, for a given date-time
            # "data": json.dumps(DS['ref'].loc[param, "1011.825":"24995.824"].values.tolist()) 
        }
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
    # validation
    for request_column in set(request_columns):
        if(not request_column in CRS_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)