import asyncio
import json
import typer

from typing import Annotated

from gdevtools.apis.gitlab.client import GitLabApiClientManager
from gdevtools.apis.gitlab.projects import GitLabProjectsApi
from gdevtools.apis.gitlab.types import GitLabVariable


app = typer.Typer()


@app.command()
def load_to_env(
    project_id: Annotated[
        int, typer.Option(help="integer identifier of your gitlab project")
    ],
    recursive: Annotated[
        bool,
        typer.Option(
            help="whether or not to recursively fetch CI variables from top level groups. Defaults to True."
        ),
    ] = True,
    environment_scope: Annotated[
        str,
        typer.Option(
            help="environment scope for the variables to fetch. Defaults to '*' (all environments)."
        ),
    ] = "*",
    prefix: Annotated[
        str,
        typer.Option(
            help="a prefix to add to the variable's name when loaded to an env var. Defaults to no prefix."
        ),
    ] = "",
    suffix: Annotated[
        str,
        typer.Option(
            help="a suffix to add to the variable's name when loaded to an env var. Defaults to no suffix."
        ),
    ] = "",
    to_lower: Annotated[
        bool,
        typer.Option(
            help="whether to convert the name of the environment variables to lowercase. Does not include suffix and prefix. Defaults to False"
        ),
    ] = False,
    file_name: Annotated[
        str,
        typer.Option(
            help="name of the .env file where to persist the values of the environment variables."
        ),
    ] = ".env",
):
    """
    Fetches gitlab CI variables from a gitlab project and creates a .env file with their contents.
    """

    async def fetch_variables() -> list[GitLabVariable]:
        async with GitLabApiClientManager().client() as client:
            variables = await GitLabProjectsApi.get_project_variables(
                client=client,
                id=project_id,
                recursive=recursive,
                environment_scope=environment_scope,
            )
            return variables

    # Fetch gitlab variables
    vars: list[GitLabVariable] = asyncio.run(fetch_variables())
    print(f"Fetched gitlab variables: {[var.key for var in vars]}")

    # Create file with environment variables
    env_var_names: list[str] = []
    with open(file_name, "w") as f:
        for var in vars:
            var_key: str = var.key.lower() if to_lower else var.key
            var_name: str = prefix + var_key + suffix
            f.write(f"{var_name}={json.dumps(var.value)}\n")
            env_var_names.append(var_name)
    print(f"Created environment variables: {env_var_names}")
