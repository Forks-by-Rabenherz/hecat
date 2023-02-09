"""hecat CLI entrypoint"""
import sys
import argparse
import logging
from .utils import load_yaml_data
from .importers import import_markdown_awesome, import_shaarli_json
from .processors import add_github_metadata, awesome_lint, check_github_last_updated, check_urls,download_media
from .exporters import render_markdown_singlepage, render_html_table


LOG_FORMAT = "%(levelname)s:%(filename)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def main():
    """Main loop"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config_file', type=str, default='.hecat.yml', help='configuration file')
    args = parser.parse_args()
    config = load_yaml_data(args.config_file)
    for step in config['steps']:
        logging.info('running step %s', step['name'])
        if step['module'] == 'importers/markdown_awesome':
            import_markdown_awesome(step)
        elif step['module'] == 'importers/shaarli_api':
            import_shaarli_json(step)
        elif step['module'] == 'processors/github_metadata':
            add_github_metadata(step)
        elif step['module'] == 'processors/awesome_lint':
            awesome_lint(step)
            check_github_last_updated(step)
        elif step['module'] == 'processors/url_check':
            check_urls(step)
        elif step['module'] == 'processors/download_media':
            download_media(step)
        elif step['module'] == 'exporters/markdown_singlepage':
            render_markdown_singlepage(step)
        elif step['module'] == 'exporters/html_table':
            render_html_table(step)
        else:
            logging.error('step %s: unknown module %s', step['name'], step['module'])
            sys.exit(1)
    logging.info('all steps completed')

if __name__ == "__main__":
    main()
