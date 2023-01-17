## Steps to deploy the histogram preprocessing script in the AWS lambda
### It is supposed that the user has some prior knowledge about lambda and docker. User needs to have docker configured on the deployment machine.

1. Deploy the script to ECR using the deploy script. The deploy script takes in `account_id`, `region` and `repository_name` as variables, so set them accordingly. 
     - In the AWS ECR, create a repository with `repository_name`
     - Then run `bash deploy.sh`
     - This will upload the docker image to the ECR according to the variables set. 
2. In the aws lamdba console, create a new lambda function (using docker), and select the deployed `repository_name`
3. Configure REST API gateway for the lambda.
     - In the API gateway console, Allow CORS for resource, and re-deploy the API gateway.
4. The script needs permission to read and write to S3.
   - Either create your own permission, Or add `sanjog-histogram-preprocessing-fcx-v1` permission to each lambda.
5. In general setting set the following configuration.
   - Memory: 1024MB 
   - Ephemeral storage: 5120MB
   - Timeout: 10min
6. Use the `Histogram_preprocessed_data.postman_collection.json` postman collection to test the Lambda.

## Steps to run the script locally:
### It is supposed that the user has docker set up on the local machine.

1. Using the docker image: 
     - `docker build -t <image_tag_name> .`
     - `docker image ls`
     - `docker run -d -p <available_port>:8080 <image_tag_name>`
     - `docker ps` to check if the docker is running.
     - curl using `curl -XPOST "http://localhost:<given_port>/2015-03-31/functions/function/invocations" -d '{"key": "value"}'`
     - Now as the docker image will run on the given port, ref. https://docs.aws.amazon.com/lambda/latest/dg/images-test.html, to emulate the lambda environment on local machine and to begin the test.
2. Directly run each .py scripts using `python3 preprocess_xyz.py`. Here, the default parameters are used to run each preprocessing script.
3. Refer the associated interactive `ipynb` to understand the step wise execution and logic behind each preprocessing.

