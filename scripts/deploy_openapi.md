# deploy_openapi.py

This script publishes an OpenAPI spec to S3 and updates the corresponding runtime pointer in AWS Systems Manager (SSM). It is the standard way to deploy the API definition for use with infrastructure components such as `serverless-api`.

---

## What It Does

- Uploads `openapi/<nickname>/openapi.yaml` to an S3 bucket
- Looks up the bucket name using:
  ```
  /iac/s3-bucket/<bucket-nickname>/runtime
  ```
- Writes a runtime pointer to:
  ```
  /iac/openapi/<nickname>/runtime
  ```

This pointer is used by the API Gateway deployment process to locate the OpenAPI spec.

---

## Usage

From the root of the `aws-openapi` repository:

```bash
python scripts/deploy_openapi.py demo-api
```

This will:

1. Upload `openapi/demo-api/openapi.yaml`
2. Write the following SSM parameter:
   ```
   /iac/openapi/demo-api/runtime
   ```
   with contents like:
   ```json
   {
      "source": "s3://aws-openapi-demo-api/openapi/demo-api/openapi.yaml"
   }
   ```

---

## Git-Based Behavior

This script deploys the spec currently checked out in your Git branch. There is no version tagging or branching logic — what you have locally is what gets published.

---

## Optional Arguments

```bash
python scripts/deploy_openapi.py demo-api \
  --bucket-nickname openapi-storage \
  --file path/to/alt-openapi.yaml
```

- `--bucket-nickname`: overrides the default S3 bucket nickname (defaults to `demo-api`)
- `--file`: deploys a specific OpenAPI file (defaults to `openapi/<nickname>/openapi.yaml`)

---

## Requirements

Before running this script:

- The S3 bucket must already exist and be deployed via the `s3-bucket` component
- The OpenAPI file must include `x-lambda-nickname` values
- Each nickname must be resolvable via:
  ```
  /iac/lambda/<nickname>/runtime
  ```

---

## Integration

After publishing, the `serverless-api` component from `aws-iac` can be deployed using:

```bash
AWS_PROFILE=prod ./scripts/deploy.sh serverless-api demo-api
```

It will:

- Read the OpenAPI pointer from `/iac/openapi/demo-api/runtime`
- Resolve Lambda nicknames from SSM
- Deploy a functional API Gateway configuration
