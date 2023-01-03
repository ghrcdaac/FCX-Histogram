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

def get_filename(instrument, datetime):
    # using the instrument type and datetime, get the filename for the preprocessed data.
    # refer. data manual for each instrument type
    return "goesr_plt_lip_20170517.txt"