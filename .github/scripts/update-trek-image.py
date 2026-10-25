#!/usr/bin/env python3
"""Update the Home Assistant app version to the latest stable TREK image tag."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen


CONFIG_PATH = Path("apps/trek-haos/config.yaml")
TAGS_URL = "https://hub.docker.com/v2/repositories/mauriceboe/trek/tags"
ARCHITECTURES = {"amd64", "arm64"}
VERSION_LINE = re.compile(r'(?m)^version:\s*"(?P<version>\d+\.\d+\.\d+)"\s*$')
STABLE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def fetch_stable_tags() -> dict[str, set[str]]:
    """Return stable version tags and the architectures published for each."""
    url: str | None = f"{TAGS_URL}?page_size=100"
    tags: dict[str, set[str]] = {}

    while url:
        request = Request(url, headers={"User-Agent": "trekHAOS-image-updater"})
        with urlopen(request, timeout=30) as response:
            page = json.load(response)

        for tag in page["results"]:
            name = tag["name"]
            if not STABLE_VERSION.fullmatch(name):
                continue
            tags[name] = {
                image["architecture"]
                for image in tag.get("images", [])
                if image.get("status") == "active" and image.get("os") == "linux"
            }
        url = page.get("next")

    return tags


def main() -> int:
    config = CONFIG_PATH.read_text(encoding="utf-8")
    version_match = VERSION_LINE.search(config)
    if version_match is None:
        raise ValueError(f"Could not find a quoted stable version in {CONFIG_PATH}")

    current = version_match.group("version")
    current_version = tuple(map(int, current.split(".")))
    tags = fetch_stable_tags()
    candidates = [
        tag
        for tag, architectures in tags.items()
        if ARCHITECTURES.issubset(architectures)
        and tuple(map(int, tag.split("."))) > current_version
    ]
    if not candidates:
        print(f"No newer stable multi-architecture TREK image found (current: {current}).")
        set_output("update_available", "false")
        return 0

    latest = max(candidates, key=lambda tag: tuple(map(int, tag.split("."))))
    updated = VERSION_LINE.sub(
        f'version: "{latest}"',
        config,
        count=1,
    )
    CONFIG_PATH.write_text(updated, encoding="utf-8")

    print(f"Updated TREK image version from {current} to {latest}.")
    set_output("update_available", "true")
    set_output("new_version", latest)
    return 0


def set_output(name: str, value: str) -> None:
    """Write a GitHub Actions output, or print it when run locally."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Failed to check TREK image tags: {error}", file=sys.stderr)
        raise SystemExit(1) from error
