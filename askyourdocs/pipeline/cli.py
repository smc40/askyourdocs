import argparse

from askyourdocs.storage.cli import strg_url_parser, strge_solr_parser, strge_scrp_parser
from askyourdocs.modelling.cli import mdl_txt_parser


def add_parser(parser: argparse.ArgumentParser):
    ppln_subprs = parser.add_subparsers(help="Pipeline services", dest='pipeline', required=True)
    ppln_subprs.add_parser('add_doc', help='Adding text embedding from document', parents=[strg_url_parser(), strge_scrp_parser(), strge_solr_parser()])
    ppln_subprs.add_parser('add_text', help='Adding text embedding from text', parents=[strg_url_parser(), mdl_txt_parser(), strge_solr_parser()])
