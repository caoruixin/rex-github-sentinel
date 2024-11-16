from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up WebDriver with headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Define the URL to fetch
    url = "https://cryptopanic.com/news/dogecoin/"
    driver.get(url)
    
    # Wait for the news container to load (wait for the news rows to appear)
    try:
        # Wait until at least one news row is visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.news-row-link'))
        )
        print("Page loaded, now scraping content...")

    except Exception as e:
        print(f"Timed out waiting for page content to load: {e}")
        driver.quit()
        exit()

    # After waiting for content to load, get the page source
    page_content = driver.page_source

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find all news items in the page
    news_rows = soup.find_all('div', class_='news-row news-row-link')

    # Loop through each news item and extract the title and URL
    news_list = []
    for index, row in enumerate(news_rows, start=1):
        # Extract the title
        title_tag = row.find('a', class_='news-cell nc-title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            full_url = f"https://cryptopanic.com{link}"  # Complete the URL

            # Append the news item to the list
            news_list.append(f"{index}, [{title}]({full_url})")

    # Print out the results
    for news in news_list:
        print(news)

except Exception as e:
    print(f"Error while scraping: {e}")

finally:
    # Close the browser after scraping
    driver.quit()
