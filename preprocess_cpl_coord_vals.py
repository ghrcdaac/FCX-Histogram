import os
import numpy as np
import json
import s3fs
import h5py

# Available columns for FEGS
CPL_columns = ('ATB_1064', 'ATB_1064_PERP', 'ATB_355', 'ATB_532', 'Bin_Alt', 'Bin_Width', 'Cali_1064',
                'Cali_1064_Err', 'Cali_355', 'Cali_355_Err', 'Cali_532', 'Cali_532_Err', 'Date', 'Dec_JDay',
                'Depol_Ratio_1sec', 'End_JDay', 'Frame_Top', 'Hori_Res', 'Hour', 'Latitude', 'Longitude',
                'Minute', 'Mole_Back', 'NumBins', 'NumChans', 'NumRecs', 'NumWave', 'Plane_Alt', 'Plane_Heading',
                'Plane_Pitch', 'Plane_Roll', 'Pressure', 'Project', 'RH', 'Saturate', 'Second', 'Solar_Azimuth_Angle',
                'Solar_Elevation_Angle', 'Start_JDay', 'Temperature')

def start(filename="goesrplt_CPL_ATB_L1B_17930_20170427.hdf5", coord_type="Second"):
    """
    Description
    get coordinate values in CRS. Needed to index out a point in 3d coordinate to get a 2d dataset, for histogram visualization

    Args:
        filename (string): string filename.nc
        coord_type (string): coodinate name to get the value of.

    Returns:
        coordinate_value: array with coordinate data
    """
    request_columns=[coord_type]
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
            col_data_ds = DG[coord_type] # ds: dataset
            col_data = col_data_ds[0:col_data_ds.shape[0]] # slicing to get the data
            processed_data = {
                "coordinate_value": col_data.tolist()
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