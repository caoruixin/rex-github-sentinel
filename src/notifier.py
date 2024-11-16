import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify_github_report(self, repo, report):
        """
        发送 GitHub 项目报告邮件
        :param repo: 仓库名称
        :param report: 报告内容
        """
        if self.email_settings:
            subject = f"[GitHub] {repo} 进展简报"
            self.send_email(subject, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 GitHub 报告通知")
    
    def notify_hn_report(self, date, report):
        """
        发送 Hacker News 每日技术趋势报告邮件
        :param date: 报告日期
        :param report: 报告内容
        """
        if self.email_settings:
            subject = f"[HackerNews] {date} 技术趋势"
            self.send_email(subject, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 Hacker News 报告通知")

    def notify_dc_report(self, date, report):
        """
        发送 Dogecoin News 每日趋势报告邮件
        :param date: 报告日期
        :param report: 报告内容
        """
        if self.email_settings:
            subject = f"[Dogecoin News] {date} 市场趋势"
            self.send_email(subject, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送 Hacker News 报告通知")
    
    def send_email(self, subject, report):
        LOG.info(f"准备发送邮件:{subject}")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = subject
        
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

    # 测试 GitHub 报告邮件通知
    test_repo = "caoruixin/rex-github-sentinel"
    test_report = """
# caoruixin/rex-github-sentinel 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    #notifier.notify_github_report(test_repo, test_report)

    # 测试 Hacker News 报告邮件通知
    hn_report = """
# Hacker News 前沿技术趋势 (2024-09-01)

## Top 1：硬盘驱动器的讨论引发热门讨论

关于硬盘驱动器的多个讨论，尤其是关于未使用和不需要的硬盘驱动器的文章，显示出人们对科技过时技术的兴趣。

详细内容见相关链接：

- http://tom7.org/harder/
- http://tom7.org/harder/

## Top 2：学习 Linux 的重要性和 Bubbletea 程序开发

有关于 Linux 的讨论，强调了 Linux 在现代开发中的重要性和应用性，以及关于构建 Bubbletea 程序的讨论，展示了 Bubbletea 在开发中的应用性和可能性。

详细内容见相关链接：

- https://opiero.medium.com/why-you-should-learn-linux-9ceace168e5c
- https://leg100.github.io/en/posts/building-bubbletea-programs/

## Top 3：Nvidia 在 AI 领域中的强大竞争力

有关于 Nvidia 的四个未知客户，每个人购买价值超过 3 亿美元的讨论，显示出 N 维达在 AI 领域中的强大竞争力。

详细内容见相关链接：

- https://fortune.com/2024/08/29/nvidia-jensen-huang-ai-customers/

"""
    #notifier.notify_hn_report("2024-09-01", hn_report)

    dc_report = '''
    # 【Dogecoin News 热门话题】

时间：2024年11月16日

## Top 1：Memecoin回报率比加密市场平均水平高出6倍

最近的分析显示，在过去30天，Memecoin的回报率是整个加密市场平均水平的6倍，表明这一类数字货币表现出色，吸引了投资者的关注。

详细内容见相关链接：
- [cryptoslate.com](https://cryptopanic.com/news/dogecoin/20249985/Memecoin-returns-were-6x-higher-than-crypto-market-average-over-past-30-days)

### Top 2：Dogecoin投资者放弃针对Elon Musk的法律诉讼

在经历了几个月的法律争斗后，Dogecoin投资者决定撤回对Elon Musk的起诉，这一决定有望对市场情绪产生平稳影响。

详细内容见相关链接：
- [cryptonews.com](https://cryptopanic.com/news/dogecoin/20249940/Dogecoin-Investors-Drop-Legal-Battle-Against-Elon-Musk)

### Top 3：加密分析师指出Dogecoin价格突破$1的主要障碍

加密货币分析师分享了影响Dogecoin突破1美元的几个关键因素，包括市场情绪和技术分析，强调了当前的市场状况对价格走势的重要性。

详细内容见相关链接：
- [newsbtc.com](https://cryptopanic.com/news/dogecoin/20249756/Major-Hindrances-To-Dogecoin-Price-Hitting-1-According-To-This-Crypto-Analyst)

### Top 4：Dogecoin价格为何在最近的加密行情中超越比特币

分析师探讨了为什么Dogecoin在最近的市场反弹中表现超越比特币，真的为投资者提供了不少启示。

详细内容见相关链接：
- [thecoinrepublic.com](https://cryptopanic.com/news/dogecoin/20249727/Why-Dogecoin-Price-Outpaced-Bitcoin-In-Latest-Crypto-Rally)

### Top 5：狗狗币暴涨112%

Dogecoin经历了一次历史性的暴涨，价格上涨了112%。分析师们讨论了这一反弹是否将推动价格达到1美元的期望。

详细内容见相关链接：
- [newsbtc.com](https://cryptopanic.com/news/dogecoin/20249264/Dogecoin-Explodes-112-Is-1-The-New-Target-After-This-Historic-Rally)

    '''
    notifier.notify_dc_report("2024-11-16", dc_report)
