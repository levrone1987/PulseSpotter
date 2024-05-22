import re


def get_page_number(url):
    match = re.search(r'page=(\d+)', url)
    if match:
        return int(match.group(1))
    else:
        return 1
