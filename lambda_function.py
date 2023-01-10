import json
import boto3
from APILayer.SchemasJsonApiStandard.datapreprocess import DataPreprocessingDeserializerSchema, DataPreprocessingSerializerSchema
from preprocess_FEGS import start as startFEGS
from preprocess_CRS import start as startCRS
from preprocess_CPL import start as startCPL
from preprocess_LIP import start as startLIP
from preprocess_cpl_coord_vals import start as getCPLCoords
from preprocess_crs_coord_vals import start as getCRSCoords

def lambda_handler(event, context):
    body = json.loads(event["body"]) #dictonary
    if (not body):
        mock = '{ "data": { "type": "data_pre_process_request", "attributes": { "instrument_type" : "FEGS", "datetime" : "2017-03-21", "coord_type" : "FlashID", "data_type" : "peak", "params" : "None", "pageno" : "1", "pagesize" : "20", "density": "0.05" } } }'    # body = json.loads(event["body"]) #dictonary
        body = json.loads(mock)
    payload = {}

    # prepare the data required to call the instrument preprocessors

    # # DESERIALIZE DATA START
    validataionError = DataPreprocessingDeserializerSchema().validate(body)
    if (validataionError):
        # if any kind of error, return it as response.
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET'
            },
            'body': json.dumps(validataionError)
            }
    payload = DataPreprocessingDeserializerSchema().load(body) #deserilalize
    # DESERIALIZE DATA END

    instrument_type = payload['instrument_type']
    datetime = payload['datetime']
    coord_type = payload['coord_type']
    data_type = payload['data_type']
    params = payload['params']
    pageno = payload['pageno']
    pagesize = payload['pagesize']
    density = payload['density']

    # validate if data corresponding to datetime and instrument type is available.
    filename = get_filename(instrument_type, datetime)
    if(not validate_filename(instrument_type, filename)):
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET'
            },
            'body': 'File for given instrument in the given date is not available.'
        }

    # if data_type is not provided in request, then the request is for coord values only.
    if (not data_type):
        response_body = col_request_handler(filename, instrument_type, coord_type)
    else:
        response_body = data_request_handler(filename, instrument_type, coord_type, data_type, params, pageno, pagesize, density)

    # SERIALIZE DATA START
    serialized_response = DataPreprocessingSerializerSchema().dumps(response_body) #serialize
    # SERIALIZE DATA END

    result = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },
        'body': serialized_response
    }
    print("res=>", result)
    return result

## REQUEST HANDLERS START

def col_request_handler(filename, instrument_type, coord_type):
    """
    This function handles the request for the column data.
    When a coordinate values is requested for a specific filename (includes dates), for a specific instrument,
    this function returns the column data

    Args:
        filename (string): name of the data file, from which the column values are to be extracted
        instrument_type (string): the type of instrument, from which the data was collected
        coord_type (string): the name of the coordinate (column), which values are to be extracted

    Returns:
        dictonary: the dictonary contains "coordinate_value" as the key, and an array of coordinate values as the value 
    """
    preprocessing_instruments_coords = { 
                'CRS': getCRSCoords,
                'CPL': getCPLCoords
            }
    get_instrument_coords = preprocessing_instruments_coords.get(instrument_type, False)
    preprocessed_data = {}
    if (get_instrument_coords):
        preprocessed_data = get_instrument_coords(filename, coord_type)

    if (not preprocessed_data):
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET'
            },
            'body': "The requested instrument or column data for preprocessing doesnot Exist."
            }

    return {
                'message': "Subsetting lambda function invoked.",
                'data' : preprocessed_data
            }

def data_request_handler(filename, instrument_type, coord_type, data_type, params, pageno=1, pagesize=50, density=0.05):
    """
    This function handles the request for the 2D data, for histogram plots

    Args:
        filename (string): name of the data file, from which the 2-dim data are to be extracted
        instrument_type (string): the type of instrument, from which the data was collected
        coord_type (string): the name of the coordinate (column), which values are to be extracted. The first dim.
        data_type (string): the name of the corresponding data, which values are to be extracted. The second dim.
        params (string): when the data set has 2-D coordiates pointing to a data value (where data value is the 3rd-dim), 
                         use one value of the either coordinate (say first)
                         and get the next coordinate (say second) and data values corresponding to that specific value.
                         Hence, managing 2D data set for histogram plot, from a 3D dataset.
                         Note: This is a optional paramater, if the dataset is 2-dim. i.e. 1st-dim as coordinate, and 2nd dim as data values
        pageno (number): the page to get the data from
        pagesize (number): the no of data rows to include per page

    Returns:
        dictonary: The dictonary contains "columns", "index" and "data" as keys, necessary for 2-d histogram plot.
                    index (array): values for the first coordinate
                    data (array): values for the second coordinate
                    columns (array): name of those 2-d coordinates
                    Note: the key here are named with reference to the data which are needed by three.js for plots.
    """
    preprocessing_instruments = {
                'FEGS': startFEGS,
                'LIP': startLIP,
                'CRS': startCRS,
                'CPL': startCPL
            }

    selected_preporcessing = preprocessing_instruments.get(instrument_type, False)
    preprocessed_data = {}
    if (selected_preporcessing):
        preprocessed_data = selected_preporcessing(filename, coord_type, data_type, params, pageno, pagesize, density)

    if (not preprocessed_data):
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET'
            },
            'body': "The requested instrument or column data for preprocessing doesnot Exist."
            }

    return {
                'message': "Subsetting lambda function invoked.",
                'data' : preprocessed_data
            }

