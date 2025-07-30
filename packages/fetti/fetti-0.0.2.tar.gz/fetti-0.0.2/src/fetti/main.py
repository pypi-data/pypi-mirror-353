import os
import re
import subprocess
import tomllib
from collections.abc import Sequence
from typing import Any

import click

INTERPOLATION_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")

# Maximum number of additional passes for iterative interpolation
# beyond the number of variables. This is a safety margin to ensure
# convergence for chained interpolations (e.g., A=${B}, B=${C_ENV})
# and to handle cases where the order of processing items in a
# dictionary during a pass might require an extra pass for a dependency
# to be resolved. A small number is usually sufficient.
INTERPOLATION_PASS_MARGIN = 5


def flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "_"
) -> dict[str, Any]:
    """
    Flattens a nested dictionary.

    Keys are converted to uppercase and joined with the separator.
    Example: {"db": {"host": "localhost"}} -> {"DB_HOST": "localhost"}
    """
    items: dict[str, Any] = {}

    prefix_for_this_level = f"{parent_key.upper()}{sep}" if parent_key else ""

    for k, v in d.items():
        current_key_part = k.upper()
        new_key = f"{prefix_for_this_level}{current_key_part}"

        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def interpolate(value: Any, context_vars: dict[str, Any]) -> Any:
    """
    Interpolates string values using ${VAR} syntax.

    VAR is looked up in `context_vars` first, then in `os.environ`.
    If not found in either, it resolves to an empty string.
    Non-string values are returned as is.
    """
    if not isinstance(value, str):
        return value

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        # Lookup order:
        # 1. Other variables from the (flattened) config
        # 2. Existing OS environment variables
        # 3. Default to empty string
        if key in context_vars:
            return str(
                context_vars[key]
            )  # Ensure string conversion for resolved value
        return os.environ.get(key, "")

    return INTERPOLATION_PATTERN.sub(replacer, value)


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        "help_option_names": ["-h", "--help"],
    }
)
@click.argument(
    "file",
    type=click.Path(
        exists=True, readable=True, dir_okay=False, resolve_path=True
    ),
)
@click.option(
    "--namespace",
    "-n",
    default=None,
    help=(
        "Isolate environment variables to a top-level TOML table "
        "(e.g., [table])."
    ),
)
@click.option(
    "--key",
    "-k",
    default=None,
    help=(
        "Filter to a sub-table (e.g., 'subtable' for [table.subtable]). "
        "If no command is given, extracts the key's value instead."
    ),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help=(
        "Print the resolved environment variables (from TOML) before "
        "running the command."
    ),
)
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(
    ctx: click.Context,
    file: str,
    namespace: str | None,
    key: str | None,
    verbose: bool,  # noqa: FBT001
    command: Sequence[str],
):
    """
    Load TOML config from FILE and run COMMAND with values as
    environment variables.

    Nested TOML keys are flattened (e.g., [a.b] c=1 -> A_B_C=1).
    String values can interpolate other config variables or existing
    environment variables using ${VAR_NAME} syntax.
    """
    try:
        with open(file, "rb") as f:
            config_data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        click.secho(
            f"Error: Failed to parse TOML file '{file}': {e}",
            fg="red",
            err=True,
        )
        ctx.exit(1)
    except OSError as e:
        click.secho(
            f"Error: Could not read file '{file}': {e}", fg="red", err=True
        )
        ctx.exit(1)

    if namespace:
        if namespace not in config_data:
            click.secho(
                f"Error: Namespace '{namespace}' not found in TOML "
                f"file '{file}'.",
                fg="red",
                err=True,
            )
            ctx.exit(1)
        current_config_scope = config_data[namespace]
        if not isinstance(current_config_scope, dict):
            click.secho(
                f"Error: Namespace '{namespace}' in '{file}' "
                "is not a table/dictionary (found type: "
                f"{type(current_config_scope).__name__}).",
                fg="red",
                err=True,
            )
            ctx.exit(1)
        parent_for_flattening = namespace
    else:
        current_config_scope = config_data
        parent_for_flattening = ""

    if not isinstance(current_config_scope, dict):
        scope_name = (
            f"namespace '{namespace}'"
            if namespace
            else "root of the TOML file"
        )
        click.secho(
            f"Error: The configuration under {scope_name} in '{file}' "
            "is not a table/dictionary (found type: "
            f"{type(current_config_scope).__name__}).",
            fg="red",
            err=True,
        )
        ctx.exit(1)

    flat_config_vars = flatten_dict(
        current_config_scope,
        parent_key=parent_for_flattening,
        sep="_"
    )
    resolved_vars: dict[str, str] = {
        str(k): str(v) for k, v in flat_config_vars.items()
    }

    # Define number of variables (for dependency chains) + a safety margin.
    max_interpolation_passes = len(resolved_vars) + INTERPOLATION_PASS_MARGIN
    for _pass_num in range(max_interpolation_passes):
        changed_in_this_pass = False
        next_resolved_vars: dict[str, str] = {}

        for k_res, v_to_interpolate in resolved_vars.items():
            interpolated_value = interpolate(v_to_interpolate, resolved_vars)
            str_interpolated_value = str(interpolated_value)

            if str_interpolated_value != v_to_interpolate:
                changed_in_this_pass = True
            next_resolved_vars[k_res] = str_interpolated_value

        resolved_vars = next_resolved_vars

        if not changed_in_this_pass:
            break

    vars_for_subprocess = resolved_vars

    if key:
        if command:
            # Filter environment to sub-table specified by --key
            key_prefix = (
                f"{parent_for_flattening.upper()}_" if parent_for_flattening else ""
            )
            key_prefix += f"{key.upper()}_"

            vars_for_subprocess = {
                k: v
                for k, v in resolved_vars.items()
                if k.startswith(key_prefix)
            }

            if not vars_for_subprocess and verbose:
                click.secho(
                    f"Warning: --key '{key}' did not match any variables "
                    f"with prefix '{key_prefix}'. The subprocess will "
                    "receive no variables from the config.",
                    fg="yellow",
                    err=True,
                )
        else:
            # Get a single value (no command was provided)
            lookup_key = key.upper()
            if lookup_key in resolved_vars:
                click.echo(resolved_vars[lookup_key])
                ctx.exit(0)
            else:
                click.secho(
                    f"Error: Key '{key}' not found in the resolved "
                    "configuration.",
                    fg="red",
                    err=True,
                )
                ctx.exit(1)

    if not command:
        # This branch is reached if NO command was given (and no --key for value lookup)
        click.secho(
            "Error: No command provided to execute.", fg="red", err=True
        )
        click.echo(ctx.get_help(), err=True)
        ctx.exit(2)

    effective_env = os.environ.copy()
    effective_env.update(vars_for_subprocess)

    if verbose:
        if vars_for_subprocess:
            output_vars = "\n".join(
                f"  {k}={v}" for k, v in vars_for_subprocess.items()
            )
            click.secho(
                "Augmenting environment with (from TOML config):\n"
                + output_vars,
                fg="green",
                err=True,
            )
        else:
            click.secho(
                "No environment variables derived from the TOML "
                "config (or selected namespace/key is empty).",
                fg="yellow",
                err=True,
            )
        click.secho(
            f"Running command: {' '.join(command)}\n", fg="green", err=True
        )

    try:
        process = subprocess.run(  # noqa: S603
            command, env=effective_env, check=False
        )
        # We use check=False and then explicitly exit with the process's
        # return code This allows the subprocess to print its own errors
        # to stderr/stdout naturally.
        ctx.exit(process.returncode)
    except (
        subprocess.CalledProcessError
    ) as e:
        click.secho(
            f"Command '{' '.join(command)}' failed unexpectedly "
            f"with error: {e}",
            fg="red",
            err=True,
        )
        ctx.exit(e.returncode)
    except FileNotFoundError:
        click.secho(
            f"Error: Command not found: '{command[0]}'. Please ensure "
            "it is in your PATH.",
            fg="red",
            err=True,
        )
        ctx.exit(127)
    except (
        OSError
    ) as e:
        click.secho(
            f"Error running command '{' '.join(command)}': {e}",
            fg="red",
            err=True,
        )
        ctx.exit(1)


if __name__ == "__main__":
    cli()
