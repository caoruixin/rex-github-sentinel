import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建Gradio界面
generate_report_interface = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    title="GitHubSentinel",  # 设置界面标题
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),  # 下拉菜单选择订阅的GitHub项目
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
        # 滑动条选择报告的时间范围
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)

#############
# 初始加载订阅数据
subscriptions = subscription_manager.list_subscriptions()

# 定义函数用于添加订阅
def add_subscription(repo_url):
    if repo_url not in subscriptions:
        subscription_manager.add_subscription(repo_url)
        return "Successfully added subscription."
    else:
        return "Subscription already exists."

# 定义函数用于移除订阅
def remove_subscription(repo_url):
    if repo_url in subscriptions:
        subscription_manager.remove_subscription(repo_url)
        return "Successfully removed subscription."
    else:
        return "Subscription not found."

# 定义函数用于列出订阅
def list_subscriptions():
    return "\n".join(subscriptions)

# 创建管理订阅的界面
def create_manage_subscriptions_interface():
    with gr.Blocks() as interface:
        with gr.Row():
            add_repo_url = gr.Textbox(label="Repository URL", placeholder="Enter GitHub repository URL to add")
            add_button = gr.Button("Add Subscription")
            add_output = gr.Textbox(label="Add Output", interactive=False)
        
        with gr.Row():
            remove_repo_url = gr.Textbox(label="Repository URL", placeholder="Enter GitHub repository URL to remove")
            remove_button = gr.Button("Remove Subscription")
            remove_output = gr.Textbox(label="Remove Output", interactive=False)
        
        list_button = gr.Button("List Subscriptions")
        list_output = gr.Markdown()

        # 设置按钮点击事件
        add_button.click(fn=add_subscription, inputs=[add_repo_url], outputs=[add_output])
        remove_button.click(fn=remove_subscription, inputs=[remove_repo_url], outputs=[remove_output])
        list_button.click(fn=list_subscriptions, outputs=[list_output])

    return interface

# 创建带有两个Tab的界面
demo = gr.TabbedInterface(
    [generate_report_interface, create_manage_subscriptions_interface()],
    ["Generate Report", "Manage Subscriptions"]
)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))