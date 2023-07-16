"""export data to single markdown document suitable for "awesome" lists
- https://github.com/sindresorhus/awesome
- https://gitlab.com/nodiscc/toolbox/-/raw/master/DOC/SCREENSHOTS/rJyCEFw.png

$ git clone https://github.com/awesome-selfhosted/awesome-selfhosted tests/awesome-selfhosted
$ git clone https://github.com/awesome-selfhosted/awesome-selfhosted-data tests/awesome-selfhosted-data
$ $EDITOR .hecat.yml
$ hecat

# .hecat.yml
steps:
  - name: export YAML data to single-page markdown
    module: exporters/markdown_singlepage
    module_options:
      source_directory: tests/awesome-selfhosted-data # source/YAML data directory, see structure below
      output_directory: tests/awesome-selfhosted # output directory
      output_file: README.md # output markdown file
      markdown_header: markdown/header.md # (optional, default none) path to markdown file to use as header (relative to source_directory)
      markdown_footer: markdown/footer.md # (optional, default none) path to markdown file to use as footer (relative to source_directory)
      back_to_top_url: '#awesome-selfhosted' # (optional, default #) the URL/anchor to use in 'back to top' links
      exclude_licenses: # (optional, default none) do not write software items with any of these licenses to the output file
        - 'CC-BY-NC-4.0'
        - '⊘ Proprietary'
        - 'SSPL-1.0'

  - name: export awesome-selfhosted markdown (non-free)
    module: exporters/markdown_singlepage
    module_options:
      source_directory: tests/awesome-selfhosted-data
      output_directory: tests/awesome-selfhosted
      output_file: non-free.md
      markdown_header: markdown/non-free-header.md
      back_to_top_url: '##awesome-selfhosted---non-free-software'
      render_empty_categories: False # (optional, default True) do not render categories which contain 0 items
      render_category_headers: False # (optional, default True) do not render category headers (description, related categories, external links...)
      include_licenses: # (default none) only render items matching at least one of these licenses (cannot be used together with exclude_licenses)
        - '⊘ Proprietary'
        - 'BUSL-1.1'
        - 'CC-BY-NC-4.0'
        - 'CC-BY-NC-SA-3.0'
        - 'CC-BY-ND-3.0'
        - 'Commons-Clause'
        - 'DPL'
        - 'SSPL-1.0'
        - 'DPL'
        - 'Elastic-1.0'


Output directory structure:
└── README.md

Source YAML directory structure:
├── markdown
│   ├── header.md # markdown footer to render in the final single-page document (markdown_header module option)
│   └── footer.md # markdown header to render in the final single-page document (markdown_footer module option)
├── software
│   ├── mysoftware.yml # .yml files containing software data
│   ├── someothersoftware.yml
│   └── ...
├── platforms
│   ├── bash.yml # .yml files containing language/platforms data
│   ├── python.yml
│   └── ...
├── tags
│   ├── groupware.yml # .yml files containing tags/categories data
│   ├── enterprise-resource-planning.yml
│   └── ...
├── licenses.yml # yaml list of licenses
└── tools

Files containing software data must be formatted as follows:

# software/my-awesome-software.yml
name: "My awesome software" # required
website_url: "https://my.awesome.softwar.e" # required
source_code_url: "https://gitlab.com/awesome/software" # required
description: "A description of my awesome software." # required
licenses: # required, all licenses must be listed in licenses.yml
  - Apache-2.0
  - AGPL-3.0
platforms: # required, all platforms must be listed in platforms/*.yml
  - Java
  - Python
  - PHP
  - Nodejs
  - Deb
  - Docker
tags: # required, all tags must be listed in tags/*.yml
  - Automation
  - Calendar
  - File synchronization
demo_url: "https://my.awesome.softwar.e/demo" # optional
related_software_url: "https://my.awesome.softwar.e/apps" # optional
depends_3rdparty: yes # optional, default no
updated_at: "20200202T20:20:20Z" # optional, auto-generated by processors/github_metadata, last update/commit date
stargazers_count: "999"  # optional, auto-generated, number of stars for github projects

Files containing platforms/languages must be formatted as follows:

name: Document management # required
description: "[Document management systems (DMS)](https://en.wikipedia.org/wiki/Document_management_system) are used to receive, track, manage and store documents and reduce paper" # required, markdown
related_tags: # optional
  - E-books and Integrated Library Systems (ILS)
  - Archiving and Digital Preservation
redirect: # optional, URLs of other collaborative lists which should be used instead
  - https://another.awesome.li.st
  - https://gitlab.com/user/awesome-list
"""

