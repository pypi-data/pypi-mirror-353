"""
@author: cunyue
@file: __init__.py
@time: 2025/6/5 14:03
@description: 同步本地数据到云端
"""

import click

from swanlab.api import terminal_login, create_http
from swanlab.error import KeyFileError
from swanlab.package import get_key
from swanlab.sync import sync as sync_logs


@click.command()
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        readable=True,
    ),
    nargs=1,
    required=True,
)
@click.option(
    "--api-key",
    "-k",
    default=None,
    type=str,
    help="The API key to use for authentication. If not specified, it will use the default API key from the environment."
    "If specified, it will log in using this API key but will not save the key.",
)
@click.option(
    "--workspace",
    "-w",
    default=None,
    type=str,
    help="The workspace to sync the logs to. If not specified, it will use the default workspace.",
)
@click.option(
    "--project",
    "-p",
    default=None,
    type=str,
    help="The project to sync the logs to. If not specified, it will use the default project.",
)
def sync(path, api_key, workspace, project):
    """
    Synchronize local logs to the cloud.
    """
    # 1. 登录
    # 如果输入了 api-key， 使用此 api-key 登录但不保存数据
    try:
        api_key = get_key() if api_key is None else api_key
    except KeyFileError:
        pass
    log_info = terminal_login(api_key=api_key, save_key=False)
    create_http(log_info)
    # 2. 同步日志
    sync_logs(path, login_required=False)
