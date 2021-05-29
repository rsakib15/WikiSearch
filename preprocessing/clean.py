from extract import Extractor, ignoreTag, resetIgnoredTags


def clean_markup(markup, keep_links=False, ignore_headers=True):
    if not keep_links:
        ignoreTag('a')

    extractor = Extractor(0, '', [])

    paragraphs = extractor.clean_text(markup,mark_headers=True,expand_templates=False,escape_doc=True)
    resetIgnoredTags()

    if ignore_headers:
        paragraphs = filter(lambda s: not s.startswith('## '), paragraphs)

    return paragraphs