import sys
import logging
import ruamel.yaml
from ..utils import to_kebab_case, load_yaml_data, render_markdown_licenses

yaml = ruamel.yaml.YAML(typ='safe')
yaml.indent(sequence=4, offset=2)

def to_markdown_anchor(string):
    """Convert a section name to a markdown anchor link in the form [Tag name](#tag-name)"""
    anchor_url = to_kebab_case(string)
    markdown_anchor = '[{}](#{})'.format(string, anchor_url)
    return markdown_anchor

def render_markdown_singlepage_category(step, tag, software_list):
    """Render a category for the single page markdown output format"""
    logging.debug('rendering tag %s', tag['name'])
    markdown_redirect = ''
    markdown_related_tags = ''
    markdown_description = ''
    markdown_external_links = ''
    items_count = 0

    # category header rendering
    if step['module_options']['render_category_headers']:
        if 'related_tags' in tag and tag['related_tags']:
            markdown_related_tags = '_Related: {}_\n\n'.format(', '.join(
                to_markdown_anchor(related_tag) for related_tag in tag['related_tags']))
        if 'description' in tag and tag['description']:
            markdown_description = tag['description'] + '\n\n'
        if 'redirect' in tag and tag['redirect']:
            markdown_redirect = '**Please visit {}**\n\n'.format(', '.join(
                '[{}]({})'.format(
                    link['title'], link['url']
            ) for link in tag['redirect']))
        if 'external_links' in tag and tag['external_links']:
            markdown_external_links = '_See also: {}_\n\n'.format(', '.join(
                '[{}]({})'.format(
                    link['title'], link['url']
                ) for link in tag['external_links']))
        markdown_category = '### {}{}{}{}{}{}'.format(
            tag['name'] + '\n\n',
            '**[`^        back to top        ^`](' + step['module_options']['back_to_top_url'] + ')**\n\n',
            markdown_description,
            markdown_redirect,
            markdown_related_tags,
            markdown_external_links
        )
    else:
        markdown_category = '### {}{}'.format(
            tag['name'] + '\n\n',
            '**[`^        back to top        ^`](' + step['module_options']['back_to_top_url'] + ')**\n\n'
        )

    # software list rendering
    for software in software_list:
        if step['module_options']['exclude_licenses']:
            if any(license in software['licenses'] for license in step['module_options']['exclude_licenses']):
                logging.debug("%s has a license listed in exclude_licenses, skipping", software['name'])
                continue
        elif step['module_options']['include_licenses']:
            if not any(license in software['licenses'] for license in step['module_options']['include_licenses']):
                logging.debug("%s does not match any license listed in include_licenses, skipping", software['name'])
                continue
        if software['tags'][0] == tag['name']:
            markdown_list_item = render_markdown_list_item(software)
            logging.debug('adding project %s to category %s', software['name'], tag['name'])
            markdown_category = markdown_category + markdown_list_item
            items_count = items_count + 1
    if (items_count == 0) and not step['module_options']['render_empty_categories']:
        logging.info('category %s is empty, not rendering it', tag['name'])
        return ''

    return markdown_category + '\n\n'


