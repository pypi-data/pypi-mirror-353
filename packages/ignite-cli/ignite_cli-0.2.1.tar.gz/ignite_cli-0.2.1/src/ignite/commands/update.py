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

from igniteops_sdk.models.cloud_integration_update_request import CloudIntegrationUpdateRequest
from igniteops_sdk.api.integrations.update_cloud_integration import sync as update_cloud_integration_sync
from igniteops_sdk.models.update_project_release_body import UpdateProjectReleaseBody
from igniteops_sdk.api.projects.update_project_release import sync as update_project_release_sync
from igniteops_sdk.models.project_team_update_request import ProjectTeamUpdateRequest
from igniteops_sdk.api.projects.update_project_team_member import sync as update_project_team_member_sync

app = Typer(help="Update commands.")


@app.command("cloud-integration")
def update_cloud_integration(integration_id: str = Argument(...), body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Update a cloud integration"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = CloudIntegrationUpdateRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = update_cloud_integration_sync(client=client, integration_id=integration_id if integration_id is not None else UNSET, body=body if body is not None else UNSET)
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
def update_project_release(project_id: str = Argument(...), id: str = Argument(...), body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Update project release status"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = UpdateProjectReleaseBody.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = update_project_release_sync(client=client, project_id=project_id if project_id is not None else UNSET, id=id if id is not None else UNSET, body=body if body is not None else UNSET)
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


@app.command("project-team-member")
def update_project_team_member(project_id: str = Argument(...), user_id: str = Argument(...), body: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Update a team member's role"""
    
    # support @file.json syntax or inline JSON for body argument and wrap into model
    if 'body' in locals() and isinstance(body, str):
        if body.startswith("@"):
            raw = Path(body[1:]).read_text()
        else:
            raw = body
        data = _json.loads(raw)
        body = ProjectTeamUpdateRequest.from_dict(data)
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = update_project_team_member_sync(client=client, project_id=project_id if project_id is not None else UNSET, user_id=user_id if user_id is not None else UNSET, body=body if body is not None else UNSET)
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

