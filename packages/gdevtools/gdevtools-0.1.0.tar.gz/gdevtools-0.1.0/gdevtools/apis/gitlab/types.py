from enum import Enum
from pydantic import BaseModel

#######################
# Groups and projects #
#######################


class GitLabProjectVisibility(Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    INTERNAL = "internal"


class GitLabGroup(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    path: str
    full_path: str
    avatar_url: str | None = None
    web_url: str


class GitLabNamespaceKind(Enum):
    GROUP = "group"
    USER = "user"


class GitLabNamespace(GitLabGroup):
    kind: GitLabNamespaceKind


class GitLabProject(BaseModel):
    id: int
    name: str
    path: str
    name_with_namespace: str
    path_with_namespace: str
    description: str | None = None
    default_branch: str
    visibility: GitLabProjectVisibility
    namespace: GitLabNamespace


####################
# GitLab variables #
####################


class GitLabVariableType(Enum):
    ENV_VAR = "env_var"


class GitLabVariable(BaseModel):
    variable_type: GitLabVariableType
    key: str
    value: str
    protected: bool
    masked: bool
    hidden: bool
    raw: bool
    environment_scope: str
    description: str | None = None