## REQUEST HANDLERS END

## FILENAME HANDLERS START

def get_filename(instrument, date):
    # using the instrument type and datetime, get the filename for the preprocessed data.
    # refer. data manual for each instrument type
    """
    Description

    Args:
        instrument (string): The name of the instrument from which the data is to be read
        date (string): The date where the instrument collected data . format it to be in YYYY-MM-DD format.

    Returns:
        file_name (string): particular filename for the data of the instrument in the specified date.
    """
    # convert to fdatetime
    fdate = date.replace("-", "")
    if (instrument == "FEGS"):
        return filename_fegs(fdate)
    elif (instrument == "LIP"):
        return filename_lip(fdate)
    elif (instrument == "CRS"):
        return filename_crs(fdate)
    elif (instrument == "CPL"):
        return filename_cpl(fdate)

def filename_fegs(date = '20170321'):
    # available date ranges from March 21, 2017 to May 17, 2017
    # Flash and pulse data are unavailable for the following flight dates: March 23 and 28, April 6, 11 and 13, and May 7, 2017.

    # return 'goesr_plt_FEGS_YYYYMMDD_[Flash|Pulse|MedianBG]_[v2|vK2].txt'
    return f"goesr_plt_FEGS_{date}_Flash_v2.txt"

def filename_lip(date = '20170517'):
    # available date ranges from March 21, 2017 to May 17, 2017
    # Two data files for April 6, 2017 and April 27, 2017 are not included in this dataset due to missing navigation information;

    # return 'goesr_plt_lip_YYYYMMDD.txt'
    return f"goesr_plt_lip_{date}.txt"

def filename_crs(date = '20170517'):
    # available date ranges from April 11, 2017 to May 17, 2017
    # The ER-2 aircraft did not operate each day of the campaign, so CRS data are only available for aircraft flight days.
    # Which date are they available for then ???

    # return 'GOESR_CRS_L1B_YYYYMMDD_v0.nc'
    return f"GOESR_CRS_L1B_{date}_v0.nc"

def filename_cpl(date = '20170427'):
    # available date ranges from April 13, 2017 to May 14, 2017
    # Also, the ER-2 aircraft did not operate each day of the campaign, therefore, data are only available on flight days.
    # Which date are they available for then ???

    # return "goesrplt_CPL_[ATB|ATB-4sec]_L1B_<flight>_<YYYYMMDD>.hdf5"
    return f"goesrplt_CPL_ATB_L1B_17930_{date}.hdf5"

## FILENAME HANDLERS END


## FILE (AVAILABILITY) VALIDATION

def validate_filename(instrument_type, filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    s3_client = boto3.client('s3')
    file_dir = get_file_path(instrument_type, filename)
    try:
        # if File_bck is Found
        s3_client.head_object(Bucket=bucket_src, Key=f'{file_dir}')
        print(f'File with "{filename}" name found.')
        return True
    except:
        # if file is not found
        print(f'File with name "{filename}" doesnot exists.\n')
        return False

def get_file_path(instrument_type, filename):
    bucket_src = "fcx-raw-data-temp"
    # bucket_src = os.environ.get('SOURCE_BUCKET_NAME')
    if (instrument_type == "FEGS"):
        path_to_file = "FEGS/data"
    if (instrument_type == "LIP"):
        path_to_file = "LIP/data"
    if (instrument_type == "CRS"):
        path_to_file = "CRS/data"
    if (instrument_type == "CPL"):
        path_to_file = "CPL/data/L1B"

    # path_to_file = os.environ.get('PATH_TO_FEGS')
    return f"{path_to_file}/{filename}"

## FILE VALIDATION END