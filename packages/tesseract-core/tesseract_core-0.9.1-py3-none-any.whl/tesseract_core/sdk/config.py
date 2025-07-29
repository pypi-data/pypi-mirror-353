# Copyright 2025 Pasteur Labs. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import shlex
import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict


def validate_executable(value: str | Sequence[str]) -> tuple[str, ...]:
    """Get the path to the requested program."""
    if isinstance(value, str):
        exe, *args = shlex.split(value)
    else:
        exe, *args = value

    exe = shutil.which(exe)
    if exe is None:
        raise FileNotFoundError(f"{exe} executable not found.")

    exe_path = Path(exe)
    if not exe_path.is_file():
        raise FileNotFoundError(f"{exe} is not a file.")
    if not os.access(exe_path, os.X_OK):
        raise PermissionError(f"{exe} is not executable.")

    return (str(exe_path.resolve()), *args)


def maybe_split_args(value: str | Sequence[str]) -> tuple[str, ...]:
    """Split arguments if they are passed as a string."""
    if isinstance(value, str):
        value = shlex.split(value)
    return tuple(value)


class RuntimeConfig(BaseModel):
    """Available runtime configuration."""

    docker_executable: Annotated[
        tuple[str, ...], BeforeValidator(validate_executable)
    ] = ("docker",)
    docker_compose_executable: Annotated[
        tuple[str, ...], BeforeValidator(validate_executable)
    ] = ("docker", "compose")
    docker_build_args: Annotated[
        tuple[str, ...], BeforeValidator(maybe_split_args)
    ] = ()

    model_config = ConfigDict(frozen=True, extra="forbid")


def update_config(**kwargs: Any) -> None:
    """Create a new runtime configuration from the current environment.

    Passed keyword arguments will override environment variables.
    """
    global _current_config

    conf_settings = {}
    for field in RuntimeConfig.model_fields.keys():
        env_key = f"TESSERACT_{field.upper()}"
        if env_key in os.environ:
            conf_settings[field] = os.environ[env_key]

    conf_settings.update(kwargs)

    config = RuntimeConfig(**conf_settings)
    _current_config = config


_current_config = None
update_config()


def get_config() -> RuntimeConfig:
    """Return the current runtime configuration."""
    return _current_config
