bash ./predeploy.sh
&& terraform init \
-backend-config="bucket=${TF_VAR_S3_STATE_BUCKET}" \
-backend-config="region=${TF_VAR_S3_STATE_BUCKET_aws_region}"
&& terraform apply -auto-approve