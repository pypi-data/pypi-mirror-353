from pathlib import Path
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ConfigDict,
    UrlConstraints,
    field_validator,
    model_validator,
)
from pydantic.types import PathType
from pydantic_settings import BaseSettings, SettingsConfigDict

FilePath = Annotated[Path, AfterValidator(lambda v: v.expanduser()), PathType("file")]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
    )


class StrictBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="forbid", validate_assignment=True, use_enum_values=True, env_nested_delimiter="__"
    )


class S3Options(StrictBaseModel):
    endpoint_url: AnyHttpUrl
    """
    The URL for the S3 service.
    """

    bucket: str
    """
    The name of the S3 bucket.
    """

    access_key: str | None = None
    """
    The access key for the S3 bucket.
    If undefined, it is read from the AWS_ACCESS_KEY_ID environment variable.
    """

    secret: str | None = None
    """
    The secret key for the S3 bucket.
    If undefined, it is read from the AWS_SECRET_ACCESS_KEY environment variable.
    """

    session_token: str | None = None
    """
    The session token for temporary credentials (optional).
    """

    region_name: str | None = None
    """
    The region name for the S3 bucket.
    """

    api_version: str | None = None
    """
    The S3 API version.
    """

    use_ssl: bool = True
    """
    Whether to use SSL for S3 operations.
    """

    proxy_url: AnyUrl | None = None
    """
    The proxy URL for S3 operations (optional).
    """

    request_checksum_calculation: str | None = None
    """
    Whether to calculate checksums for S3 request payloads (optional).
    Valid values are:

    * ``when_supported`` -- When set, a checksum will be calculated for
      all request payloads of operations modeled with the ``httpChecksum``
      trait where ``requestChecksumRequired`` is ``true`` or a
      ``requestAlgorithmMember`` is modeled.

    * ``when_required`` -- When set, a checksum will only be calculated
      for request payloads of operations modeled with the ``httpChecksum``
      trait where ``requestChecksumRequired`` is ``true`` or where a
      ``requestAlgorithmMember`` is modeled and supplied.

    Defaults to None.
    """

    multipart_chunksize: int = 256 * 1024**2
    """
    The size of the chunks to use for multipart uploads in bytes.
    """


class PruefberichtConfig(StrictBaseModel):
    authorization_url: Annotated[AnyHttpUrl, UrlConstraints(allowed_schemes=["https"], host_required=True)] | None = (
        None
    )
    """
    URL from which to request a new Prüfbericht submission token
    """

    client_id: str | None = None
    """
    Client ID used to obtain new Prüfbericht submission tokens
    """

    client_secret: str | None = None
    """
    Client secret used to obtain new Prüfbericht submission tokens
    """

    api_base_url: Annotated[AnyHttpUrl, UrlConstraints(allowed_schemes=["https"], host_required=True)] | None = None
    """
    Base URL to BfArM Submission (Prüfbericht) API
    """


class ConfigModel(StrictBaseSettings):
    model_config = SettingsConfigDict(env_prefix="grz_")

    grz_public_key: str | None = None
    """
    The public key of the recipient (the associated GRZ).
    """

    grz_public_key_path: FilePath | None = None
    """
    Path to the crypt4gh public key of the recipient (the associated GRZ).
    """

    grz_private_key_path: FilePath | None = None
    """
    Path to the crypt4gh private key of the recipient (optional).
    """

    submitter_private_key_path: FilePath | None = None
    """
    Path to the submitter's private key (optional).
    """

    s3_options: S3Options

    pruefbericht: PruefberichtConfig = PruefberichtConfig()

    @field_validator("grz_public_key")
    @classmethod
    def check_grz_public_key(cls, v):
        if v is not None and "BEGIN CRYPT4GH PUBLIC KEY" not in v and "END CRYPT4GH PUBLIC KEY" not in v:
            raise ValueError("Invalid public key format")
        return v

    @model_validator(mode="after")
    def validate_grz_public_key(self) -> Self:
        if self.grz_public_key is None and self.grz_public_key_path is None:
            raise ValueError("Either grz_public_key or grz_public_key_path must be set.")
        if self.grz_public_key is not None and self.grz_public_key_path is not None:
            raise ValueError("Only one of grz_public_key or grz_public_key_path must be set.")
        return self
