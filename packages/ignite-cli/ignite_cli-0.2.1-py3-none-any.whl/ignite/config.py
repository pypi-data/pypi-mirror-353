from pathlib import Path
import json

CONFIG_FILE = Path.home() / ".ignite_config.json"


def load_config() -> dict:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_config(cfg: dict) -> None:
    """Save configuration to file."""
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
        CONFIG_FILE.chmod(0o600)
    except Exception:
        pass


def get_default_output() -> str:
    """Return default output format from config."""
    return load_config().get("output", "plain")


def set_default_output(value: str) -> None:
    """Set default output format in config."""
    cfg = load_config()
    cfg["output"] = value
    save_config(cfg)
