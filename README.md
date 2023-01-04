![social-preview.png](social-preview.png)

# Broken-Links-Crawler-Action
This action checks all links on a website. It will detect broken links i.e. links that return HTTP Code 403, 404...
Check the logs to see which links are broken and consequently cause this action to fail. 
In addition to the actual broken URL, the navigation path to that location is also displayed.

Based on this work: https://github.com/healeycodes/Broken-Link-Crawler  
**Demo: https://github.com/ScholliYT/devportfolio/actions?query=workflow%3A%22Site+Reliability%22**

## Inputs

### `website_url`

**Required** The URL of the website to check. You can provide a comma separated list of URLs if you would like to 
crawl multiple websites.

### `include_url_prefix`

**Optional** Comma separated list of URL prefixes to include. You may only want to crawl URLs that use "https://".

### `exclude_url_prefix`

**Optional** Comma separated list of URL prefixes to exclude (default mailto:,tel:). Some sites do not respond properly to bots, and you might want to exclude those known sites to prevent a failed build. 

### `include_url_suffix`

**Optional** Comma separated list of URL suffixes to include. You may only want to crawl URLs that end with ".html".

### `exclude_url_suffix`

**Optional** Comma separated list of URL suffixes to exclude. You may want to skip images by using ".jpg,.gif,.png".

### `include_url_contained`

**Optional** Comma separated list of URL substrings to include. You may only want to crawl URLs that are hosted on your primary
domain, so you could use "mydomain.com", which would include all of your subdomains, regardless the protocol you use.

### `exclude_url_contained`

**Optional** Comma separated list of URL substrings to exclude. You may want to skip specific domains for external links that
you do not want to fetch from, such as "knownadprovider.com".

### `web_agent_string`

**Optional** The string to use for the web agent when crawling pages.  
The default is:  
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36
```

### `verbose`

**Optional** Set logging verbosity level: true/false/yes/no/on/off/debug/info/warning/error/critical (default false).

### `max_retry_time`

**Optional** Maximum seconds for request retries (default 30).

### `max_retries`

**Optional** Maximum request retry count (default 4).

### `max_depth`

**Optional** Maximum levels deep to check, -1 = unlimited depth (default -1).

### `always_get_onsite`

**Optional** By default, the crawler will use a HEAD request first, then will follow up with a GET request if the response is HTML and the URL represents a page on the same site as the root URL. By setting this value to 'true', the crawler will always use a GET request for any onsite URL. (default false).

### `connect_limit_per_host`

**Optional** By default, the crawler will open a maximum of 10 connections per host. This can be useful for when crawling a site that has rate limits. Setting this value to zero will cause an unlimited number of connections per host, but this could inadvertently cause timeout errors if the target server gets overwhelmed with connections. (default 10).

### `search_attrs`

**Optional** The names of HTML element attributes to extract links from. This can be useful if you are crawling a site that uses a library like [lazyload](https://github.com/tuupola/lazyload) to lazy-load images -- you would want to make your search_attrs 'href,src,data-src'. (default 'href,src')

### `resolve_before_filtering`

**Optional** By default, the crawler will apply the includes/excludes filtering criteria to the links as they appear in the HTML source. For example, if a link has a relative URL in the HTML source, then the includes/excludes will be applied to the link in its relative form. By setting this value to true, the crawler will fully resolve the link to its absolute representation before applying the includes/excludes filtering criteria. If you wanted to only crawl links that are prefixed with your site ('http://mysite.com/') then you would set `resolve_before_filtering` to `'true'` and set `include_url_prefix` to `'http://mysite.com/'`. (default false)

## Example usage

### Basic scan with retry
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v3
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  exclude_url_prefix: 'mailto:,https://www.linkedin.com,https://linkedin.com'
  verbose: 'true'
  max_retry_time: 30
  max_retries: 5
  max_depth: 1
```

### Basic scan with retry, only fetches URLs on same site
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v3
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  include_url_prefix: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  resolve_before_filtering: 'true'
  verbose: 'true'
  max_retry_time: 30
  max_retries: 5
  max_depth: 1
```

## Development

The easiest way to run this action locally is to use Docker. Just build a new image and pass the correct environment variables to it. 
```
docker build --tag broken-links-crawler-action:latest .
docker run -e INPUT_WEBSITE_URL="https://github.com/ScholliYT/Broken-Links-Crawler-Action" -e INPUT_VERBOSE="true" -e INPUT_MAX_RETRY_TIME=30 -e INPUT_MAX_RETRIES=5 -e INPUT_MAX_DEPTH=1 -e INPUT_INCLUDE_URL_CONTAINED='ScholliYT/Broken-Links-Crawler-Action' -e INPUT_EXCLUDE_URL_CONTAINED='/tree,/code_menu_contents,/hovercards/citation' -e INPUT_EXCLUDE_URL_PREFIX="mailto:,https://www.linkedin.com,https://linkedin.com" broken-links-crawler-action:latest
```

### Installing test dependencies

Several utilities are used for testing the code out. 
We use [Poetry](https://python-poetry.org/) (version 1.2.2) to manage dependencies.
To install all the required dependencies, please 
use the following command:

```sh
poetry env use python3.11 # in case your system python differs from 3.8, 3.9, 3.10 or 3.11
poetry install # use '--without dev' to install only required dependencies
```

### Pre-commit hook

To execute quality checks automatically during a commit, make sure that the git hook script is set up by
running the following command:

```
poetry run pre-commit install
```

### Automated Testing

You can run the full suite of automated tests on your local machine by using the "act" tool to simulate the GitHub workflow action that executes during commit, more information here:  
https://github.com/nektos/act

### Running linting and code formatting checks

You can run linting and code formatting checks using the `flake8` command:
```
poetry run flake8 . --count --show-source --max-complexity=10 --statistics
```

You can run type linting `mypy` command:
```
poetry run mypy
```

### Running Tests

#### Running Unit Tests

To run the unit tests, use the `pytest` command like this:
```
poetry run pytest -m "not integrationtest" --cov=deadseeker --cov-fail-under=95 --cov-branch --cov-report=term-missing
```

To generate an HTML report that visually displays uncovered lines, use this version:
```
poetry run pytest -m "not integrationtest" --cov=deadseeker --cov-fail-under=95 --cov-branch --cov-report=term-missing --cov-report=html
```

#### Running Integration Tests

To run the unit tests, use the `pytest` command like this:
```
poetry run pytest -m "integrationtest"
```

#### Mutation Testing

Mutation testing changes the real code (creating a 'mutant') and runs all the tests to make sure that at least one test fails. This ensures that your tests are actually effective at testing the code, or it can also reveal unnecessary implementation code that should be refactored. To run mutation testing, use the `poetry run mutmut run` command. For details on missed mutants, run the `poetry run mutmut html` command to generate an HTML report of the missed mutants.
