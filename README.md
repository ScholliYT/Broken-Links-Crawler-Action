# Broken-Links-Crawler-Action


This action checks a website for broken links like 404...

## Inputs

### `website_url`

**Optional** The url of the website to check. Defaults to the homepage url of the repository (description). If that url is not set you'll have to set it in the yml (The piority of GitHub's homepage url is higher than the parameter).

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
