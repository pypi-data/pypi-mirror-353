"""Gear toolkit utilities module."""

import json
import logging
import math
import os
import subprocess
import sys
import typing as t
from contextlib import contextmanager
from pathlib import Path

log = logging.getLogger(__name__)

try:
    # Make numpy optional
    import numpy as np

    NUMPY = True
except ImportError:
    NUMPY = False


def validate_requirements_file(req_file):
    req_path = Path(req_file).resolve()
    if not req_path.is_file():
        raise ValueError(f"File does not exist: {req_path}")
    if req_path.suffix not in {".txt", ".in"}:
        raise ValueError(f"Invalid file type: {req_path.suffix}")
    return str(req_path)


def _run_pip_install(req_path: str):
    cmd = [sys.executable, "-m", "pip", "install", "-r", req_path]
    subprocess.run(cmd, check=True)


def install_requirements(req_file):
    """Install requirements from a file programatically.

    Args:
        req_file (str): Path to requirements file

    Raises:
        SystemExit: If there was an error from pip
    """
    try:
        req_path = validate_requirements_file(req_file)
        _run_pip_install(req_path)
    except (ValueError, subprocess.CalledProcessError) as e:
        log.error(f"Requirement installation failed: {e}")
        sys.exit(1)


class MetadataEncoder(json.JSONEncoder):
    # Overwrite default handler for bytes objects
    def default(self, obj: t.Any) -> t.Any:
        """Default json encoder when not handled.

        Handle bytes objects and pass everything else to the default JSONEncoder.

        For bytes, convert to hex and return the first 10 characters, or truncate.

        Args:
            obj (Any): Object to be encoded, can be anything, this only handles bytes.

        Returns:
            str: encoded obj.
        """
        if isinstance(obj, bytes):
            return obj.hex() if len(obj) < 10 else f"{obj.hex()[:10]} ... truncated byte value."

        if NUMPY:  # only if numpy is available
            if type(obj).__module__ == np.__name__:
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return obj.item()

        return json.JSONEncoder.default(self, obj)


def convert_nan_in_dict(d: dict) -> dict:
    # Note: convert_nan_in_dict is borrowed from core-api
    return {key: _convert_nan(value) for key, value in d.items()}


def _convert_nan(
    d: t.Optional[t.Union[dict, str, list, float, int]],
) -> t.Optional[t.Union[dict, str, list, float, int]]:
    # Note: _convert_nan is borrowed from core-api
    """Return converted values."""
    if d is None:
        return None
    if isinstance(d, (str, int)):
        return d
    if isinstance(d, float):
        if math.isnan(d) or math.isinf(d):
            return None
        return d
    if isinstance(d, dict):
        return {key: _convert_nan(value) for key, value in d.items()}
    if isinstance(d, list):
        return [_convert_nan(item) for item in d]
    return d


# Not really a testable unit since I'd need an instantiated client,
#  Good candidate for future integration test.
@contextmanager
def sdk_post_retry_handler(client):  # pragma: no cover
    """Patch the SDK session object to retry on specific errors.

    Safe to use on:
        - updating container info
        - updating file classification
        - adding notes
        - adding tags

    Not safe to use on:
        - Creating containers
        - Uploading files
    """
    import requests
    import urllib3

    orig_adapter = client.api_client.rest_client.session.adapters["https://"]
    try:
        BACKOFF_FACTOR = float(os.getenv("FLYWHEEL_SDK_BACKOFF_FACTOR", 0.5))
        retry = urllib3.util.Retry(
            total=5,
            backoff_factor=BACKOFF_FACTOR,
            allowed_methods=["DELETE", "GET", "HEAD", "POST", "PUT", "OPTIONS"],
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        client.api_client.rest_client.session.mount("http://", adapter)
        client.api_client.rest_client.session.mount("https://", adapter)
        yield
    finally:
        client.api_client.rest_client.session.mount("https://", orig_adapter)
        client.api_client.rest_client.session.mount("http://", orig_adapter)


@contextmanager
def sdk_delete_404_handler(client):
    """Ignore 404 errors on retries of deletes."""
    orig_resp_hook = client.api_client.res_client.session.hooks["response"]
    try:

        def ignore_404(self, resp, *args, **kwargs):
            if resp.status_code == 404:
                log.debug("Ignoring 404 response on {req.method} {req.url}")
            else:
                orig_resp_hook(self, resp, *args, *kwargs)

        client.api_client.res_client.session.hooks["response"] = ignore_404
        yield
    finally:
        client.api_client.res_client.session.hooks["response"] = orig_resp_hook


def trim(obj: dict):
    """Trim object for printing."""
    return {key: trim_lists(val) for key, val in obj.items()}


def trim_lists(obj: t.Any):
    """Replace a long list with a representation.

    List/Arrays greater than 5 in length will be replaced with the first two
    items followed by `...` then the last two items
    """
    if isinstance(obj, (list, tuple)):
        # Trim list
        if len(obj) > 5:
            return [*obj[:1], f"...{len(obj) - 2} more items...", *obj[-1:]]
        # Recurse into lists
        return [trim_lists(v) for v in obj]
    # Recurse into dictionaries
    if isinstance(obj, dict):
        return {key: trim_lists(val) for key, val in obj.items()}
    return obj


def deep_merge(base, **update):
    """Recursive merging of `update` dict on `base` dict.

    Instead of updating only top-level keys, `deep_merge` recurses down to
    perform a "nested" update.
    """
    for k, v in update.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], **v)
        else:
            base[k] = v
