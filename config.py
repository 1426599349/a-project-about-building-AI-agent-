# config.py - 兼容版本
import os

def get_api_key():
    """安全获取API密钥 - 兼容streamlit run和python直接运行"""
    
    # 方法1: 尝试从Streamlit Secrets获取（streamlit run时可用）
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DEEPSEEK_API_KEY' in st.secrets:
            return st.secrets['DEEPSEEK_API_KEY']
    except:
        pass  # 如果streamlit不可用，继续其他方法
    
    # 方法2: 从环境变量获取
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        return api_key
    
    # 方法3: 从本地.env文件获取（开发环境）
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('DEEPSEEK_API_KEY')
    except:
        return None
    
    # 方法4: 如果以上都失败，返回None
    return None

# 配置常量
DEEPSEEK_API_KEY = get_api_key()
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# 验证配置
if __name__ == "__main__":
    if DEEPSEEK_API_KEY:
        print("✅ API Key loaded successfully")
    else:
        print("⚠️  Warning: DEEPSEEK_API_KEY not found")
        print("请设置环境变量 DEEPSEEK_API_KEY 或创建 .env 文件")