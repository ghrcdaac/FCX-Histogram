output "HISTOGRAM_TOOL_API" {
  description = "api endpoint to invoke fcx-histogram-preprocessing-api. Refer postman collection."

  value = "${aws_api_gateway_stage.histogram_tool_preprocessing.invoke_url}${aws_api_gateway_resource.histogram_tool_preprocessing.path}"
}

output "HISTOGRAM_TOOL_API_KEY" {
  description = "key required to invoke fcx-histogram-preprocessing-api endpoint."

  value = aws_api_gateway_api_key.histogram_tool_preprocessing_api_key.value
  sensitive = true
}