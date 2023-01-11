> build using build.sh
> upload the zip inside dist to the lambda
> api gateway, cors policy and re-deploy
> roles to access s3
> layers for packages
     used packages:
     - boto3 (not needed)
     - json (not needed)
     - marshmallow_jsonapi
     - numpy
     - pandas
     - xarray (installs, pandas and numpy as dependencies)
     - scipy
     - s3fs (installs botocore as dependencies)
     - h5py (installs numpy as dependency)

