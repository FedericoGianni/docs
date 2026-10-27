#!/usr/bin/env python3
"""Fail when a real value reaches the repo or a placeholder is undefined."""

import re
import struct
import subprocess
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"
SECRETS = BASE / "secrets.local.yml"
SCRAMBLED = BASE / "secrets.scrambled.yml"
ENCRYPTED = BASE / "secrets.age"
KEY = BASE / "secrets.key"
TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")
FORBIDDEN = {
    "figma share link": re.compile(r"figma\.com/board/"),
}
# Real values must go through {{ keys }}; a bare private IP is a leak.
BARE_IP = re.compile(
    r"\b(?:10(?:\.\d{1,3}){3}"
    r"|192\.168(?:\.\d{1,3}){2}"
    r"|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}"
    r"|127(?:\.\d{1,3}){3}"
    r"|169\.254(?:\.\d{1,3}){2})\b"
)
# Real hostnames must also go through {{ keys }}. Public/software domains are
# allowlisted; anything else in the source is treated as a leak.
HOST = re.compile(r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}\b", re.I)
# Coverage boundary for hostname detection: extend if a real domain uses another TLD.
TLDS = {
    "ai", "app", "biz", "ca", "cc", "cloud", "co", "com", "de", "dev", "edu",
    "eu", "fr", "gov", "info", "internal", "io", "lan", "local", "me",
    "net", "nl", "online", "org", "sh", "site", "tech", "tv", "uk", "us", "xyz",
}
ALLOWED_HOSTS = {
    "ansible.com",
    "caddyserver.com",
    "cloudflare.com",
    "community-scripts.org",
    "debian.org",
    "docker.com",
    "example.com",
    "example.org",
    "example.net",
    "github.com",
    "github.io",
    "gitlab.com",
    "grafana.com",
    "healthchecks.io",
    "home-assistant.io",
    "k3s.io",
    "kubernetes.io",
    "longhorn.io",
    "mermaid.js.org",
    "mikrotik.com",
    "proxmox.com",
    "python.org",
    "renovatebot.com",
    "tailscale.com",
    "ubuntu.com",
    "youtube.com",
}
EXCLUDE_PARTS = {".git", "site", "public", "venv", ".venv", "__pycache__"}
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".sh", ".txt", ".py", ".toml", ".cfg", ".ini"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
METADATA_CHUNKS = {b"eXIf"}


def text_files():
    for path in BASE.rglob("*"):
        if not path.is_file() or path in {SECRETS, KEY}:
            continue
        if any(part in EXCLUDE_PARTS for part in path.relative_to(BASE).parts):
            continue
        if path.suffix in TEXT_SUFFIXES or path.name == "Makefile":
            yield path


def image_files():
    for path in BASE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if any(part in EXCLUDE_PARTS for part in path.relative_to(BASE).parts):
            continue
        yield path


def image_metadata(path):
    """Return metadata chunk names; covers the EXIF/GPS leak vector."""
    data = path.read_bytes()
    found = set()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        offset = 8
        while offset + 8 <= len(data):
            (length,) = struct.unpack(">I", data[offset : offset + 4])
            kind = data[offset + 4 : offset + 8]
            if kind in METADATA_CHUNKS:
                found.add(kind.decode("latin1"))
            offset += 12 + length
    elif data.startswith(b"\xff\xd8"):
        if b"Exif\x00\x00" in data:
            found.add("EXIF")
    return found


def load(path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def flatten(data, prefix=""):
    for key, value in data.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            yield from flatten(value, name + ".")
        else:
            yield name, str(value)


def main():
    failures = []
    real = dict(flatten(load(SECRETS)))
    scrambled = dict(flatten(load(SCRAMBLED)))
    pages = sorted(DOCS.rglob("*.md"))
    files = list(text_files())

    for key, value in real.items():
        if not value:
            continue
        for path in files:
            if value in path.read_text(encoding="utf-8", errors="ignore"):
                failures.append(f"leak: {path.relative_to(BASE)} contains {key}")

    for label, pattern in FORBIDDEN.items():
        for path in files:
            if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                failures.append(f"forbidden {label}: {path.relative_to(BASE)}")

    for page in pages:
        text = page.read_text(encoding="utf-8")
        for match in BARE_IP.finditer(text):
            failures.append(
                f"bare private IP in {page.relative_to(BASE)}: {match.group(0)}"
            )
        stripped = TOKEN.sub("", text)
        for match in HOST.finditer(stripped):
            host = match.group(0).lower()
            if host.rsplit(".", 1)[-1] not in TLDS:
                continue
            if any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_HOSTS):
                continue
            failures.append(
                f"bare hostname in {page.relative_to(BASE)}: {host} "
                f"(use {{{{ domain }}}}, or add it to ALLOWED_HOSTS in scripts/check.py)"
            )
        for match in TOKEN.finditer(text):
            key = match.group(1)
            if key not in scrambled:
                failures.append(
                    f"missing '{key}' in {SCRAMBLED.name} ({page.relative_to(BASE)})"
                )
            if real and key not in real:
                failures.append(
                    f"missing '{key}' in {SECRETS.name} ({page.relative_to(BASE)})"
                )

    for image in image_files():
        chunks = image_metadata(image)
        if chunks:
            failures.append(
                f"image metadata in {image.relative_to(BASE)}: {', '.join(sorted(chunks))}"
            )

    tracked = subprocess.run(
        ["git", "-C", str(BASE), "ls-files", SECRETS.name, KEY.name],
        capture_output=True,
        text=True,
    ).stdout.split()
    for name in tracked:
        failures.append(f"{name} is tracked by git")

    if not SCRAMBLED.exists():
        failures.append("missing secrets.scrambled.yml")
    for key in real:
        if key not in scrambled:
            failures.append(f"{SCRAMBLED.name} is missing '{key}'")

    if not ENCRYPTED.exists():
        failures.append("missing secrets.age")
    elif not ENCRYPTED.read_bytes().startswith(b"age-encryption.org/"):
        failures.append("secrets.age is not age-encrypted")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
