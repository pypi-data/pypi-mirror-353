from functools import partial
from typing import Any

import click

from ..commands.invenio import install_invenio_cfg
from ..commands.resolver import get_resolver
from ..commands.types import StepFunctions
from ..commands.ui import (
    build_production_ui,
    collect_assets,
    copy_translations,
    install_npm_packages,
)
from ..commands.utils import make_step, no_args, run_fixup
from ..config import OARepoConfig
from .base import command_sequence, nrp_command


@nrp_command.command(name="build")
@command_sequence()
def build_command(*, config: OARepoConfig, **kwargs: Any) -> StepFunctions:
    """Builds the repository"""
    return build_command_internal(config=config, **kwargs)


def build_command_internal(*, config: OARepoConfig, **kwargs: Any) -> StepFunctions:
    resolver = get_resolver(config)
    return (
        no_args(
            partial(click.secho, "Building repository for production", fg="yellow"),
            name="display_message",
        ),
        make_step(
            lambda config, **kwargs: resolver.clean_previous_installation(),
            name="clean_previous_installation",
        ),
        make_step(
            lambda config, **kwargs: resolver.create_empty_venv(),
            name="create_empty_venv",
        ),
        run_fixup(
            lambda config, **kwargs: resolver.check_requirements(),
            lambda config, **kwargs: resolver.build_requirements(),
            fix=True,
            name="check_and_build_requirements",
        ),
        make_step(
            lambda config, **kwargs: resolver.install_python_repository(),
            name="install_python_repository",
        ),
        install_invenio_cfg,
        copy_translations,
        collect_assets,
        install_npm_packages,
        build_production_ui,
        no_args(partial(click.secho, "Successfully built the repository", fg="green")),
    )
