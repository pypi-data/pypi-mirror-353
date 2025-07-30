# sqlstride/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Config:
    project_path: Path
    host: str
    port: int
    instance: str
    database: str
    username: str
    password: str
    trusted_auth: bool
    sql_dialect: str
    default_schema: str
    log_table: str = "sqlstride_log"
    lock_table: str = "sqlstride_lock"
    jinja_vars: dict = None


def load_config(project_path: Path, host: str, port: int, instance: str, database: str, username: str, password: str,
                trusted_auth: bool, sql_dialect: str, default_schema: str, log_table: str = "sqlstride_log",
                lock_table: str = "sqlstride_lock", jinja_vars: dict = None) -> Config:
    """Read sqlstride.yaml, merge env vars & CLI overrides, return a Config object."""
    config_file = project_path / "sqlstride.yaml"
    if not config_file.exists():
        raise FileNotFoundError("sqlstride.yaml not found in the project path")

    data = yaml.safe_load(config_file.read_text()) or {}
    # log_table = data.get("log_table", "sqlstride_log")
    # check if value was passed in from cli, if not load from config file
    if not host:
        host = data.get("host", None)
        if not host:
            raise ValueError("host is required in sqlstride.yaml or as a CLI argument")
    if not port:
        port = data.get("port", None)
    if not instance:
        instance = data.get("instance", None)
    if not database:
        database = data.get("database", None)
    if not username:
        username = data.get("username", None)
    if not password:
        password = data.get("password", None)
    if not trusted_auth:
        trusted_auth = data.get("trusted_auth", False)
    if not sql_dialect:
        sql_dialect = data.get("sql_dialect", "postgres")
    if not default_schema:
        default_schema = data.get("default_schema", None)
    if not log_table:
        log_table = data.get("log_table", "sqlstride_log")
    if not lock_table:
        lock_table = data.get("lock_table", "sqlstride_lock")
    if not jinja_vars:
        jinja_vars = data.get("jinja_vars", {})

    return Config(project_path, host, port, instance, database, username, password, trusted_auth,
                  sql_dialect, default_schema, log_table, lock_table, jinja_vars)
