import asyncio
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from datetime import datetime
import json
import logging
import aiohttp

# Configure logging to track script execution and debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'nypost_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

def get_chrome_options():
    """
    Configure Chrome browser options for headless scraping.
    
    Returns:
        Options: Configured Chrome options for optimal scraping performance
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("--disable-extensions")  # Disable extensions
    options.add_argument("--disable-images")  # Disable image loading
    options.add_argument("--blink-settings=imagesEnabled=false")  # Disable image rendering
    return options

async def test_homepage_scan(keywords=None):
    """
    Scan NY Post homepage for articles containing specified keywords.
    
    Args:
        keywords (list): List of keywords to search for in article titles
        
    Returns:
        list: List of dictionaries containing matching article information
    """
    if keywords is None:
        keywords = ["crypto", "bitcoin", "btc", "solana", "sol", "ripple", "xrp"]
    
    driver = webdriver.Chrome(service=Service(), options=get_chrome_options())
    driver.set_page_load_timeout(10)
    driver.implicitly_wait(2)
    
    try:
        print(f"Navigating to NY Post... Looking for headlines with keywords: {keywords}")
        base_url = "https://nypost.com"
        driver.get(base_url)
        
        # Wait for article links to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            print("Found article links")
        except TimeoutException:
            print("No article links found")
            return []
            
        # Parse the page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all article links using multiple selectors
        article_links = (
            soup.find_all('a', class_=lambda x: x and x.startswith('postid-')) or
            soup.find_all('a', href=lambda x: x and '/20' in x)
        )
        
        print(f"Found {len(article_links)} total article links")
        
        # Filter articles based on keywords
        matching_articles = []
        for link in article_links:
            if 'href' in link.attrs:
                url = link['href']
                # Skip shopping and subscription links
                if any(x in url.lower() for x in ['/shopping/', 'tubitv.com', 'subscribe']):
                    continue
                    
                title = link.text.strip()
                # Check if title contains any of the keywords (case insensitive)
                if any(keyword.lower() in title.lower() for keyword in keywords):
                    full_url = urljoin(base_url, url)
                    matching_articles.append({
                        'url': full_url, 
                        'title': title,
                        'matched_keyword': next(keyword for keyword in keywords if keyword.lower() in title.lower())
                    })
                    print(f"Found matching article: {title}")
        
        return matching_articles
    
    finally:
        driver.quit()

async def test_article_parse(url: str, max_retries=2):
    """
    Parse individual article content with retry mechanism.
    
    Args:
        url (str): URL of the article to parse
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        dict: Parsed article content including title, text, and metadata
    """
    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(service=Service(), options=get_chrome_options())
            driver.set_page_load_timeout(10)
            driver.implicitly_wait(2)
            
            print(f"Fetching {url}")
            driver.get(url)
            
            # Wait for article content to load
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                driver.quit()
                continue
            
            # Parse article content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            article_container = soup.find('article')
            
            if article_container:
                title = article_container.find('h1')
                content_paragraphs = article_container.find_all('p')
                
                # Find publish date using multiple selectors
                publish_date = (
                    soup.find('meta', property='article:published_time') or
                    soup.find('meta', property='article:modified_time') or
                    soup.find('time', class_='entry-date') or
                    soup.find('time', class_='published') or
                    soup.find('meta', itemprop='datePublished')
                )
                
                result = {
                    'url': url,
                    'title': title.text.strip() if title else 'Not found',
                    'content': ' '.join([p.text.strip() for p in content_paragraphs]) if content_paragraphs else 'Not found',
                    'publish_date': (publish_date['content'] if publish_date and 'content' in publish_date.attrs
                                   else publish_date['datetime'] if publish_date and 'datetime' in publish_date.attrs
                                   else 'Not found'),
                    'timestamp': datetime.now().isoformat()
                }
                
                driver.quit()
                return result
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Retrying... ({attempt + 2}/{max_retries})")
        
        finally:
            try:
                driver.quit()
            except:
                pass
    
    return None

async def process_articles_parallel(matching_articles):
    """
    Process multiple articles concurrently using asyncio.
    
    Args:
        matching_articles (list): List of articles to process
        
    Returns:
        list: Processed article content
    """
    tasks = []
    for article in matching_articles:
        task = asyncio.create_task(test_article_parse(article['url']))
        tasks.append(task)
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_articles = []
        for article, result in zip(matching_articles, results):
            if result and not isinstance(result, Exception):
                processed_articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'content': result['content'],
                    'publish_date': result['publish_date']
                })
            else:
                print(f"Failed to process article: {article['title']}")
        
        return processed_articles
        
    except Exception as e:
        print(f"Error in parallel processing: {str(e)}")
        return []

async def main():
    """
    Main execution function that coordinates the scraping process.
    """
    start_time = time.time()
    print("Starting article scan and processing...")
    
    # Define crypto-related keywords
    crypto_keywords = ["crypto", "bitcoin", "btc", "solana", "sol", "ripple", "xrp"]
    matching_articles = await test_homepage_scan(keywords=crypto_keywords)
    processed_articles = []
    
    if matching_articles:
        print(f"\nFound {len(matching_articles)} matching articles. Processing in parallel...")
        processed_articles = await process_articles_parallel(matching_articles)
        
        # Print results
        print("\nProcessing Results:")
        for article in processed_articles:
            print(f"\nTitle: {article['title']}")
            print(f"URL: {article['url']}")
            print(f"Date: {article['publish_date']}")
            print(f"Matched Keyword: {article.get('matched_keyword', 'unknown')}")
            print("Content Preview (first 200 chars):")
            print(article['content'][:200] + "...")
    else:
        print("\nNo articles found matching crypto keywords")
    
    # Calculate and display execution time
    end_time = time.time()
    print(f"\nTotal processing time: {end_time - start_time:.2f} seconds")

    # Save results to JSON file
    if processed_articles:
        output_file = f'nypost_crypto_articles_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(processed_articles, f, indent=2)
        print(f"\nSaved results to {output_file}")

if __name__ == "__main__":
    # Configure thread pool for parallel processing
    asyncio.get_event_loop().set_default_executor(
        ThreadPoolExecutor(max_workers=10)
    )
    
    # Run main function with debug mode enabled
    asyncio.run(main(), debug=True) 