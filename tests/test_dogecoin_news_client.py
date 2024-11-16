import os
import unittest
from unittest.mock import patch, MagicMock
from dogecoin_news_client import DogeNewsClient
from io import StringIO

class TestDogeNewsClient(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法之前运行，初始化 DogeNewsClient 实例和测试数据，并设置日志捕获。
        """
        self.client = DogeNewsClient()
        
        # 捕获日志输出
        self.log_capture = StringIO()
        self.capture_id = MagicMock()
        self.capture_id = self.client.LOG.addHandler(logging.StreamHandler(self.log_capture))
        
        # 创建模拟数据
        self.mock_html_content = """
        <html>
            <body>
                <div class="news-row news-row-link">
                    <a class="news-cell nc-title" href="/news/dogecoin/1/sample-link">
                        <span>Sample Dogecoin News Title 1</span>
                    </a>
                </div>
                <div class="news-row news-row-link">
                    <a class="news-cell nc-title" href="/news/dogecoin/2/sample-link2">
                        <span>Sample Dogecoin News Title 2</span>
                    </a>
                </div>
            </body>
        </html>
        """
        # Mock the methods that interact with external systems like Selenium WebDriver

    def tearDown(self):
        """
        在每个测试方法之后运行，移除日志捕获并清理测试环境。
        """
        self.client.LOG.removeHandler(self.capture_id)
        self.log_capture.close()

        # 清理生成的测试文件
        if os.path.exists('dogecoin_top_news'):
            for root, dirs, files in os.walk('dogecoin_top_news', topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_fetch_top_news(self, mock_chromedriver, mock_chrome):
        """
        测试 fetch_top_news 方法是否能够成功抓取并解析 Dogecoin 新闻。
        """
        # 模拟 Selenium WebDriver
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = self.mock_html_content
        mock_driver.quit = MagicMock()

        # 执行 fetch_top_news 方法
        top_news = self.client.fetch_top_news()

        # 验证 fetch_top_news 方法返回的数据是否正确
        self.assertEqual(len(top_news), 2)
        self.assertEqual(top_news[0]['title'], "Sample Dogecoin News Title 1")
        self.assertEqual(top_news[0]['link'], "https://cryptopanic.com/news/dogecoin/1/sample-link")
        self.assertEqual(top_news[1]['title'], "Sample Dogecoin News Title 2")
        self.assertEqual(top_news[1]['link'], "https://cryptopanic.com/news/dogecoin/2/sample-link2")

        # 验证日志内容
        log_content = self.log_capture.getvalue()
        self.assertIn("准备获取Dogecoin的热门新闻", log_content)
        self.assertIn("成功解析 2 条Dogecoin新闻", log_content)

    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_fetch_top_news_error(self, mock_chromedriver, mock_chrome):
        """
        测试 fetch_top_news 方法在获取 Dogecoin 新闻失败时的错误处理。
        """
        # 模拟 Selenium WebDriver 抛出异常
        mock_chrome.side_effect = Exception("Failed to initialize WebDriver")
        
        # 执行 fetch_top_news 方法，捕获异常
        top_news = self.client.fetch_top_news()

        # 验证返回的新闻为空，因为获取新闻失败
        self.assertEqual(top_news, [])

        # 验证错误日志
        log_content = self.log_capture.getvalue()
        self.assertIn("获取Dogecoin的热门新闻失败", log_content)

    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_export_top_news(self, mock_chromedriver, mock_chrome):
        """
        测试 export_top_news 方法是否能正确生成文件。
        """
        # 模拟 fetch_top_news 方法返回的数据
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = self.mock_html_content
        mock_driver.quit = MagicMock()
        
        # 模拟 fetch_top_news 方法
        self.client.fetch_top_news = MagicMock(return_value=[{'title': 'Sample Dogecoin News Title 1', 'link': '/news/dogecoin/1/sample-link'},
                                                             {'title': 'Sample Dogecoin News Title 2', 'link': '/news/dogecoin/2/sample-link2'}])

        # 执行 export_top_news 方法
        report_file_path = self.client.export_top_news(date="2024-11-16", hour="10")

        # 验证文件路径是否正确
        self.assertTrue(report_file_path.endswith("dogecoin_top_news/2024-11-16/10.md"))

        # 验证文件内容是否正确
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertIn("Sample Dogecoin News Title 1", content)
            self.assertIn("Sample Dogecoin News Title 2", content)

        # 验证生成的目录和文件是否存在
        self.assertTrue(os.path.exists('dogecoin_top_news/2024-11-16'))
        self.assertTrue(os.path.exists(report_file_path))

    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    def test_export_top_news_no_news(self, mock_chromedriver, mock_chrome):
        """
        测试 export_top_news 方法在没有新闻时的行为。
        """
        # 模拟 fetch_top_news 返回空
        self.client.fetch_top_news = MagicMock(return_value=[])

        # 执行 export_top_news 方法
        report_file_path = self.client.export_top_news(date="2024-11-16", hour="10")

        # 验证返回值是否为 None，因为没有新闻
        self.assertIsNone(report_file_path)

        # 验证日志内容
        log_content = self.log_capture.getvalue()
        self.assertIn("未找到任何Dogecoin新闻", log_content)


if __name__ == '__main__':
    unittest.main()
