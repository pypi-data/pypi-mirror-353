import json
import os
import sys
from pathlib import Path

import click
import requests
from pydantic import ValidationError

from . import api, git
from .config import CONFIG_FILENAME_PREFIX, ConfigModel
from .results import match_diff, match_files


@click.group()
def cli():
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--quiet", is_flag=True)
def validate(path, quiet):
    """
    Locally validate config files
    """

    errors = {}
    configs = {}  # Configs by directory

    for root, _, files in os.walk(path):
        for f in files:
            if f.startswith(CONFIG_FILENAME_PREFIX):
                config_path = Path(root) / f

                if not quiet:
                    click.echo(config_path, nl=False)
                try:
                    configs[config_path] = ConfigModel.from_filesystem(config_path)

                    if not quiet:
                        click.secho(" -> OK", fg="green")
                except ValidationError as e:
                    if not quiet:
                        click.secho(" -> ERROR", fg="red")

                    errors[config_path] = e

    for path, error in errors.items():
        click.secho(str(path), fg="red")
        print(error)

    if errors:
        sys.exit(1)

    return configs


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--changed", is_flag=True)
@click.option("--json", "as_json", is_flag=True)
@click.option("--by", type=click.Choice(["scope", "path"]), default="path")
@click.pass_context
def ls(ctx, path, changed, as_json, by):
    """
    List files and lines that match scopes
    """
    configs = ctx.invoke(validate, path=path, quiet=True)

    if changed:
        iterator = git.git_ls_changes(path)
    else:
        iterator = git.git_ls_files(path)

    results = match_files(configs, iterator)
    if as_json:
        click.echo(results.model_dump_json(indent=2))
    else:
        results.print(by=by)


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--json", "as_json", is_flag=True)
@click.option("--staged", is_flag=True)
@click.option("--by", type=click.Choice(["scope", "path"]), default="path")
@click.pass_context
def diff(ctx, path, as_json, staged, by):
    configs = ctx.invoke(validate, path=path, quiet=True)

    diff_args = []
    if staged:
        diff_args.append("--staged")

    diff_stream = git.git_diff_stream(path, *diff_args)

    results = match_diff(configs, diff_stream)
    if as_json:
        click.echo(results.model_dump_json(indent=2))
    else:
        results.print(by=by)


# @cli.command()
# @click.option("--check", is_flag=True)
# @click.argument("path", type=click.Path(exists=True), default=".")
# def coverage(path, check):
#     config = load_root_config()
#     num_matched = 0
#     num_total = 0

#     for f in git.git_ls_files(path):
#         file_path = Path(f)
#         matched = False

#         # TODO doesn't include line patterns...

#         for scope in config.config.scopes:
#             if scope.matches_path(file_path):
#                 matched = True
#                 break

#         if matched:
#             num_matched += 1
#         num_total += 1

#     percentage = f"{num_matched / num_total:.1%}"
#     click.echo(f"{num_matched}/{num_total} files covered ({percentage})")

#     if check and num_matched != num_total:
#         sys.exit(1)


@cli.command()
@click.option("--host", default="https://5.pullapprove.com", envvar="PULLAPPROVE_HOST")
@click.argument("target", type=str, default="")
def status(host, target):
    """
    Show the status of a PR
    """
    # if target.startswith("http"):
    #     url = target
    # elif target:
    #     # number?
    #     pass
    # else:
    #     # try to get for current branch?
    #     pass
    url = target
    session = api.get_requests_session(host=host)
    response = session.get(
        f"{host}/api/pullrequests/lookup/",
        params={"host_url": url},
    )
    response.raise_for_status()
    data = response.json()
    click.echo(json.dumps(data, indent=2))

    # Get the status, load it back as scopes


@cli.command()
@click.option("--host", default="https://5.pullapprove.com", envvar="PULLAPPROVE_HOST")
@click.argument("target", type=str, default="")
@click.pass_context
def test(ctx, host, target):
    """
    Test local config files against a live PR
    """

    configs = ctx.invoke(validate, quiet=True)

    # if target.startswith("http"):
    #     url = target
    # elif target:
    #     # number?
    #     pass
    # else:
    #     # try to get for current branch?
    #     pass
    session = api.get_requests_session(host=host)

    url = target

    response = session.get(
        f"{host}/api/pullrequests/lookup/",
        params={"host_url": url},
    )
    response.raise_for_status()
    data = response.json()

    test_url = data["test_url"]

    response = session.post(
        test_url,
        json={
            "configs": {
                str(config_path): config.config_model.model_dump()
                for config_path, config in configs.items()
            }
        },
    )
    response.raise_for_status()

    # Get the status, load it back as scopes
    print(json.dumps(response.json(), indent=2))


@cli.command()
@click.option("--host", default="https://5.pullapprove.com", envvar="PULLAPPROVE_HOST")
def login(host):
    if not host.startswith("https://"):
        click.echo("Host must start with https://")
        sys.exit(1)

    key = click.prompt("Enter your PullApprove API key", hide_input=True)

    click.echo("Verifying API key...")
    response = requests.get(
        f"{host}/api/user/",
        headers={"Authorization": f"Bearer {key}"},
    )
    if not response.status_code == 200:
        click.secho("Invalid API key", fg="red")
        # click.echo(response.text)
        sys.exit(1)

    click.echo(json.dumps(response.json(), indent=2))

    api.save_api_key(
        host=host,
        key=key,
    )

    click.secho("API key saved", fg="green")


@cli.command()
@click.option("--host", default="https://5.pullapprove.com", envvar="PULLAPPROVE_HOST")
def logout(host):
    api.delete_api_key(host=host)
    click.echo("API key deleted")


# list - find open PRs, find status url and send json request (needs PA token)

# maybe even the pypi package is hosted by pullapprove itself...
# so a hosted customer can use the version tied to their instance
# (binary? sh script? require uv?)
