import argparse
import os


def strg_url_parser():
    parser = argparse.ArgumentParser(add_help=False)

    group = parser.add_argument_group('URL options')
    group.add_argument('--tika_url', dest='tika_url', help='Apache Tika host', default=os.getenv('TIKA_URL'))
    group.add_argument('--solr_url', dest='solr_url', help='Apache Solr host', default=os.getenv('SOLR_URL'))
    group.add_argument('--zk_urls', dest='zk_urls', help='Comma-separated list of ZooKeeper hosts.', default=os.getenv('ZK_URLS'))
    return parser


def strge_solr_parser():
    parser = argparse.ArgumentParser(add_help=False)

    group = parser.add_argument_group('Solr data management options')
    group.add_argument('--collection', '-c', dest='collection', help='Collection name')
    group.add_argument('--commit', dest='commit', action='store_true', help='Commit changes to solr')
    return parser


def strge_scrp_parser():
    parser = argparse.ArgumentParser(add_help=False)

    group = parser.add_argument_group('Text extraction options')
    group.add_argument('--filename', '-f', dest='filename', help='Filename')
    group.add_argument('--source', '-s', dest='source', help='Source')
    return parser


def add_parser(parser: argparse.ArgumentParser):

    strge_subprs = parser.add_subparsers(help="Storage services", dest="storage", required=True)

    # Storage service
    strge_subprs.add_parser('add', help='Adding a document', parents=[strg_url_parser(), strge_scrp_parser(), strge_solr_parser()])

    # Solr service
    strge_subprs.add_parser('migration', help='Migration of collection', parents=[strg_url_parser(), strge_solr_parser()])
    strge_srch_subprs = strge_subprs.add_parser('search', help='Search inside collection', parents=[strg_url_parser(), strge_solr_parser()])
    strge_srch_subprs.add_argument('--query', '-q', dest='query', help='Search query', required=True)

    # Scraping service
    strge_subprs.add_parser('extraction', help='Extract text from source', parents=[strg_url_parser(), strge_scrp_parser()])
