#!/usr/bin/env python3

import argparse
import boto3
import json
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

lambda_client = boto3.client("lambda")
ssm = boto3.client("ssm")


def install_dependencies(lambda_dir: Path, build_dir: Path):
    req_file = lambda_dir / "requirements.txt"
    if req_file.exists():
        print("📦 Installing dependencies from requirements.txt...")
        subprocess.run(
            [
                "pip",
                "install",
                "--target",
                str(build_dir),
                "-r",
                str(req_file),
                "--upgrade",
            ],
            check=True,
        )


def build_lambda(nickname: str) -> Path:
    lambda_dir = Path(f"lambdas/{nickname}").resolve()

    # dist/ holds the zip; build/ holds the actual payload contents
    dist_dir = lambda_dir / "dist"
    build_dir = dist_dir / "build"
    dist_zip = dist_dir / f"{nickname}.zip"

    # Clean dist + build
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    build_dir.mkdir(parents=True)

    # Copy handler .py files into build_dir
    for file in lambda_dir.glob("*.py"):
        shutil.copy(file, build_dir)

    # Install deps into build_dir
    install_dependencies(lambda_dir, build_dir)

    print(f"📦 Creating ZIP file: {dist_zip}")
    # Zip only the build_dir contents, enable Zip64 + compression
    with ZipFile(dist_zip, "w", compression=ZIP_DEFLATED, allowZip64=True) as zipf:
        for file in build_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(build_dir)
                zipf.write(file, arcname=arcname)

    return dist_zip


def publish_lambda(nickname: str, zip_path: Path) -> str:
    print(f"🚀 Publishing Lambda: {nickname}")
    with open(zip_path, "rb") as f:
        response = lambda_client.update_function_code(
            FunctionName=nickname,
            ZipFile=f.read(),
            Publish=True,
        )
    return response["FunctionArn"]


def put_ssm_parameter(nickname: str, arn: str):
    param_path = f"/iac/lambda/{nickname}/runtime"
    print(f"📝 Writing runtime ARN to SSM: {param_path}")
    ssm.put_parameter(
        Name=param_path,
        Value=json.dumps({"arn": arn}),
        Type="String",
        Overwrite=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "nickname", help="Lambda nickname (directory name under lambdas/)"
    )
    args = parser.parse_args()

    zip_path = build_lambda(args.nickname)
    versioned_arn = publish_lambda(args.nickname, zip_path)
    # arn:aws:lambda:region:acct:function:name:version -> strip version
    unversioned_arn = ":".join(versioned_arn.split(":")[:7])
    put_ssm_parameter(args.nickname, unversioned_arn)

    print(f"✅ Lambda {args.nickname} deployed → {versioned_arn}")


if __name__ == "__main__":
    main()
