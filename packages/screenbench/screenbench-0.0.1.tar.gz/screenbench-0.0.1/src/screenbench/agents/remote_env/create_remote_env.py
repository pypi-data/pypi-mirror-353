import logging
from typing import Annotated, TypeAlias, overload

from pydantic import Field

from screensuite.agents.remote_env.docker.provider import (
    DockerProvider,
    DockerProviderConfig,
)
from screensuite.agents.remote_env.provider import FakeProvider, FakeProviderConfig

logger = logging.getLogger()

ProviderConfig: TypeAlias = Annotated[
    DockerProviderConfig | FakeProviderConfig,
    Field(discriminator="PROVIDER_NAME"),
]
ProviderClient: TypeAlias = DockerProvider | FakeProvider


# fmt: off
@overload
def create_remote_env_provider(config: DockerProviderConfig) -> DockerProvider: ...
@overload
def create_remote_env_provider(config: ProviderConfig) -> ProviderClient: ...
# fmt: on
def create_remote_env_provider(config: ProviderConfig) -> ProviderClient:
    if config.PROVIDER_NAME == "docker":
        return DockerProvider(config=config)
    raise NotImplementedError(f"Provider {config.PROVIDER_NAME} not implemented")
