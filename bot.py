#! /usr/bin/env python2

import pywikibot
import re

# For images in title, upload to an imgur album?

WEBSITE = pywikibot.Site("en", "wowwiki")
# Check for this one before FANCY_ITALICS, else it could be removed
TABLE_START = "{{tabber"
# Different tabs for tables. See WoW-wiki dog page as an example
TABLE_TAB = ("|", "|")
# This is only relevent while between the {{ braces of a table ({{tabber ...}})
# Also notes that this starts BEFORE the actual section name (i.e: ;Section Title)
TABLE_SECTION = ";"
# Want to remove FANCY_ITALICS, not relevant for summary.
# Please note that these also host the {citation needed} represented as {{fact}}
FANCY_ITALICS = ("{{", "}}")
NORMAL_ITALICS = ("''", "''")
# This also includes links to images so check for [[File:... before stripping the rest
# Aso, the text (not the link) is ALWAYS the first (and sometimes only) item after
# the first "[["
LINK = ("[[", "]]")
# This is the seperator between the displayed text and the url/wiki link
LINK_SEPERATOR = "|"
# This is what begins a wiki link to an image, with the image url right after it
# Followed by the placement on the page
IMAGE_LINK_START = "[[File:"
# This is the formatter for a citation link, which should generally be ignored
CITATION_LINK_START = "{{Cite|"
SECTION_TITLE = ("==", "==")
# There should be NO newlines seperating these for one contiguous list
LIST = ("*", "")
# This is a list of the tupled formatting above to easily iterate over

def get_raw_page(page_title):
    """Gets the raw response from the wiki page. See the output for the formatting"""
    return pywikibot.Page(site, page_title).text

def strip_formatting(page_text, formatting=(LINK,)):
    """Strips the formatting that the wiki has, returns only the plain text of the
    document. All of the link information, including images, is lost"""
    stripped_text = ""
    for line in page_text.splitlines():
        for wrapper in formatting:
            start, end = wrapper
            #line = re.sub(start+"[^"+end+"]+"+end, "", line)
            line = line.replace(start, "")
            line = line.replace(end, "")
        stripped_text += line + "\n"
    return stripped_text

def unlink_links(page_text):
    """Removes the formatting around links, but retains the text that is presented
    to the viewer, so the link now functions as plaintext"""
    link_beginning, link_end = LINK
    page_lines= page_text.splitlines()
    unlinked_text = ""
    for index, line in enumerate(page_lines):
        if link_beginning in line and all(map(lambda x: x not in line, (TABLE_START, IMAGE_LINK_START, CITATION_LINK_START))):
            if LINK_SEPERATOR in line:
                text_start = line.index(link_beginning) + len(link_beginning)
                text_end = line.index(LINK_SEPERATOR)
                # Save what comes before the link
                text_before_link = line[:line.index(link_beginning)]
                text_end = line.index(link_end)
                # Save what comes after the link as well
                text_after_link = line[line.index(link_end) + len(link_end):]
                line = line[text_start:text_end]
                # If there is a link included, make that the seperator
                line = line[:text_end]
                # Join the parts after and before the link to the altered text
                line = text_before_link + line + text_after_link
        unlinked_text += line + "\n"
    return unlinked_text

def redditify(page_text):
    wiki_to_reddit = {
            FANCY_ITALICS:  ("_", "_"),
            NORMAL_ITALICS: ("_", "_"),
            SECTION_TITLE:  ("## ", ""),
            LIST:           ("* ", ""),
            }
    stripped_text = ""
    for line in page_text.splitlines():
        for wiki_wrapper, reddit_wrapper in wiki_to_reddit.items():
            wiki_start, wiki_end = wiki_wrapper
            reddit_start, reddit_end = reddit_wrapper
            if wiki_start in line and wiki_end in line:
                if wiki_start == wiki_end: # If both sides are equal,
                    # Change only the first one
                    line = line.replace(wiki_start, reddit_start, 1)
                else:
                    line = line.replace(wiki_start, reddit_start)
                line = line.replace(wiki_end, reddit_end)
        stripped_text += line + "\n"
    return stripped_text

def get_section(raw_page, section=None):
    """Returns the summary from the given raw page. If section is given and not None,
    then the summary is taken from that section (if present) instead of the default
    (which is the first non-italicised paragraph)"""
    text = strip_formatting(raw_page)
