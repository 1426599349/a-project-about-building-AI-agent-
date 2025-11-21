# main.py - 控制台启动器
import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

def test_api_connection():
    """测试API连接"""
    print("正在测试API连接...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello, please reply with one sentence"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API连接成功！")
            print("模型回复:", result["choices"][0]["message"]["content"])
        else:
            print("API请求失败")
            print("错误详情:", response.text)
    except Exception as e:
        print(f"发生异常: {e}")

def show_main_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("        AI职业规划师 - Agent版系统")
    print("="*50)
    print("1. 测试API连接")
    print("2. 启动Web版Agent")
    print("3. 退出系统")
    print("="*50)

def main():
    """主程序"""
    print("AI职业规划师 Agent版系统初始化完成！")
    
    while True:
        show_main_menu()
        choice = input("\n请选择功能 (1-3): ").strip()
        
        if choice == "1":
            test_api_connection()
        elif choice == "2":
            print("启动Web版Agent...")
            print("请运行: streamlit run agent_ui.py")
        elif choice == "3":
            print("感谢使用AI职业规划师系统！")
            break
        else:
            print("错误：请输入有效选项 (1-3)")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()