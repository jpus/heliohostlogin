from playwright.sync_api import sync_playwright
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

from playwright.sync_api import sync_playwright

def login_heliohost(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.heliohost.org/login", wait_until="networkidle")
        
        # 等待并填充登录元素
        page.wait_for_selector('input#username', state="visible", timeout=60000)
        page.fill('input#username', email)
        page.fill('input[name="password"]', password)  # 修改为更具体的选择器
        page.click('button[type="submit"]')

        # 等待可能出现的错误消息或成功登录后的页面
        try:
            # 等待可能的错误消息
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
            if error_message:
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息,检查是否已经跳转到仪表板页面
            try:
                page.wait_for_url("https://heliohost.org/dashboard", timeout=5000)
                return f"账号 {email} 登录成功!"
            except:
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_heliohost(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "HelioHost登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
    else:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        print(error_message)
