"""Resolve {{ key }} placeholders before MkDocs renders.

Order:

1. ``MKDOCS_SECRETS`` if set (must exist).
2. ``secrets.local.yml`` (local real values, gitignored).
3. ``secrets.scrambled.yml`` (committed fake values for public builds).
4. Otherwise leave placeholders untouched.
"""

import os
import re

import yaml
from mkdocs.exceptions import PluginError

TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")
DEFAULT_SECRETS = "secrets.local.yml"
DEFAULT_SCRAMBLED = "secrets.scrambled.yml"


def _lookup(data, dotted):
    current = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def on_page_markdown(markdown, page, config, files):
    base = os.path.dirname(os.path.abspath(config.get("config_file_path") or "mkdocs.yml"))

    configured = os.environ.get("MKDOCS_SECRETS")
    if configured:
        path = configured if os.path.isabs(configured) else os.path.join(base, configured)
        if not os.path.isfile(path):
            raise PluginError(f"MKDOCS_SECRETS={path} is not a file")
    else:
        path = os.path.join(base, DEFAULT_SECRETS)
        if not os.path.isfile(path):
            path = os.path.join(base, DEFAULT_SCRAMBLED)
            if not os.path.isfile(path):
                return markdown

    with open(path, encoding="utf-8") as handle:
        values = yaml.safe_load(handle) or {}

    def replace(match):
        key = match.group(1)
        value = _lookup(values, key)
        if value is None:
            raise PluginError(f"{page.file.src_path}: no value for '{{{{ {key} }}}}'")
        return str(value)

    return TOKEN.sub(replace, markdown)
