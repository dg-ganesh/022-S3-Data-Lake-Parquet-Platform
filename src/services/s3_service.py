"""
Project : S3 Data Lake + Parquet Platform
Project ID : 022

Amazon S3 Service
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class S3ServiceError(Exception):
    """Raised when an S3 service operation fails."""


class S3Service:
    """Provides Amazon S3 operations for Project 022."""

    def __init__(
        self,
        bucket_name: str,
        region_name: str,
    ) -> None:
        """
        Initialize the S3 service.

        Args:
            bucket_name:
                Target S3 bucket name.

            region_name:
                AWS region used by the application.

        Raises:
            ValueError:
                If required configuration is missing.
        """
        if not bucket_name.strip():
            raise ValueError(
                "S3 bucket name cannot be empty."
            )

        if not region_name.strip():
            raise ValueError(
                "AWS region cannot be empty."
            )

        self._bucket_name = bucket_name.strip()
        self._region_name = region_name.strip()

        self._client = boto3.client(
            "s3",
            region_name=self._region_name,
        )

    @property
    def bucket_name(self) -> str:
        """Return the configured S3 bucket name."""
        return self._bucket_name

    @property
    def region_name(self) -> str:
        """Return the configured AWS region."""
        return self._region_name

    def check_connection(self) -> bool:
        """
        Verify access to the configured S3 bucket.

        Returns:
            True when the bucket can be accessed.

        Raises:
            S3ServiceError:
                If the bucket cannot be accessed.
        """
        try:
            self._client.head_bucket(
                Bucket=self._bucket_name,
            )
            return True

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                f"Unable to access S3 bucket "
                f"'{self._bucket_name}'."
            ) from exc

    def bucket_exists(self) -> bool:
        """
        Check whether the configured S3 bucket is accessible.

        Returns:
            True when the bucket exists and is accessible.
            False when AWS reports that the bucket does not exist.
        """
        try:
            self._client.head_bucket(
                Bucket=self._bucket_name,
            )
            return True

        except ClientError as exc:
            error_code = (
                exc.response
                .get("Error", {})
                .get("Code", "")
            )

            if error_code in {
                "404",
                "NoSuchBucket",
            }:
                return False

            raise S3ServiceError(
                f"Unable to determine whether bucket "
                f"'{self._bucket_name}' exists."
            ) from exc

        except BotoCoreError as exc:
            raise S3ServiceError(
                f"Unable to access bucket "
                f"'{self._bucket_name}'."
            ) from exc

    def create_bucket(self) -> None:
        """
        Create the configured S3 bucket.

        Raises:
            S3ServiceError:
                If bucket creation fails.
        """
        try:
            if self._region_name == "us-east-1":
                self._client.create_bucket(
                    Bucket=self._bucket_name,
                )
            else:
                self._client.create_bucket(
                    Bucket=self._bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint":
                            self._region_name,
                    },
                )

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                f"Unable to create S3 bucket "
                f"'{self._bucket_name}'."
            ) from exc

    def ensure_bucket(self) -> bool:
        """
        Ensure that the configured S3 bucket is available.

        Returns:
            True when the bucket already exists
            or was created successfully.

        Raises:
            S3ServiceError:
                If the bucket cannot be made available.
        """
        if self.bucket_exists():
            return True

        self.create_bucket()

        return self.bucket_exists()

    def upload_file(
        self,
        local_file: Path,
        s3_key: str,
    ) -> str:
        """
        Upload a local file to S3.

        Args:
            local_file:
                Path to the local file.

            s3_key:
                Destination object key in S3.

        Returns:
            The S3 URI of the uploaded object.

        Raises:
            FileNotFoundError:
                If the local file does not exist.

            ValueError:
                If the S3 key is empty.

            S3ServiceError:
                If the upload fails.
        """
        if not local_file.is_file():
            raise FileNotFoundError(
                f"Local file does not exist: "
                f"{local_file}"
            )

        normalized_key = self._validate_s3_key(
            s3_key
        )

        try:
            self._client.upload_file(
                str(local_file),
                self._bucket_name,
                normalized_key,
            )

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                f"Unable to upload '{local_file}' "
                f"to 's3://{self._bucket_name}/"
                f"{normalized_key}'."
            ) from exc

        return (
            f"s3://{self._bucket_name}/"
            f"{normalized_key}"
        )

    def object_exists(
        self,
        s3_key: str,
    ) -> bool:
        """
        Determine whether an S3 object exists.

        Args:
            s3_key:
                S3 object key.

        Returns:
            True if the object exists, otherwise False.

        Raises:
            ValueError:
                If the S3 key is empty.

            S3ServiceError:
                If the existence check fails.
        """
        normalized_key = self._validate_s3_key(
            s3_key
        )

        try:
            self._client.head_object(
                Bucket=self._bucket_name,
                Key=normalized_key,
            )

            return True

        except ClientError as exc:
            error_code = (
                exc.response
                .get("Error", {})
                .get("Code", "")
            )

            if error_code in {
                "404",
                "NoSuchKey",
                "NotFound",
            }:
                return False

            raise S3ServiceError(
                f"Unable to check S3 object "
                f"'{normalized_key}'."
            ) from exc

        except BotoCoreError as exc:
            raise S3ServiceError(
                f"Unable to check S3 object "
                f"'{normalized_key}'."
            ) from exc

    def get_object_metadata(
        self,
        s3_key: str,
    ) -> dict[str, Any]:
        """
        Retrieve metadata for an S3 object.

        Args:
            s3_key:
                S3 object key.

        Returns:
            Dictionary containing S3 object metadata.

        Raises:
            ValueError:
                If the S3 key is empty.

            S3ServiceError:
                If metadata retrieval fails.
        """
        normalized_key = self._validate_s3_key(
            s3_key
        )

        try:
            response = self._client.head_object(
                Bucket=self._bucket_name,
                Key=normalized_key,
            )

            return {
                "content_length":
                    response.get(
                        "ContentLength",
                        0,
                    ),
                "content_type":
                    response.get(
                        "ContentType"
                    ),
                "content_encoding":
                    response.get(
                        "ContentEncoding"
                    ),
                "etag":
                    response.get("ETag"),
                "last_modified":
                    response.get(
                        "LastModified"
                    ),
                "metadata":
                    response.get(
                        "Metadata",
                        {},
                    ),
            }

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                "Unable to retrieve metadata for "
                f"S3 object '{normalized_key}'."
            ) from exc

    def get_object_bytes(
        self,
        s3_key: str,
    ) -> bytes:
        """
        Read an S3 object's contents into memory.

        Args:
            s3_key: Key of the object to read.

        Returns:
            Object contents as bytes.
        """
        normalized_key = self._validate_s3_key(
            s3_key
        )

        try:
            response = self._client.get_object(
                Bucket=self._bucket_name,
                Key=normalized_key,
            )
            body = response["Body"]

            try:
                return body.read()
            finally:
                body.close()

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                "Unable to read S3 object "
                f"'{normalized_key}'."
            ) from exc

    def list_objects(
        self,
        prefix: str = "",
    ) -> list[dict[str, Any]]:
        """
        List objects within an S3 prefix.

        Args:
            prefix:
                Optional S3 prefix used to filter objects.

        Returns:
            List of object metadata dictionaries.

        Raises:
            S3ServiceError:
                If the operation fails.
        """
        normalized_prefix = (
            prefix.strip().lstrip("/")
        )

        objects: list[dict[str, Any]] = []

        try:
            paginator = self._client.get_paginator(
                "list_objects_v2"
            )

            pages = paginator.paginate(
                Bucket=self._bucket_name,
                Prefix=normalized_prefix,
            )

            for page in pages:
                objects.extend(
                    page.get("Contents", [])
                )

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                "Unable to list objects under "
                f"prefix '{normalized_prefix}'."
            ) from exc

        return objects

    def delete_objects(
        self,
        s3_keys: Iterable[str],
    ) -> int:
        """
        Delete multiple S3 objects.

        Objects are deleted in batches of up to
        1000 keys, which is the AWS S3 limit for
        one DeleteObjects request.

        Args:
            s3_keys:
                Iterable containing S3 object keys.

        Returns:
            Number of objects requested for deletion.

        Raises:
            ValueError:
                If any S3 key is empty.

            S3ServiceError:
                If deletion fails.
        """
        normalized_keys = [
            self._validate_s3_key(key)
            for key in s3_keys
        ]

        if not normalized_keys:
            return 0

        deleted_count = 0

        try:
            for start in range(
                0,
                len(normalized_keys),
                1000,
            ):
                batch = normalized_keys[
                    start:start + 1000
                ]

                response = self._client.delete_objects(
                    Bucket=self._bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": key}
                            for key in batch
                        ],
                        "Quiet": False,
                    },
                )

                errors = response.get(
                    "Errors",
                    [],
                )

                if errors:
                    error_details = "; ".join(
                        (
                            f"{error.get('Key')}: "
                            f"{error.get('Code')} - "
                            f"{error.get('Message')}"
                        )
                        for error in errors
                    )

                    raise S3ServiceError(
                        "One or more S3 object "
                        "deletions failed: "
                        f"{error_details}"
                    )

                deleted_count += len(
                    response.get(
                        "Deleted",
                        [],
                    )
                )

        except S3ServiceError:
            raise

        except (
            BotoCoreError,
            ClientError,
        ) as exc:
            raise S3ServiceError(
                f"Unable to delete objects "
                f"from S3 bucket "
                f"'{self._bucket_name}'."
            ) from exc

        return deleted_count

    def delete_prefix(
        self,
        prefix: str,
    ) -> int:
        """
        Delete every object under an S3 prefix.

        Args:
            prefix:
                S3 prefix whose objects should be deleted.

        Returns:
            Number of deleted objects.
        """
        normalized_prefix = (
            prefix.strip().lstrip("/")
        )

        if not normalized_prefix:
            return 0

        objects = self.list_objects(
            prefix=normalized_prefix
        )

        return self.delete_objects(
            str(object_metadata["Key"])
            for object_metadata in objects
            if object_metadata.get("Key")
        )

    def create_prefix(
        self,
        prefix: str,
    ) -> str:
        """
        Create an S3 prefix marker.

        S3 does not have traditional directories.
        A zero-byte object ending in '/' is used here
        to make the intended data-lake structure explicit.

        Args:
            prefix:
                Prefix to create.

        Returns:
            S3 URI of the created prefix marker.

        Raises:
            ValueError:
                If the prefix is empty.

            S3ServiceError:
                If the operation fails.
        """
        normalized_prefix = (
            prefix.strip().strip("/")
        )

        if not normalized_prefix:
            raise ValueError(
                "S3 prefix cannot be empty."
            )

        key = f"{normalized_prefix}/"

        try:
            self._client.put_object(
                Bucket=self._bucket_name,
                Key=key,
                Body=b"",
            )

        except (BotoCoreError, ClientError) as exc:
            raise S3ServiceError(
                f"Unable to create S3 prefix "
                f"'{key}'."
            ) from exc

        return (
            f"s3://{self._bucket_name}/{key}"
        )

    def _validate_s3_key(
        self,
        s3_key: str,
    ) -> str:
        """
        Validate and normalize an S3 object key.

        Args:
            s3_key:
                S3 object key.

        Returns:
            Normalized S3 key.

        Raises:
            ValueError:
                If the key is empty.
        """
        normalized_key = (
            s3_key.strip().lstrip("/")
        )

        if not normalized_key:
            raise ValueError(
                "S3 object key cannot be empty."
            )

        return normalized_key


__all__ = [
    "S3Service",
    "S3ServiceError",
]
