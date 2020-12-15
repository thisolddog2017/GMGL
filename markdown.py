import re

md_link_pat = re.compile(r'\[([^][]+)\]\([^)]+\)')
def markdown_to_plaintext(md):
    # NOTE only processing links for now
    return md_link_pat.sub(r'\1', md)
