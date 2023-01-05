import pandas as pd
from helpers.pagination import Pagination

# Available columns for LIP
LIP_columns = ('Time', 'Ex', 'Ey', 'Ez', 'Eq', 'Lat', 'Lon', 'Alt', 'Roll', 'Pitch', 'Heading')

def start(filename="goesr_plt_lip_20170517.txt", coord_type='Time', data_type='Eq', pageno=1, pagesize=50):
    request_columns=[coord_type, data_type]

    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False

    # page to index conversion
    pg = Pagination(pageno, pagesize)
    start_index = pg.get_offset()
    end_index = start_index + pg.get_item_per_page()
    
    # if okay, proceed to the necessary data
    DF = pd.read_csv(s3path, sep=", ", names=LIP_columns, index_col=coord_type, usecols=request_columns, engine='python', skiprows=start_index, nrows=end_index)
    # print(DF.describe)
    
    # Filter NaN datas
    filtered = DF[DF[data_type].notnull()]

    # return the processed data for render in JSON api specification format.
    return filtered.to_json(orient='split')
    
# helper functions

def get_file_path(filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
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