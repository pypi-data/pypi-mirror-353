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

from igniteops_sdk.api.api_keys.reissue_key import sync as reissue_key_sync

app = Typer(help="Reissue commands.")


@app.command("key")
def reissue_key(key_id: str = Argument(...), output: str = Option(get_default_output(), '-o', '--output', help='Output format', case_sensitive=False, show_choices=True), output_force: str = Option(None, '-ow', '--output-force', help='Set default output format', case_sensitive=False, show_choices=True), debug: bool = Option(False, '--debug', help='Enable HTTP request/response logging')):
    """Re-issue a API Key (generate a new secret)"""
    
    # debug HTTP
    if debug:
        logging.basicConfig()
        for name in ("httpx","httpcore","requests","urllib3"):
            logging.getLogger(name).setLevel(logging.DEBUG)
    client = _sdk_client()
    try:
        resp = reissue_key_sync(client=client, key_id=key_id if key_id is not None else UNSET)
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

