# NY Post Crypto News Scraper

A high-performance web scraper that monitors NY Post for cryptocurrency-related news articles.

## Features
- Automated crypto news detection
- Multi-keyword monitoring
- Parallel article processing
- JSON output with timestamps
- Comprehensive logging system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/eoin-hermeneutic/test_nypost_scraper.git
cd test_nypost_scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ChromeDriver:
- Windows: `choco install chromedriver`
- Mac: `brew install chromedriver`
- Linux: `apt install chromium-chromedriver`

## Usage

```bash
python test_nypost_scraper.py
```

## Output Files

- Articles: `nypost_crypto_articles_YYYYMMDD_HHMMSS.json`
- Logs: `nypost_scraper_YYYYMMDD_HHMMSS.log`

## Dependencies

- Python 3.7+
- selenium >= 4.0.0
- beautifulsoup4 >= 4.9.3
- aiohttp >= 3.8.1
- asyncio >= 3.4.3

## License

MIT License - See [LICENSE](LICENSE) file

## Disclaimer

For educational and research purposes only. Users must comply with NY Post's terms of service.
