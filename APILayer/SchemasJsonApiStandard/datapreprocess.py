from marshmallow_jsonapi import Schema, fields

# Serializers, before transmitting data
class DataPreprocessingSerializerSchema(Schema):
    id = fields.Str(dump_only=True)
    message = fields.Str()
    data = fields.Str()
    instrument_type = fields.Str() # validate it to be from a closed set of inputs

    class Meta:
        type_ = "data_pre_process_response"

# De-Serializers, after receiving data
class DataPreprocessingDeserializerSchema(Schema):
    id = fields.Str(dump_only=True)
    instrument_type = fields.Str(required=True)
    datetime = fields.Str(required=True)
    coord_type = fields.Str(required=True)
    data_type = fields.Str(required=True)
    params = fields.Str(required=True)

    class Meta:
        type_ = "data_pre_process_request"