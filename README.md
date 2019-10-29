# Broken-Links-Crawler-Action

This action checks all links on a website. It will detect broken links i.e. links that return HTTP Code 403, 404...

## Inputs

### `website_url`

**Required** The url of the website to check.

### `verbose`

**Optional** Turn verbose mode on/off. Default false.

## Outputs

## Example usage
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v1.1.2
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  verbose: 'true'
```
