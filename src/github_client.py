# src/github_client.py

import requests  # 导入requests库用于HTTP请求
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块
import pytz

class GitHubClient:
    def __init__(self, token):
        self.token = token  # GitHub API令牌
        self.headers = {'Authorization': f'token {self.token}'}  # 设置HTTP头部认证信息

    # 对于 github 久经验证的API  即便是指定的params 不支持 API也不会报错 只是不生效
    def fetch_updates(self, repo, since=None, until=None):
        # 获取指定仓库的更新，可以指定开始和结束日期

        updates = {
            'commits': self.fetch_commits(repo, since, until),  # 获取提交记录
            'issues': self.fetch_issues(repo, since, until),  # 获取问题
            'pull_requests': self.fetch_pull_requests(repo, since, until)  # 获取拉取请求
        }
        return updates

    def fetch_commits(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/commits'  # 构建获取提交的API URL
        params = {}
        if since:
            params['since'] = since  # 如果指定了开始日期，添加到参数中
        if until:
            params['until'] = until  # 如果指定了结束日期，添加到参数中

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()  # 检查请求是否成功
        commits = response.json()

        return self.filter_by_date(commits, 'commit.author.date', since, until)

        #return response.json()  # 返回JSON格式的数据

    def fetch_issues(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/issues'  # 构建获取问题的API URL
        params = {
            'state': 'closed',  # 仅获取已关闭的问题
            'since': since,
            'until': until
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        #return response.json()
        issues = response.json()
        return self.filter_by_date(issues, 'closed_at', since, until)

    def fetch_pull_requests(self, repo, since=None, until=None):
        url = f'https://api.github.com/repos/{repo}/pulls'  # 构建获取拉取请求的API URL
        params = {
            'state': 'closed',  # 仅获取已合并的拉取请求
            'since': since,
            'until': until
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        #return response.json()
        pull_requests = response.json()
        return self.filter_by_date(pull_requests, 'closed_at', since, until)
    
    def filter_by_date(self, items, date_key, since, until):
        if since:
            since = datetime.fromisoformat(since).replace(tzinfo=pytz.UTC)
        if until:
            until = datetime.fromisoformat(until).replace(tzinfo=pytz.UTC)
        '''
        if since:
            since = datetime.fromisoformat(since)
        if until:
            until = datetime.fromisoformat(until)
        '''

        filtered_items = []
        for item in items:
            date_str = self.get_nested_value(item, date_key)
            if date_str:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                LOG.info(f"Since : {since} ==========  Item date: {date} ========= Until: {until}")
                if (since and date < since) or (until and date > until):
                    continue
                filtered_items.append(item)
        return filtered_items
    

    def get_nested_value(self, data, key):
        keys = key.split('.')
        for k in keys:
            data = data.get(k, None)
            if data is None:
                return None
        return data


    def export_daily_progress(self, repo):

        local_tz = pytz.timezone('UTC')  # 假设你在 UTC 时区
        today = datetime.now(local_tz).date().isoformat()  # 获取今天的日期，并带有时区信息
        
        LOG.info(f"Fetching updates for {repo} since {today}")
        

        updates = self.fetch_updates(repo, since=today)  # 获取今天的更新数据
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建存储路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(repo_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for {repo} ({today})\n\n")
            file.write("\n## Issues Closed Today\n")
            for issue in updates['issues']:  # 写入今天关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write("\n## Pull Requests Merged Today\n")
            for pr in updates['pull_requests']:  # 写入今天合并的拉取请求
                file.write(f"- {pr['title']} #{pr['number']}\n")
        
        LOG.info(f"Exported daily progress to {file_path}")  # 记录日志
        return file_path

    def export_progress_by_date_range(self, repo, days):
    
        #today = date.today()  # 获取当前日期

        # 获取当前日期，并转换为带有 UTC 时区信息的 datetime 对象
        today = datetime.now(pytz.UTC).date()

        since = today - timedelta(days=days)  # 计算开始日期
        
        updates = self.fetch_updates(repo, since=since.isoformat(), until=today.isoformat())  # 获取指定日期范围内的更新
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        # 更新文件名以包含日期范围
        date_str = f"{since}_to_{today}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for issue in updates['issues']:  # 写入在指定日期内关闭的问题
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write(f"\n## Pull Requests Merged in the Last {days} Days\n")
            for pr in updates['pull_requests']:  # 写入在指定日期内合并的拉取请求
                file.write(f"- {pr['title']} #{pr['number']}\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")  # 记录日志
        return file_path
    
    def export_progress_by_since_until(self, repo, since, until):

        # 将字符串转换为具有时区信息的 datetime 对象
        since_date = datetime.fromisoformat(since).replace(tzinfo=pytz.UTC)
        until_date = datetime.fromisoformat(until).replace(tzinfo=pytz.UTC)
    
        # # 将字符串转换为 datetime 对象
        #since_date = datetime.fromisoformat(since)
        #until_date = datetime.fromisoformat(until)
    
        updates = self.fetch_updates(repo, since=since_date.isoformat(), until=until_date.isoformat())
        
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)
        
        date_str = f"{since}_to_{until}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {until})\n\n")
            file.write("\n## Issues Closed in the Specified Time Range\n")
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
            file.write("\n## Pull Requests Merged in the Specified Time Range\n")
            for pr in updates['pull_requests']:
                file.write(f"- {pr['title']} #{pr['number']}\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")
        return file_path