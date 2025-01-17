# NY Post News Scraper

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
git clone https://github.com/yourusername/nypost-crypto-scraper.git
cd nypost-crypto-scraper
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

<<<<<<< HEAD
=======
selenium>=4.0.0
beautifulsoup4>=4.9.3
aiohttp>=3.8.1
asyncio>=3.4.3

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring their use complies with NY Post's terms of service and applicable laws.
>>>>>>> b714f9d0f4e2e1540f190b0ad8d5fd04d2a068d1
