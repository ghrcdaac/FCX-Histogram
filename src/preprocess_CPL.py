import os
import numpy as np
import json
import s3fs
import h5py
from helpers.pagination import Pagination
from helpers.density_sampling import DensitySampling

# Available columns for FEGS
CPL_columns = ('ATB_1064', 'ATB_1064_PERP', 'ATB_355', 'ATB_532', 'Bin_Alt', 'Bin_Width', 'Cali_1064',
                'Cali_1064_Err', 'Cali_355', 'Cali_355_Err', 'Cali_532', 'Cali_532_Err', 'Date', 'Dec_JDay',
                'Depol_Ratio_1sec', 'End_JDay', 'Frame_Top', 'Hori_Res', 'Hour', 'Latitude', 'Longitude',
                'Minute', 'Mole_Back', 'NumBins', 'NumChans', 'NumRecs', 'NumWave', 'Plane_Alt', 'Plane_Heading',
                'Plane_Pitch', 'Plane_Roll', 'Pressure', 'Project', 'RH', 'Saturate', 'Second', 'Solar_Azimuth_Angle',
                'Solar_Elevation_Angle', 'Start_JDay', 'Temperature')

def start(filename="goesrplt_CPL_ATB_L1B_17930_20170427.hdf5", coord_type="Second", data_type="ATB_1064", params=0, pageno=1, pagesize=50, density=0.05):
    """
    Description

    Args:
        filename (string): string filename.nc
        coord_type (string): Second
        data_type (string): Type of data to be
        param (string): param has the value of the nth second.
                        value of datatype for nth second will be returned.
                        Example: All the values for ATB_1064 will be returned, for the 11th second of the instrument.

    Returns:
        processed_data: json with data and their coordinate labels (index)
    """
    dsamp = DensitySampling(density)

    request_columns=[coord_type, data_type]
    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False

    # use s3fs to mount s3 as fs and load data in xarray
    fs = s3fs.S3FileSystem(anon=False)

    processed_data = {}

    with fs.open(s3path) as cplfile:
        with h5py.File(cplfile, 'r') as DG: # DataGroup
            ATB_X_ds = DG[data_type] # ds: dataset
            total_data = ATB_X_ds.shape[0]
            # page to index conversion
            pg = Pagination(pageno, pagesize, total_data)
            start_index = pg.get_offset()
            end_index = pg.get_offset_end()

            # ATB_X = ATB_X_ds[0:ATB_X_ds.shape[0]] # slicing to get all the data
            ATB_X = ATB_X_ds[start_index:end_index] # slicing to get the data TODO: its a 2d data with shape(x,900). know which data is necessary
            processed_data = {
                "columns": [data_type],
                # "index": list(range(0, ATB_X_ds.shape[1])),
                "index": dsamp.sample_data(list(range(start_index, end_index))),
                # for a specific second, get all the ATB data
                "data": dsamp.sample_data(ATB_X[int(params)].tolist()), # accross a time (sec) received in param, get all the values of the asked data_type
                "pagemeta": pg.get_page_nos()
            }

    # return the processed data for render, in JSON api specification format.
    return json.dumps(processed_data)
    
# helper functions

def get_file_path(filename):
    # bucket_src = "fcx-raw-data-temp"
    bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
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