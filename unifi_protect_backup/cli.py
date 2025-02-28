"""Console script for unifi_protect_backup."""

import asyncio

import click
from aiorun import run

from unifi_protect_backup import __version__
from unifi_protect_backup.unifi_protect_backup import UnifiProtectBackup
from unifi_protect_backup.utils import human_readable_to_float

DETECTION_TYPES = ["motion", "person", "vehicle", "ring"]


def _parse_detection_types(ctx, param, value):
    # split columns by ',' and remove whitespace
    types = [t.strip() for t in value.split(',')]

    # validate passed columns
    for t in types:
        if t not in DETECTION_TYPES:
            raise click.BadOptionUsage("detection-types", f"`{t}` is not an available detection type.", ctx)

    return types


@click.command()
@click.version_option(__version__)
@click.option('--address', required=True, envvar='UFP_ADDRESS', help='Address of Unifi Protect instance')
@click.option('--port', default=443, envvar='UFP_PORT', show_default=True, help='Port of Unifi Protect instance')
@click.option('--username', required=True, envvar='UFP_USERNAME', help='Username to login to Unifi Protect instance')
@click.option('--password', required=True, envvar='UFP_PASSWORD', help='Password for Unifi Protect user')
@click.option(
    '--verify-ssl/--no-verify-ssl',
    default=True,
    show_default=True,
    envvar='UFP_SSL_VERIFY',
    help="Set if you do not have a valid HTTPS Certificate for your instance",
)
@click.option(
    '--rclone-destination',
    required=True,
    envvar='RCLONE_DESTINATION',
    help="`rclone` destination path in the format {rclone remote}:{path on remote}."
    " E.g. `gdrive:/backups/unifi_protect`",
)
@click.option(
    '--retention',
    default='7d',
    show_default=True,
    envvar='RCLONE_RETENTION',
    help="How long should event clips be backed up for. Format as per the `--max-age` argument of "
    "`rclone` (https://rclone.org/filtering/#max-age-don-t-transfer-any-file-older-than-this)",
)
@click.option(
    '--rclone-args',
    default='',
    envvar='RCLONE_ARGS',
    help="Optional extra arguments to pass to `rclone rcat` directly. Common usage for this would "
    "be to set a bandwidth limit, for example.",
)
@click.option(
    '--detection-types',
    envvar='DETECTION_TYPES',
    default=','.join(DETECTION_TYPES),
    show_default=True,
    help="A comma separated list of which types of detections to backup. "
    f"Valid options are: {', '.join([f'`{t}`' for t in DETECTION_TYPES])}",
    callback=_parse_detection_types,
)
@click.option(
    '--ignore-camera',
    'ignore_cameras',
    multiple=True,
    envvar="IGNORE_CAMERAS",
    help="IDs of cameras for which events should not be backed up. Use multiple times to ignore "
    "multiple IDs. If being set as an environment variable the IDs should be separated by whitespace.",
)
@click.option(
    '--file-structure-format',
    envvar='FILE_STRUCTURE_FORMAT',
    default="{camera_name}/{event.start:%Y-%m-%d}/{event.end:%Y-%m-%dT%H-%M-%S} {detection_type}.mp4",
    show_default=True,
    help="A Python format string used to generate the file structure/name on the rclone remote."
    "For details of the fields available, see the projects `README.md` file.",
)
@click.option(
    '-v',
    '--verbose',
    count=True,
    help="How verbose the logging output should be."
    """
    \n
    None: Only log info messages created by `unifi-protect-backup`, and all warnings

    -v: Only log info & debug messages created by `unifi-protect-backup`, and all warnings

    -vv: Log info & debug messages created by `unifi-protect-backup`, command output, and all warnings

    -vvv Log debug messages created by `unifi-protect-backup`, command output, all info messages, and all warnings

    -vvvv: Log debug messages created by `unifi-protect-backup` command output, all info messages,
all warnings, and websocket data

    -vvvvv: Log websocket data, command output, all debug messages, all info messages and all warnings
""",
)
@click.option(
    '--sqlite_path',
    default='events.sqlite',
    envvar='SQLITE_PATH',
    help="Path to the SQLite database to use/create",
)
@click.option(
    '--color-logging/--plain-logging',
    default=False,
    show_default=True,
    envvar='COLOR_LOGGING',
    help="Set if you want to use color in logging output",
)
@click.option(
    '--download-buffer-size',
    default='512MiB',
    show_default=True,
    envvar='DOWNLOAD_BUFFER_SIZE',
    help='How big the download buffer should be (you can use suffixes like "B", "KiB", "MiB", "GiB")',
    callback=lambda ctx, param, value: human_readable_to_float(value),
)
def main(**kwargs):
    """A Python based tool for backing up Unifi Protect event clips as they occur."""
    event_listener = UnifiProtectBackup(**kwargs)
    run(event_listener.start())


if __name__ == "__main__":
    main()  # pragma: no cover
