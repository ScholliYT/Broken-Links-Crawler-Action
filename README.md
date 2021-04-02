![social-preview.png](social-preview.png)

# Broken-Links-Crawler-Action
This action checks all links on a website. It will detect broken links i.e. links that return HTTP Code 403, 404...
Check the logs to see which links are broken and consequently cause this action to fail. 

Based on this work: https://github.com/healeycodes/Broken-Link-Crawler  
**Demo: https://github.com/ScholliYT/devportfolio/actions?query=workflow%3A%22Site+Reliability%22**
## Inputs

### `website_url`

**Required** The url of the website to check.  You can provide a comma separated list of urls if you would like to 
crawl multiple websites.

### `include_url_prefix`

**Optional** Comma separated list of url prefixes to include. You may only want to crawl urls that use "https://".

### `exclude_url_prefix`

**Optional** Comma separated list of url prefixes to exclude (default mailto:,tel:). Some sites do not respond properly to bots and you might want to exclude those known sites to prevent a failed build. 

### `include_url_suffix`

**Optional** Comma separated list of url suffixes to include. You may only want to crawl urls that end with ".html".

### `exclude_url_suffix`

**Optional** Comma separated list of url suffixes to exclude. You may want to skip images by using ".jpg,.gif,.png".

### `include_url_contained`

**Optional** Comma separated list of url substrings to include. You may only want to crawl urls that are hosted on your primay
domain, so you could use "mydomain.com", which would include all of your subdomains, regardless the protocol you use.

### `exclude_url_contained`

**Optional** Comma separated list of url substrings to exclude. You may want to skip specific domains for external links that
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

## Outputs

## Example usage
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v2.1.1
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  exclude_url_prefix: 'mailto:,https://www.linkedin.com,https://linkedin.com'
  verbose: 'true'
  max_retry_time: 30
  max_retries: 5
```

## Dev

The easiest way to run this action locally is to use Docker. Just build a new image and pass the correct env. variables to it. 
```
docker build --tag broken-links-crawler-action:latest .
docker run -e INPUT_WEBSITE_URL="https://github.com/ScholliYT/Broken-Links-Crawler-Action" -e INPUT_VERBOSE="true" -e INPUT_MAX_RETRY_TIME=30 -e INPUT_MAX_RETRIES=5 -e INPUT_EXCLUDE_URL_PREFIX="mailto:,https://www.linkedin.com,https://linkedin.com" broken-links-crawler-action:latest
```
### Automated Testing

You can run the full suite of automated tests on your local machine by using the "act" tool to simulate the github workflow action that executs during commit, more information here:  
https://github.com/nektos/act

### Running linting and code formatting checks

You can run linting and code formatting checks using the `flake8` command:
```
flake8 . --count --show-source --max-complexity=10 --statistics
```

### Running Tests

You can run tests using the `pytest` command:
```
pytest --cov=deadseeker --cov-fail-under=95 --cov-branch --cov-report=term-missing
```

To generate an html report that visually displays uncovered lines, use this version:
```
pytest --cov=deadseeker --cov-fail-under=95 --cov-branch --cov-report=term-missing --cov-report=html
```