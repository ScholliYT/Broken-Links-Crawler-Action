# Broken-Links-Crawler-Action


This action checks a website for broken links like 404...

## Inputs

### `website_url`

**Required** The url of the website to check.

### `verbose`

**Optional** Turn verbose mode on/off.

## Outputs

### `time`

The time the website was checked.

## Example usage
```yml
uses: ScholliYT/Broken-Links-Crawler-Action@v1.0.0
with:
  website_url: 'https://github.com/ScholliYT/Broken-Links-Crawler-Action'
  verbose: 'true'
```
