import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up logging
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)

class DogeNewsClient:
    def __init__(self):
        self.url = 'https://cryptopanic.com/news/dogecoin/'  # Dogecoin news URL

    def fetch_top_news(self):
        LOG.debug("准备获取Dogecoin的热门新闻。")
        try:
            # Set up Chrome WebDriver with headless mode
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(self.url)
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.news-row-link'))
            )
            LOG.debug("页面加载完毕，开始解析新闻。")
            
            page_content = driver.page_source
            driver.quit()

            return self.parse_news(page_content)

        except Exception as e:
            LOG.error(f"获取Dogecoin的热门新闻失败：{str(e)}")
            return []

    def parse_news(self, html_content):
        LOG.debug("解析Dogecoin新闻页面。")
        soup = BeautifulSoup(html_content, 'html.parser')
        news_rows = soup.find_all('div', class_='news-row news-row-link')

        top_news = []
        for row in news_rows:
            title_tag = row.find('a', class_='news-cell nc-title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                full_url = f"https://cryptopanic.com{link}"  # Complete the URL
                top_news.append({'title': title, 'link': full_url})

        LOG.info(f"成功解析 {len(top_news)} 条Dogecoin新闻。")
        return top_news

    def export_top_news(self, date=None, hour=None):
        LOG.debug("准备导出Dogecoin的热门新闻。")
        top_news = self.fetch_top_news()

        if not top_news:
            LOG.warning("未找到任何Dogecoin新闻。")
            return None

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # Create the directory path
        dir_path = os.path.join('dogecoin_top_news', date)
        os.makedirs(dir_path, exist_ok=True)

        # Define the file path
        file_path = os.path.join(dir_path, f'{hour}.md')
        
        with open(file_path, 'w') as file:
            file.write(f"# Dogecoin Top News ({date} {hour}:00)\n\n")
            for idx, news in enumerate(top_news, start=1):
                file.write(f"{idx}. [{news['title']}]({news['link']})\n")

        LOG.info(f"Dogecoin热门新闻文件已生成：{file_path}")
        return file_path

def main():
    client = DogeNewsClient()
    client.export_top_news()  # 默认情况下使用当前日期和时间

if __name__ == "__main__":
    main()