def render_markdown_list_item(software):
    """render a software project info as a markdown list item"""
    # check optional fields
    if 'demo_url' in software:
        markdown_demo = '[Demo]({})'.format(software['demo_url'])
    else:
        markdown_demo = ''
    if not software['source_code_url'] == software['website_url']:
        markdown_source_code = '[Source Code]({})'.format(software['source_code_url'])
    else:
        markdown_source_code = ''
    if 'related_software_url' in software:
        markdown_related_software = '[Clients]({})'.format(
            software['related_software_url'])
    else:
        markdown_related_software = ''
    if 'depends_3rdparty' in software and software['depends_3rdparty']:
        markdown_depends_3rdparty = '`⚠` '
    else:
        markdown_depends_3rdparty = ''
    links_list = [markdown_demo, markdown_source_code, markdown_related_software]
    # remove empty links from list
    links = [link for link in links_list if link]
    markdown_links = ' ({})'.format(', '.join(links)) if links else ''
    # build markdown-formatted list item
    markdown_list_item = '- [{}]({}) {}- {}{} {} {}\n'.format(
        software['name'],
        software['website_url'],
        markdown_depends_3rdparty,
        software['description'],
        markdown_links,
        '`' + '/'.join(software['licenses']) + '`',
        '`' + '/'.join(software['platforms']) + '`'
        )
    return markdown_list_item

def render_markdown_toc(*args):
    """render a markdown-formatted table of contents"""
    markdown = ''
    for i in args:
        markdown += i
    markdown_toc = '\n--------------------\n\n## Table of contents\n\n'
    # DEBT factorize
    for line in markdown.split('\n'):
        if line.startswith('## '):
            toc_entry = '- [{}](#{})\n'.format(line[3:], to_kebab_case(line)[3:])
            markdown_toc = markdown_toc + toc_entry
        if line.startswith('### '):
            toc_entry = '  - [{}](#{})\n'.format(line[4:], to_kebab_case(line)[4:])
            markdown_toc = markdown_toc + toc_entry
    markdown_toc = markdown_toc + '\n--------------------'
    return markdown_toc

def render_markdown_singlepage(step):
    """
    Render a single-page markdown list of all software, grouped by category
    Prepend/append header/footer, categorized list and footer
    A software item is only listed once, under the first item of its 'tags:' list
    """
    # pylint: disable=consider-using-with
    tags = load_yaml_data(step['module_options']['source_directory'] + '/tags', sort_key='name')
    software_list = load_yaml_data(step['module_options']['source_directory'] + '/software')
    licenses = load_yaml_data(step['module_options']['source_directory'] + '/licenses.yml')
    markdown_header = ''
    markdown_footer = ''
    if 'markdown_header' in step['module_options']:
        markdown_header = open(step['module_options']['source_directory'] + '/' + step['module_options']['markdown_header'], 'r').read()
    if 'markdown_footer' in step['module_options']:
        markdown_footer = open(step['module_options']['source_directory'] + '/' + step['module_options']['markdown_footer'], 'r').read()
    markdown_software_list = '## Software\n\n'
    if ('exclude_licenses' in step['module_options']) and ('include_licenses' in step['module_options']):
        logging.error('module options exclude_licenses and include_licenses cannot be used together.')
        sys.exit(1)
    if 'exclude_licenses' not in step['module_options']:
        step['module_options']['exclude_licenses'] = []
    if 'include_licenses' not in step['module_options']:
        step['module_options']['include_licenses'] = []
    if 'back_to_top_url' not in step['module_options']:
        step['module_options']['back_to_top_url'] = '#'
    if 'render_empty_categories' not in step['module_options']:
        step['module_options']['render_empty_categories'] = True
    if 'render_category_headers' not in step['module_options']:
        step['module_options']['render_category_headers'] = True
    for tag in tags:
        markdown_category = render_markdown_singlepage_category(step, tag, software_list)
        markdown_software_list = markdown_software_list + markdown_category
    markdown_licenses = render_markdown_licenses(step, licenses, back_to_top_url=step['module_options']['back_to_top_url'])
    markdown_toc_section = render_markdown_toc(
        markdown_header,
        markdown_software_list,
        markdown_licenses,
        markdown_footer)
    markdown = '{}{}\n\n{}{}\n\n{}'.format(
        markdown_header, markdown_toc_section, markdown_software_list, markdown_licenses, markdown_footer)
    with open(step['module_options']['output_directory'] + '/' + step['module_options']['output_file'], 'w+', encoding="utf-8") as outfile:
        outfile.write(markdown)
