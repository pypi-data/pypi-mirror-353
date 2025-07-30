from enum import Enum
import httpx

from gdevtools.apis.gitlab.client import GitLabApiClientManager
from gdevtools.apis.gitlab.types import GitLabGroup, GitLabVariable

##########
# Models #
##########


class SortBy(Enum):
    DESC = "descending"
    ASC = "ascending"


class GitLabGroupWithLevel(GitLabGroup):
    """
    A class that represents a gitlab group together with how many levels it is **above**
    another gitlab group.
    """

    base_group_id: int
    level: int


#######
# Api #
#######


class GitLabGroupsApi:
    @staticmethod
    async def get(client: httpx.Client, id: int | str) -> GitLabGroup:
        """
        Fetches information about the gitlab group.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer group identifier or string group path.

        Returns:
          GitLabGroup: description of the gitlab group
        """
        response: httpx.Response = await client.get(f"/groups/{id}")
        group: GitLabGroup = GitLabGroup.model_validate(response.json())
        return group

    @staticmethod
    async def get_group_variables(
        client: httpx.Client, id: int | str, environment_scope: str = "*"
    ) -> list[GitLabVariable]:
        """
        Fetches all variables stored in the gitlab group.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer group identifier or string group path.
          environment_scope (str): fetch variables only matching this environment scope. Defaults to '*' (all environments).

        Returns:
          list[GitLabVariable]: list of all gitlab variables in group
        """
        response: httpx.Response = await client.get(f"/groups/{id}/variables")
        variables: list[GitLabVariable] = [
            GitLabVariable.model_validate(var) for var in response.json()
        ]
        variables = [
            var for var in variables if var.environment_scope == environment_scope
        ]
        return variables

    @classmethod
    async def get_parent_group(
        cls,
        client: httpx.Client,
        id: int | str,
    ) -> GitLabGroup | None:
        """
        Fetches the parent gitlab group of a group, if it has one.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer group identifier or group project path.

        Returns:
          GitLabGroup | None: parent gitlab group, if it exists
        """
        group: GitLabGroup = await cls.get(client=client, id=id)
        if group.parent_id is None:
            return None
        parent_group = await cls.get(client=client, id=group.parent_id)
        return parent_group

    @classmethod
    async def get_parent_groups(
        cls, client: httpx.Client, id: int | str, sort_by: SortBy = SortBy.DESC
    ) -> list[GitLabGroup]:
        """
        Recursively fetches all parent gitlab group of a group.

        Args:
          client (httpx.Client): httpx Client for the gitlab api
          id (int | str): integer group identifier or group project path.
          sort_by (SortBy): how to sort the groups. 'SortBy.DESC' sorts from top parent to base group,
            'SortBy.ASC' does the opposite, starting with the base group and going up to top parent.
            Defaults to 'SortBy.DESC'.

        Returns:
          list[GitLabGroup]: list of parent gitlab groups
        """

        def add_to_list(
            group: GitLabGroup, groups: list[GitLabGroup]
        ) -> list[GitLabGroup]:
            if sort_by == SortBy.ASC:
                return groups + [group]
            elif sort_by == SortBy.DESC:
                return [group] + groups
            else:
                raise ValueError(
                    f"Invalid SortBy option selected: {sort_by}. Must be one of SortBy.ASC or SortBy.DESC."
                )

        async def get_parent_groups_aux(
            group: GitLabGroup, accumulator: list[GitLabGroup]
        ) -> list[GitLabGroup]:
            # Create new accumulator by adding group to list
            new_accumulator = add_to_list(group, accumulator)

            # Return accumulator when top level group is reached
            if group.parent_id is None:
                return new_accumulator

            # Otherwise, fetch parent group and recursively keep going
            parent_group = await cls.get_parent_group(client=client, id=group.id)
            if parent_group is None:
                raise RuntimeError("GitLab API responses are inconsistent")

            return await get_parent_groups_aux(
                group=parent_group, accumulator=new_accumulator
            )

        group: GitLabGroup = await cls.get(client=client, id=id)
        return await get_parent_groups_aux(group=group, accumulator=[])


if __name__ == "__main__":
    import asyncio

    async def main():
        async with GitLabApiClientManager().client() as client:
            # vars = await GitLabGroupsApi.get_group_variables(client, 95764352)
            groups = await GitLabGroupsApi.get_parent_groups(
                client, 100896239, sort_by=SortBy.ASC
            )
            print(groups)

    asyncio.run(main())
