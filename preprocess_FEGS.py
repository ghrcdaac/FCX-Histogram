import pandas as pd

def start(filename="goesr_plt_FEGS_20170321_Flash_v2.txt", request_columns=['FlashID', 'peak']):
    # fetch the data
    s3path=get_file_path(filename)
    
    # validate
    if not validate(request_columns):
        return False
    
    # if okay, proceed to the necessary data
    DF = pd.read_csv(s3path, sep=",",index_col=None,usecols=request_columns)
    # print(DF.describe)
    
    # return the processed data for render in JSON api specification format.
    return DF.to_json(orient='split', index=False)
    
# helper functions

def get_file_path(filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    path_to_file="FEGS/data"
    # path_to_file = os.environ.get('PATH_TO_FEGS')
    return f"s3://{bucket_src}/{path_to_file}/{filename}"

def validate(request_columns):
    # Available columns for FEGS
    FEGS_columns = ('FlashID', 'GPSstart','SUBstart','GPSend','SUBend', 
                'lat','lon','alt','roll','peak','energy','meanBG','MaxPixNum',
                'FOVlat1','FOVlon1','FOVlat2','FOVlon2',
                'FOVlat3','FOVlon3','FOVlat4','FOVlon4')
    
    # validation
    for request_column in set(request_columns):
        if(not request_column in FEGS_columns):
            return False
    return True

if __name__ == "__main__":
    preprocessed_data = start()
    print(preprocessed_data)