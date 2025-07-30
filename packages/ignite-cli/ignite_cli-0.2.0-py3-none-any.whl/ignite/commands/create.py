from __future__ import annotations
"""Generated, do not edit."""
from typer import Typer, Option, Argument
from igniteops_sdk.client import AuthenticatedClient
from igniteops_sdk.types import UNSET
from ignite.utils.output import show
import json as _json
import logging
import typer
import sys
from igniteops_sdk.errors import UnexpectedStatus
from ignite.client import API_BASE, TOKEN_FILE
from ignite.config import get_default_output, set_default_output
from pathlib import Path  # support @file.json syntax for body

def _sdk_client() -> AuthenticatedClient:
    token = None
    try:
        if TOKEN_FILE.exists():
            token = TOKEN_FILE.read_text().strip()
    except Exception:
        pass
    # propagate non-2xx statuses (e.g., 401/403) as errors
    return AuthenticatedClient(base_url=API_BASE, token=token or "", raise_on_unexpected_status=True)

from igniteops_sdk.models.api_key_create_request import ApiKeyCreateRequest
from igniteops_sdk.api.api_keys.create_key import sync as create_key_sync
from igniteops_sdk.models.cloud_integration_request import CloudIntegrationRequest
from igniteops_sdk.api.integrations.create_cloud_integration import sync as create_cloud_integration_sync
from igniteops_sdk.models.integration_repository_create_request import IntegrationRepositoryCreateRequest
from igniteops_sdk.api.integrations.create_repository import sync as create_repository_sync
from typing import Union
from igniteops_sdk.api.projects.create_project import sync as create_project_sync
from igniteops_sdk.models.create_project_release_body import CreateProjectReleaseBody
from igniteops_sdk.api.projects.create_project_release import sync as create_project_release_sync
from igniteops_sdk.models.subscription_create_request import SubscriptionCreateRequest
from igniteops_sdk.api.subscriptions.create_subscription import sync as create_subscription_sync

app = Typer(help="Create commands.")


@app.command("key")
def create_key(body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create an API Key"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = ApiKeyCreateRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_key_sync(client=client, body=body if body is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))


@app.command("cloud-integration")
def create_cloud_integration(body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create a cloud integration"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = CloudIntegrationRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_cloud_integration_sync(client=client, body=body if body is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))


@app.command("repository")
def create_repository(body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create a repository integration"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = IntegrationRepositoryCreateRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_repository_sync(client=client, body=body if body is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))


@app.command("project")
def create_project(body: str = Argument(...), dry_run: str = Option(None), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create a new project"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = Union.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_project_sync(client=client, body=body if body is not None else UNSET, dry_run=dry_run if dry_run is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))


@app.command("project-release")
def create_project_release(project_id: str = Argument(...), body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create project release"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = CreateProjectReleaseBody.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_project_release_sync(client=client, project_id=project_id if project_id is not None else UNSET, body=body if body is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))


@app.command("subscription")
def create_subscription(body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Create a new subscription"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = SubscriptionCreateRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = create_subscription_sync(client=client, body=body if body is not None else UNSET)
    except UnexpectedStatus as e:
        # handle unauthorized or expired token
        if e.status_code in (401, 403):
            typer.secho(
                "Unauthorized or expired token. Please run 'ignite login'.",
                fg="red",
                err=True,
            )
        else:
            typer.secho(str(e), fg="red", err=True)
        sys.exit(1)
    # handle output force
    if output_force:
        set_default_output(output_force)
        typer.secho(f"Default output set to {output_force}", fg="green")
        effective_output = output_force
    else:
        effective_output = output
    show(resp, raw_json=(effective_output == 'json'), raw_yaml=(effective_output == 'yaml'))

