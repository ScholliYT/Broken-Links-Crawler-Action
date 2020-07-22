# Broken-Links-Crawler-Action
This action checks all links on a website. It will detect broken links i.e. links that return HTTP Code 403, 404...
Check the logs to see which links are broken and consequently cause this action to fail. 

based on this work: https://github.com/healeycodes/Broken-Link-Crawler
## Inputs

### `website_url`

**Required** The url of the website to check.

### `verbose`

**Optional** Turn verbose mode on/off (default false).

### `max_retry_time`

**Optional** Maximum time for request retries (default 30).

### `max_retries`

**Optional** Maximum request retry count (default 4).

## Outputs

## Example usage
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v2.0.0
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  verbose: 'true'
  max_retry_time: 30
  max_retries: 5
```
