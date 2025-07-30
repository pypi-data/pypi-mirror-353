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

from igniteops_sdk.api.integrations.get_cloud_integration import sync as get_cloud_integration_sync
from igniteops_sdk.api.integrations.get_cloud_integrations import sync as get_cloud_integrations_sync
from igniteops_sdk.api.integrations.get_repositories import sync as get_repositories_sync
from igniteops_sdk.api.project_team.get_v1_users import sync as get_v1_users_sync
from igniteops_sdk.api.projects.get_project import sync as get_project_sync
from igniteops_sdk.api.projects.get_project_activity import sync as get_project_activity_sync
from igniteops_sdk.api.projects.get_project_releases import sync as get_project_releases_sync
from igniteops_sdk.api.projects.get_project_team import sync as get_project_team_sync
from igniteops_sdk.api.projects.get_projects import sync as get_projects_sync
from igniteops_sdk.api.status.get_status import sync as get_status_sync
from igniteops_sdk.api.subscriptions.get_payment_method import sync as get_payment_method_sync
from igniteops_sdk.api.subscriptions.get_subscription import sync as get_subscription_sync
from igniteops_sdk.api.subscriptions.get_subscription_plans import sync as get_subscription_plans_sync

app = Typer(help="Get commands.")


@app.command("cloud-integration")
def get_cloud_integration(integration_id: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get a cloud integration"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_cloud_integration_sync(client=client, integration_id=integration_id if integration_id is not None else UNSET)
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


@app.command("cloud-integrations")
def get_cloud_integrations(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get user's cloud integrations"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_cloud_integrations_sync(client=client)
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


@app.command("repositories")
def get_repositories(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get user's repository integrations"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_repositories_sync(client=client)
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


@app.command("v1-users")
def get_v1_users(q: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Search users by name or email"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_v1_users_sync(client=client, q=q if q is not None else UNSET)
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
def get_project(project_id: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get a project by ID"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_project_sync(client=client, project_id=project_id if project_id is not None else UNSET)
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


@app.command("project-activity")
def get_project_activity(project_id: str = Argument(...), limit: str = Option(None), next_token: str = Option(None), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get activity for a project"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_project_activity_sync(client=client, project_id=project_id if project_id is not None else UNSET, limit=limit if limit is not None else UNSET, next_token=next_token if next_token is not None else UNSET)
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


@app.command("project-releases")
def get_project_releases(project_id: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get project releases"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_project_releases_sync(client=client, project_id=project_id if project_id is not None else UNSET)
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


@app.command("project-team")
def get_project_team(project_id: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """List project team members"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_project_team_sync(client=client, project_id=project_id if project_id is not None else UNSET)
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


@app.command("projects")
def get_projects(limit: str = Option(None), next_token: str = Option(None), language: str = Option(None), sort_by: str = Option(None), sort_order: str = Option(None), favs: str = Option(None), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get user's projects"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_projects_sync(client=client, limit=limit if limit is not None else UNSET, next_token=next_token if next_token is not None else UNSET, language=language if language is not None else UNSET, sort_by=sort_by if sort_by is not None else UNSET, sort_order=sort_order if sort_order is not None else UNSET, favs=favs if favs is not None else UNSET)
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


@app.command("status")
def get_status(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Gets status of services"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_status_sync(client=client)
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


@app.command("payment-method")
def get_payment_method(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get user's payment method"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_payment_method_sync(client=client)
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
def get_subscription(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Get user's active subscription"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_subscription_sync(client=client)
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


@app.command("subscription-plans")
def get_subscription_plans(output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Gets available subscription plans"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = get_subscription_plans_sync(client=client)
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

