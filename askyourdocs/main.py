import argparse
import logging
import os
import sys

from askyourdocs import Environment, Service
from askyourdocs.settings import SETTINGS
import askyourdocs.storage.cli as srge_cli
from askyourdocs.storage.base import StorageService
import askyourdocs.modelling.cli as mdl_cli
from askyourdocs.modelling.base import ModellingService
import askyourdocs.pipeline.cli as ppln_cli
from askyourdocs.pipeline.base import PipelineService

SERVICES = {
    'storage': {'name': 'storage', 'help': 'Storage services', 'cli': srge_cli, 'service': StorageService},
    'modelling': {'name': 'modelling', 'help': 'Modelling services', 'cli': mdl_cli, 'service': ModellingService},
    'pipeline': {'name': 'pipeline', 'help': 'Pipeline services', 'cli': ppln_cli, 'service': PipelineService},
}


def parse_args(args_) -> Environment:
    # Create global parser for logs
    global_parser = argparse.ArgumentParser(add_help=False)
    group = global_parser.add_argument_group('global options')
    group.add_argument("--log_level",
                       default=os.getenv("LOG_LEVEL", "INFO"),
                       help="log level (%(default)s)")

    parser = argparse.ArgumentParser(description="AskYourDocs", parents=[global_parser])
    serv_subprs = parser.add_subparsers(help="Services", dest="service", required=True)

    # Adding all service subparser
    for srv in SERVICES.values():
        sub_prs = serv_subprs.add_parser(srv['name'], help=srv['help'], parents=[global_parser])
        srv['cli'].add_parser(sub_prs)

    # Parse arguments
    kwargs = vars(parser.parse_args(args_))

    # Logging
    fmt = logging.Formatter('%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s')
    log_level = kwargs['log_level'].upper()
    num_log_level = getattr(logging, log_level, None)
    if not isinstance(num_log_level, int):
        raise ValueError(f'Invalid log level: {log_level}')  # pragma: no cover
    handler = logging.StreamHandler()
    handler.setFormatter(fmt=fmt)
    handler.setLevel(level=num_log_level)
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    # Generate and return Context object
    environment = Environment(**kwargs)
    return environment


def run(args_):
    environment = parse_args(args_)
    service = SERVICES[environment.service]['service'](environment=environment, settings=SETTINGS)     # type: Service
    service.apply()


def main():
    run(sys.argv[1:])
