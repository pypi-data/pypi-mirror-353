import httpx

from gdevtools.apis.gitlab.client import GitLabApiClientManager
from gdevtools.apis.gitlab.groups import GitLabGroupsApi, SortBy
from gdevtools.apis.gitlab.types import (
    GitLabProject,
    GitLabGroup,
    GitLabVariable,
    GitLabNamespaceKind,
)


#######
# API #
#######


class GitLabProjectsApi:
    @staticmethod
    async def get(client: httpx.Client, id: int | str) -> GitLabProject:
        """
        Fetches information about the gitlab project.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer project identifier or string project path.

        Returns:
          GitLabProject: description of the gitlab project
        """
        response: httpx.Response = await client.get(f"/projects/{id}")
        project: GitLabProject = GitLabProject.model_validate(response.json())
        return project

    @classmethod
    async def get_parent_group(
        cls,
        client: httpx.Client,
        id: int | str,
    ) -> GitLabGroup | None:
        """
        Fetches the parent gitlab group of a project, if it has one.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer project identifier or string project path.

        Returns:
          GitLabGroup | None: parent gitlab group, if it exists
        """
        project: GitLabProject = await cls.get(client=client, id=id)
        if project.namespace.kind != GitLabNamespaceKind.GROUP:
            return None
        return GitLabGroup(**project.namespace.model_dump())

    @classmethod
    async def get_parent_groups(
        cls, client: httpx.Client, id: int | str, sort_by: SortBy | None = SortBy.DESC
    ) -> list[GitLabGroup]:
        """
        Fetches information about the gitlab project.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer project identifier or string project path.

        Returns:
          GitLabProject: description of the gitlab project
        """
        parent_group: GitLabGroup | None = await cls.get_parent_group(
            client=client, id=id
        )
        if parent_group is None:
            return []

        parent_groups = await GitLabGroupsApi.get_parent_groups(
            client=client, id=parent_group.id, sort_by=sort_by
        )
        return parent_groups

    @classmethod
    async def get_project_variables(
        cls,
        client: httpx.Client,
        id: int | str,
        recursive: bool = False,
        environment_scope: str = "*",
    ) -> list[GitLabVariable]:
        """
        Fetches all variables stored in the gitlab project.

        Args:
          client (httpx.Client): httpx Client for the gitlab api.
          id (int | str): integer project identifier or string project path.
          recursive (bool): whether to fetch variables from all parent groups of the project, recursively.
          environment_scope (str): fetch variables only matching this environment scope. Defaults to '*' (all environments).

        Returns:
          list[GitLabVariable]: list of all gitlab variables in project
        """
        response: httpx.Response = await client.get(f"/projects/{id}/variables")
        variables: list[GitLabVariable] = [
            GitLabVariable.model_validate(var) for var in response.json()
        ]
        variables = [
            var for var in variables if var.environment_scope == environment_scope
        ]

        if not recursive:
            return variables

        # Fetch group variables recursively
        # NOTE:
        # Since the key of variables from top level groups and low level groups might clash,
        # we first order the parent groups from lowest level to top level using SortBy.ASC
        # and then only add variables with new keys to our variable list.
        # This way, if there is a variable key collision, we only preserve the variables of the lower level groups
        # which should take precedence.
        variable_keys: list[str] = [var.key for var in variables]
        parent_groups = await cls.get_parent_groups(
            client=client, id=id, sort_by=SortBy.ASC
        )
        for group in parent_groups:
            group_variables = await GitLabGroupsApi.get_group_variables(
                client=client, id=group.id, environment_scope=environment_scope
            )
            new_variables = [
                var for var in group_variables if var.key not in variable_keys
            ]
            variables += new_variables

        return variables


if __name__ == "__main__":
    import asyncio

    async def main():
        async with GitLabApiClientManager().client() as client:
            vars = await GitLabProjectsApi.get_project_variables(
                client, 66285509, recursive=True
            )
            # groups = await GitLabProjectsApi.get_parent_groups(client, 66285509)
            print(vars)

    asyncio.run(main())
