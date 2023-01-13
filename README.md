## Steps to deploy the histogram preprocessing script in the AWS lambda
### It is supposed that the user has some prior knowledge about lambda and docker.

1. Deploy the script to ECR using the deploy script. The deploy script takes in `account_id`, `region` and `repository_name` as variables, so set them accordingly. 
     - Then run `bash deploy.sh`
     - This will upload the docker image to the ECR according to the variables set. 
2. In the aws lamdba console, create a new lambda function (using docker), and select the deployed `repository_name`
3. Configure REST API gateway for the lambda.
     - In the API gateway console, Allow CORS for resource, and re-deploy the API gateway.
4. The script needs permission to read and write to S3.
   - Either create your own permission, Or add `sanjog-subsetting-fcx-role-ikmiflyf` permission to each lambda.
5. In general setting set the following configuration.
   - Memory: 1024MB 
   - Ephemeral storage: 5120MB
   - Timeout: 10min

