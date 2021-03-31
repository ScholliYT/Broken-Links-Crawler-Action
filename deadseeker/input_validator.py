import validators
import os


class ValidatedInput:
    def __init__(self, website_urls):
        self.website_urls = website_urls


class InputValidator:
    def validateInput(self) -> ValidatedInput:
        website_url = os.environ.get('INPUT_WEBSITE_URL')
        assert website_url, \
            "'INPUT_WEBSITE_URL' environment variable expected to be provided!"
        website_urls = [x.strip() for x in website_url.split(',')]
        for url in website_urls:
            assert validators.url(url), \
                f"Invalid url provided: {url}"
        return ValidatedInput(website_urls)
