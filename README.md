# Broken-Links-Crawler-Action

This action checks all links on a website. It will detect broken links i.e. links that return HTTP Code 403, 404...
Check the logs to see which links are broken and consequently cause this action to fail. 
## Inputs

### `website_url`

**Required** The url of the website to check.

### `verbose`

**Optional** Turn verbose mode on/off. Default false.

## Outputs

## Example usage
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v2.0.0
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  verbose: 'true'
```
