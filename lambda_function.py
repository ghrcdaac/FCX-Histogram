import json
from APILayer.SchemasJsonApiStandard.triggerSubset import DataPreprocessingDeserializerSchema, DataPreprocessingSerializerSchema
from .preprocess_FEGS import start as startFEGS

def lambda_handler(event, context):
    body = json.loads(event["body"]) #dictonary
    payload = {}

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

    instrument_type = payload['instrument_type'], filename = payload['filename'], request_columns = payload['request_columns']
    
    preprocessing_instruments = {
        'FEGS': startFEGS,
        'LIPS': startFEGS, 
        'CRS': startFEGS,
        'CPL': startFEGS
    }

    selected_preporcessing = preprocessing_instruments.get(instrument_type, False)
    preprocessed_data = ''
    if (not selected_preporcessing):
        preprocessed_data = selected_preporcessing(filename, request_columns)
    
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