# Lambda Deployment Script – `deploy_lambda.py`

This script publishes a Lambda function to AWS and updates its **unversioned ARN** in SSM Parameter Store. It is the standard way to deploy Lambda functions from the `aws-openapi` repo into an Adage-managed infrastructure.

---

## What It Does

For a given Lambda nickname (directory under `lambdas/`), the script:

1. Builds a deployment ZIP containing:
   - All top-level `*.py` files in `lambdas/<nickname>/`
   - All dependencies from `lambdas/<nickname>/requirements.txt` (if present)
2. Uploads the ZIP to the existing AWS Lambda function (matching the nickname)
3. Publishes a new version
4. Writes the **unversioned function ARN** (no `:version` suffix) to SSM at:

```
/iac/lambda/<nickname>/runtime
```

This SSM parameter is how other components (e.g. `serverless-api`) resolve the Lambda.

> The Lambda *must already exist.*  
> Terraform (or other IaC) must create the IAM role and the initial Lambda resource.

---

## Usage

From the root of the repository:

```bash
python scripts/deploy_lambda.py <nickname>
```

Example:

```bash
python scripts/deploy_lambda.py echo
```

This will:

1. Build `lambdas/echo/dist/echo.zip`
2. Update the Lambda function `echo`
3. Publish a new version
4. Update:

```
/iac/lambda/echo/runtime
```

with:

```json
{ "arn": "arn:aws:lambda:us-east-1:<acctId>:function:echo" }
```

which always resolves to `$LATEST`.

---

## Directory Structure

Each Lambda lives under:

```
lambdas/<nickname>/
```

Example:

```
lambdas/
  seed-sales-data/
    seed_sales_data.py
    requirements.txt
    dist/
      build/
      seed-sales-data.zip
```

---

## Build Logic

For nickname `N`:

1. Resolve `lambdas/N` as the Lambda directory
2. Recreate `lambdas/N/dist/build`
3. Copy all `*.py` files from the Lambda dir into `build/`
4. Install dependencies into `build/` (if `requirements.txt` exists)
5. Zip **only** the contents of `build/` into:

```
lambdas/N/dist/N.zip
```

6. Use `UpdateFunctionCode` to upload the ZIP
7. Publish a new version
8. Update the unversioned ARN in SSM

The ZIP never contains itself; only `build/` is zipped.

---

## Terraform / IaC Expectations

To avoid dependency cycles:

- **Terraform must create:**
  - The IAM role used by the Lambda
  - The initial `aws_lambda_function` resource (with a tiny bootstrap ZIP)

- **This deployment script must handle:**
  - Updating the Lambda code
  - Publishing a new version
  - Updating the SSM parameter

If the Lambda does not exist, AWS returns `ResourceNotFoundException` — this is expected.

---

## Requirements

- AWS credentials available via profile or environment
- Lambda must already exist with name `<nickname>`
- Runtime must match your handler (e.g., Python 3.12)
- IAM role must have already been created

---

## Notes

- Safe to run repeatedly; always pushes new code + updates SSM
- Different branches can deploy to the same nickname
- Ensures consistent resolution via the `/iac/lambda/<nickname>/runtime` parameter
