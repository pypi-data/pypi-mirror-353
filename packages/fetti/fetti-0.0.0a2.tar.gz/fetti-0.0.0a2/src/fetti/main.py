import os
import re
import subprocess
import tomllib

import click


def flatten_dict(d, parent_key="", sep="_"):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}".upper() if parent_key else k.upper()
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def interpolate(value, flat_dict):
    pattern = re.compile(r"\$\{([A-Z0-9_]+)\}")

    def replacer(match):
        key = match.group(1)
        return str(flat_dict.get(key, os.environ.get(key, "")))

    return pattern.sub(replacer, value) if isinstance(value, str) else value


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    }
)
@click.argument("file", type=click.Path(exists=True, readable=True))
@click.option(
    "--namespace",
    "-n",
    help="Top-level key in TOML to isolate (e.g., [database])",
)
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(ctx, file, namespace, command):
    """
    Load TOML config and run COMMAND with values as environment variables.
    """
    with open(file, "rb") as f:
        config = tomllib.load(f)

    if namespace:
        config = config.get(namespace)
        if config is None:
            click.echo(
                f"Namespace '{namespace}' not found in {file}.",
                err=True,
            )
            ctx.exit(1)

    flat = flatten_dict(config)
    resolved = {k: interpolate(v, flat) for k, v in flat.items()}

    env = os.environ.copy()
    env.update(resolved)

    if not command:
        click.echo("No command provided after '--'.", err=True)
        ctx.exit(1)

    click.echo(
        f"Running command with environment variables:\n{resolved}\n",
        err=True,
    )

    try:
        subprocess.run(command, env=env, check=True)  # noqa: S603
    except subprocess.CalledProcessError as e:
        click.echo(f"Command failed with exit code {e.returncode}", err=True)
        ctx.exit(e.returncode)


if __name__ == "__main__":
    cli()
