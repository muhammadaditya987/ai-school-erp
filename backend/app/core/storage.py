from functools import lru_cache

import boto3
from botocore.config import Config

from app.core.config import get_settings


@lru_cache
def get_s3_client():
    settings = get_settings()
    credentials: dict[str, str] = {}
    if (
        settings.s3_access_key_id
        and settings.s3_secret_access_key
        and settings.s3_access_key_id.get_secret_value().strip()
        and settings.s3_secret_access_key.get_secret_value().strip()
    ):
        credentials = {
            "aws_access_key_id": settings.s3_access_key_id.get_secret_value(),
            "aws_secret_access_key": settings.s3_secret_access_key.get_secret_value(),
        }
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        config=Config(s3={"addressing_style": "path"}),
        **credentials,
    )


def put_object(key: str, body: bytes, content_type: str) -> None:
    settings = get_settings()
    request = {
        "Bucket": settings.s3_bucket,
        "Key": key,
        "Body": body,
        "ContentType": content_type,
    }
    if not settings.s3_endpoint_url:
        request["ServerSideEncryption"] = "AES256"
    get_s3_client().put_object(**request)


def get_object(key: str) -> bytes:
    settings = get_settings()
    response = get_s3_client().get_object(Bucket=settings.s3_bucket, Key=key)
    return response["Body"].read()
