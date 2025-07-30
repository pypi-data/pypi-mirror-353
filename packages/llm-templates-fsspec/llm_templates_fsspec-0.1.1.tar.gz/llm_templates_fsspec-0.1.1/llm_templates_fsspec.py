import json
import os

import fsspec
import yaml

from llm import Template, hookimpl


@hookimpl
def register_template_loaders(register):
    register("fsspec", fsspec_template_loader)


def fsspec_template_loader(template_path: str) -> Template:
    """Load a template from any fsspec URL."""

    cache_dir = os.getenv("LLM_TEMPLATES_FSSPEC_CACHE_DIR")
    storage_options_env = os.getenv("LLM_TEMPLATES_FSSPEC_STORAGE_OPTIONS")
    storage_options = {}

    if storage_options_env:
        try:
            storage_options = json.loads(storage_options_env)
        except json.JSONDecodeError:
            raise ValueError(
                "Invalid JSON in LLM_TEMPLATES_FSSPEC_STORAGE_OPTIONS"
            )

    if cache_dir:
        storage_options["cache_storage"] = cache_dir

    with fsspec.open(template_path, mode="r", **storage_options) as fp:
        content = fp.read()

    try:
        loaded = yaml.safe_load(content)

        if isinstance(loaded, str):
            return Template(name=template_path, prompt=loaded)
        else:
            return Template(name=template_path, **loaded)
    except yaml.YAMLError as e:
        raise ValueError(
            f"Failed to parse YAML from {template_path}: {e}"
        )
