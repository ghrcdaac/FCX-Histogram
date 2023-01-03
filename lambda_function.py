import json
from APILayer.SchemasJsonApiStandard.datapreprocess import DataPreprocessingDeserializerSchema, DataPreprocessingSerializerSchema
from .preprocess_FEGS import start as startFEGS
from .preprocess_CRS import start as startCRS
from .preprocess_CPL import start as startCPL
from .preprocess_LIP import start as startLIP

def lambda_handler(event, context):
    body = json.loads(event["body"]) #dictonary
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

    instrument_type = payload['instrument_type'], datetime = payload['datetime'], coord_type = payload['coord_type'], data_type = payload['data_type'], params = payload['params']
    
    # validate datetime and instrument type.
    filename = get_filename(instrument_type, datetime)

    preprocessing_instruments = {
        'FEGS': startFEGS,
        'LIP': startLIP, 
        'CRS': startCRS,
        'CPL': startCPL
    }

    selected_preporcessing = preprocessing_instruments.get(instrument_type, False)
    preprocessed_data = {}
    if (selected_preporcessing):
        preprocessed_data = selected_preporcessing(filename, coord_type, data_type, params)
    
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
    
    responseBody = {
                'message': "Subsetting lambda function invoked.",
                'data' : preprocessed_data
            }

    # SERIALIZE DATA START
    serializedResponse = DataPreprocessingSerializerSchema().dumps(responseBody) #serialize
    # SERIALIZE DATA END

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET'
        },
        'body': serializedResponse
    }

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