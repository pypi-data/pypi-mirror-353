from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crypto_exchange_news_crawler",
    version="0.1.0",
    author="lowweihong",
    author_email="lowweihong14@gmail.com",
    description="Cryptocurrency exchange announcement news crawler for major crypto exchanges",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lowweihong/crypto_exchange_news_crawler",
    packages=find_packages(),
    keywords=[
        "cryptocurrency", "crypto", "exchange", "news", "crawler", "scraper",
        "bybit", "binance", "bitget", "bitfinex", "xt", "okx", "announcements",
        "trading", "bot", "api", "scrapy", "web-scraping", "market-data",
        "fintech", "blockchain", "defi", "trading-bot", "crypto-news"
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    project_urls={
        "Bug Reports": "https://github.com/lowweihong/crypto-exchange-news-crawler/issues",
        "Source": "https://github.com/lowweihong/crypto-exchange-news-crawler",
        "Documentation": "https://github.com/lowweihong/crypto-exchange-news-crawler#readme",
    },
    include_package_data=True,
    zip_safe=False,
) 