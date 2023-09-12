import os
import numpy as np
import pandas as pd
import json

from helpers.pagination import Pagination
from helpers.density_sampling import DensitySampling

# Available columns for LIP
LIP_columns = ('Time', 'Ex', 'Ey', 'Ez', 'Eq', 'Lat', 'Lon', 'Alt', 'Roll', 'Pitch', 'Heading')

def start(filename="goesr_plt_lip_20170517.txt", coord_type='Time', data_type='Eq', params=None, pageno=1, pagesize=50, density=0.05):
    dsamp = DensitySampling(density)

    request_columns=[coord_type, data_type]

    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False

    # TODO: explore on skiprows and nrows. For now, they donot work with usecols and index_cols set.
    # Also, the total number of data is to be known, for pagination to work. So, skiprows and nrows is skipped for now.
    # DF = pd.read_csv(s3path, sep=", ", names=LIP_columns, index_col=coord_type, usecols=request_columns, engine='python', skiprows=start_index, nrows=end_index)

    # if okay, proceed to the necessary data
    DF = pd.read_csv(s3path, sep=", ", names=LIP_columns, index_col=coord_type, usecols=request_columns, engine='python')
    # print(DF.describe)
    
    # Filter NaN datas
    filtered = DF[DF[data_type].notnull()]

    # page to index conversion
    total_data = filtered.shape[0]
    pg = Pagination(pageno, pagesize, total_data)
    start_index = pg.get_offset()
    end_index = pg.get_offset_end()
    # end_index = start_index + pg.get_item_per_page() #Although this is sufficient as, nrows can be greater than the available rows. so end_index handling (get_offset_end()) not necessary here.

    # return the processed data for render in JSON api specification format.
    pre_result = filtered[start_index:end_index].to_json(orient='split')
    result = json.loads(pre_result)
    result['data'] = dsamp.sample_data(np.array(result['data']).flatten().tolist())
    result['index'] = dsamp.sample_data(result['index'])
    return json.dumps(result)
    
# helper functions

def get_file_path(filename):
    # bucket_src = "fcx-raw-data-temp"
    bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    path_to_file="LIP/data"
    # path_to_file = os.environ.get('PATH_TO_LIP')
    return f"s3://{bucket_src}/{path_to_file}/{filename}"

def validate(request_columns):
    # validation
    for request_column in set(request_columns):
        if(not request_column in LIP_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)