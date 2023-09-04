import argparse


def mdl_txt_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--text', '-t', dest='text', help='Text string')
    return parser


def add_parser(parser: argparse.ArgumentParser):
    mdl_subprs = parser.add_subparsers(help="Modelling services", dest="modelling", required=True)

    mdl_subprs.add_parser('embedding', help='Text embedding by llm', parents=[mdl_txt_parser()])
    mdl_subprs.add_parser('tokenization', help='Text tokenization', parents=[mdl_txt_parser()])
    mdl_subprs.add_parser('add', help='Migration of text', parents=[mdl_txt_parser()])
