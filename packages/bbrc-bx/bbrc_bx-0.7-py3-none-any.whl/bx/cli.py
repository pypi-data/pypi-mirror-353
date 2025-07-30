import logging as log
import pyxnat
import json
import tempfile
import os.path as op
from bx import parse


def cli_bx():
    """
    Main entry point for the 'bx' command-line utility.

    This function encapsulates the entire logic that was previously
    in the `bin/bx` shell script.
    When 'bx' is run from the terminal, setuptools will execute this function.
    """
    parser = parse.create_parser()
    args = parser.parse_args()
    logger = log.getLogger()
    if args.verbose:
        logger.setLevel(level=log.DEBUG)
    else:
        logger.setLevel(level=log.INFO)

    if not op.isfile(args.config):
        log.error('Configuration file not found (%s)' % args.config)
        ans = input('Do you want to create it? (Y/n) (%s)' % args.config)
        if ans in ['y', 'Y', '']:
            url = 'https://xnat.barcelonabeta.org'
            server = input('Server: [%s]' % url)
            if server == '':
                server = url
            x = pyxnat.Interface(server=server)
            x.save_config(args.config)

        else:
            import sys
            log.info('Please provide a valid configuration file and try again.')
            sys.exit(-1)

    if args.dest is not None:
        dd = args.dest
    else:
        dd = json.load(open(args.config)).get('destination', None)
    if dd is None:
        dd = tempfile.gettempdir()
    log.info('Output folder: %s' % dd)

    x = pyxnat.Interface(config=args.config)

    parse.parse_args(args.command, args.args, x, dd)


def cli_dump():
    """
    Main entry point for the 'dump' command-line utility.

    This function encapsulates the entire logic that was previously
    in the `bin/dump` shell script.
    When 'dump' is run from the terminal, setuptools will execute this function.
    """
    import sys
    from bx import dump

    def dir_path(fp):
        if op.isdir(fp):
            return fp
        else:
            raise NotADirectoryError(fp)

    def create_dump_parser():
        import argparse
        from argparse import RawTextHelpFormatter

        cfgfile = op.join(op.expanduser('~'), '.xnat.cfg')

        desc = 'Run every bx command returning alphanumeric endpoints and store ' \
               'results as a collection of spreadsheets.'
        arg_parser = argparse.ArgumentParser(description=desc,
                                             formatter_class=RawTextHelpFormatter)
        arg_parser.add_argument('--dest', '-d',
                                help='Destination directory',
                                type=dir_path,
                                required=True)
        arg_parser.add_argument('--config', '-c',
                                help='XNAT configuration file',
                                required=False,
                                default=cfgfile)
        arg_parser.add_argument('--python', '--py',
                                help='Python interpreter',
                                default='python',
                                required=False)
        arg_parser.add_argument('--shell', '--sh',
                                help='Shell interpreter',
                                default='/usr/bin/bash',
                                required=False)
        arg_parser.add_argument('--debug',
                                help='Debug mode (dry run)',
                                action='store_true',
                                default=False,
                                required=False)
        arg_parser.add_argument('--verbose', '-v',
                                help='Display verbosal information (optional)',
                                action='store_true',
                                default=False,
                                required=False)
        return arg_parser

    parser = create_dump_parser()
    args = parser.parse_args()
    logger = log.getLogger()
    if args.verbose:
        logger.setLevel(level=log.DEBUG)
    else:
        logger.setLevel(level=log.INFO)

    if not op.isfile(args.config):
        log.error('Configuration file not found (%s)' % args.config)
        sys.exit(-1)

    dump.dump(args.dest, config=args.config, debug=args.debug,
              interpreter=args.python, bash_command=args.shell)


if __name__ == "__main__":
    cli_bx()
