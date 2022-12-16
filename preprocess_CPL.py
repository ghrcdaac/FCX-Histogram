import xarray as xr
import numpy as np
import pandas as pd
import s3fs
import json

# Available columns for FEGS
CPL_columns = ('ATB_1064', 'ATB_1064_PERP', 'ATB_355', 'ATB_532', 'Bin_Alt', 'Bin_Width', 'Cali_1064',
                'Cali_1064_Err', 'Cali_355', 'Cali_355_Err', 'Cali_532', 'Cali_532_Err', 'Date', 'Dec_JDay',
                'Depol_Ratio_1sec', 'End_JDay', 'Frame_Top', 'Hori_Res', 'Hour', 'Latitude', 'Longitude',
                'Minute', 'Mole_Back', 'NumBins', 'NumChans', 'NumRecs', 'NumWave', 'Plane_Alt', 'Plane_Heading',
                'Plane_Pitch', 'Plane_Roll', 'Pressure', 'Project', 'RH', 'Saturate', 'Second', 'Solar_Azimuth_Angle',
                'Solar_Elevation_Angle', 'Start_JDay', 'Temperature')

def start(filename="goesrplt_CPL_ATB_L1B_17930_20170427.hdf5", request_columns=['ATB_1064', 'ATB_1064_PERP', 'ATB_355', 'ATB_532']):
    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False
    
    # use s3fs to mount s3 as fs and load data in xarray
    fs = s3fs.S3FileSystem(anon=False)

    print(s3path)
    # before loading, seperate out the columns that is not necessary
    nonRequestColumns = np.setdiff1d(CPL_columns, request_columns)
    with fs.open(s3path) as cplfile:
        # if okay, proceed to the necessary data
        DS = xr.open_dataset(cplfile, engine="h5netcdf", drop_variables=nonRequestColumns) # need to install scipy, a xr dependency to open crs file.
    print(DS)

    # preprocess the data, into appropriate format.
    DF = DS.to_dataframe()
    print(DF)
    processed_data = DF
    # processed_data = DF.to_json(orient='split', index=False)
    # return the processed data for render, in JSON api specification format.
    return processed_data
    
# helper functions

def get_file_path(filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    path_to_file="CPL/data/L1B"
    # path_to_file = os.environ.get('PATH_TO_FEGS')
    return f"s3://{bucket_src}/{path_to_file}/{filename}"

def validate(request_columns): 
    # validation
    for request_column in set(request_columns):
        if(not request_column in CPL_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)