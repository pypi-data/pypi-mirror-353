# gdevtools

A collection of developer tools to make local development easier.

## Installation

`uvx install gdevtools`

## Usage

Get help with: `gdevtools --help`.

You can also request help for any nested commands: `gdevtools gitlab --help`

## Load gitlab variables into environment

Used to load gitlab variables into environment variables. By default, it even loads all your parent group gitlab variables, recursively.

Default usage, which fetches variables recursively:
```bash
gdevtools gitlab variables load_to_env --project-id 1234 # Creates a .env file with the values of all variables
. ./.env                                               # Load environment variables into current shell
```

Additional options:
```bash
gdevtools gitlab variables load_to_env --project-id 1234 --environment-scope dev --prefix TF_VAR_ --suffix _HURRAY --file-name .my-env
. ./.my-env
```
