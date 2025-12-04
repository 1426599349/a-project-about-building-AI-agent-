# agent_ui.py - 最终简洁版（纯前端）
import streamlit as st
import os
import sys
import time

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 导入Agent和配置 ==========
try:
    from career_agent import CareerAgent
    from config import get_api_key
    API_KEY = get_api_key()
    
    if not API_KEY:
        st.error("❌ 未找到API密钥，请检查.env文件配置")
        st.stop()
        
except ImportError as e:
    st.error(f"❌ 导入模块失败: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    st.stop()

# ========== 初始化Session State ==========
if 'agent' not in st.session_state:
    try:
        # 初始化Agent（超时设置在agent文件中）
        st.session_state.agent = CareerAgent(API_KEY)
        st.session_state.agent_active = True
    except Exception as e:
        st.error(f"❌ 创建Agent失败: {e}")
        st.stop()

if 'messages' not in st.session_state:
    st.session_state.messages = []

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI职业规划师",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 侧边栏（最小化）==========
with st.sidebar:
    # 设置按钮
    if st.button("⚙️", help="设置", key="settings_btn"):
        st.session_state.show_settings = not st.session_state.get('show_settings', False)
    
    if st.session_state.get('show_settings', False):
        st.divider()
        
        # 系统状态
        if 'agent' in st.session_state:
            try:
                status = st.session_state.agent.get_status()
                st.info(f"**当前模式**: {status['state']}")
                st.info(f"**对话轮次**: {len(st.session_state.messages)//2}")
            except:
                pass
        
        # 清空对话
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            if 'agent' in st.session_state:
                try:
                    st.session_state.agent.clear_conversation()
                except:
                    pass
            st.success("对话已清空")
            time.sleep(0.5)
            st.rerun()
        
        st.divider()
        st.caption("💡 提示：点击问题卡片快速开始")

# ========== 主界面 ==========
# 1. 标题区域
st.markdown("""
<div style='text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;'>
    <h1 style='color: white; margin: 0; font-size: 3rem;'>🎯 AI职业规划师</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;'>
        智能职业发展顾问，为您提供专业的职业规划建议
    </p>
</div>
""", unsafe_allow_html=True)

# 2. 快速问题卡片
st.markdown("### 💡 快速提问")

# 问题分类
categories = [
    {
        "title": "📄 简历优化",
        "color": "#667eea",
        "questions": [
            "如何写一份优秀的技术简历？",
            "简历中项目经验怎么写？", 
            "没有工作经验如何写简历？"
        ]
    },
    {
        "title": "💼 面试准备",
        "color": "#764ba2", 
        "questions": [
            "技术面试常见问题有哪些？",
            "如何准备产品经理面试？",
            "行为面试问题怎么回答？"
        ]
    },
    {
        "title": "🎯 职业规划",
        "color": "#f093fb",
        "questions": [
            "如何规划我的职业发展路径？",
            "想转行AI行业怎么办？",
            "遇到职业瓶颈怎么突破？"
        ]
    },
    {
        "title": "💰 薪资谈判",
        "color": "#4facfe",
        "questions": [
            "跳槽时如何谈薪资？",
            "期望薪资定多少合适？",
            "薪资谈判有什么技巧？"
        ]
    }
]

# 创建4列
cols = st.columns(4)

for idx, (col, category) in enumerate(zip(cols, categories)):
    with col:
        with st.container():
            st.markdown(f"""
            <div style='
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border-left: 5px solid {category['color']};
                height: 100%;
                transition: transform 0.2s;
            '>
                <h3 style='color: {category['color']}; margin-top: 0;'>{category['title']}</h3>
            """, unsafe_allow_html=True)
            
            for question in category['questions']:
                if st.button(
                    f"💬 {question}",
                    key=f"quick_{idx}_{hash(question)}",
                    use_container_width=True,
                    help=f"点击提问"
                ):
                    # 直接调用Agent处理
                    try:
                        response = st.session_state.agent.passive_chat(question)
                        st.session_state.messages.append({"role": "user", "content": question})
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
                    except Exception as e:
                        st.error(f"提问失败: {str(e)[:100]}")
            
            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 3. 对话历史
st.markdown("### 💬 对话历史")

if not st.session_state.messages:
    st.info("👋 请在上方选择问题开始对话，或直接在下方输入您的问题")
else:
    # 显示对话历史
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px 18px 0 18px;
                    margin: 8px 0;
                    max-width: 80%;
                    margin-left: auto;
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"""
                <div style='
                    background: #f8f9fa;
                    color: #212529;
                    padding: 12px 16px;
                    border-radius: 18px 18px 18px 0;
                    margin: 8px 0;
                    max-width: 80%;
                    border: 1px solid #e9ecef;
                '>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

# 4. 用户输入
st.markdown("---")
user_input = st.chat_input("💭 请输入您的问题...")

if user_input and 'agent' in st.session_state:
    # 显示用户消息
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 16px;
            border-radius: 18px 18px 0 18px;
            margin: 8px 0;
            max-width: 80%;
            margin-left: auto;
        '>
            {user_input}
        </div>
        """, unsafe_allow_html=True)
    
    # 使用Agent处理
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 AI正在思考..."):
            try:
                response = st.session_state.agent.passive_chat(user_input)
                
                # 显示响应
                st.markdown(f"""
                <div style='
                    background: #f8f9fa;
                    color: #212529;
                    padding: 12px 16px;
                    border-radius: 18px 18px 18px 0;
                    margin: 8px 0;
                    max-width: 80%;
                    border: 1px solid #e9ecef;
                '>
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                # 保存对话
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"❌ 处理请求时出错: {str(e)[:100]}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # 自动刷新
    time.sleep(0.3)
    st.rerun()

# 5. 页脚
st.markdown("""
<div style='
    text-align: center;
    padding: 2rem 1rem;
    color: #6c757d;
    font-size: 0.9rem;
    margin-top: 3rem;
'>
    <p style='margin: 0.5rem 0; opacity: 0.8;'>
        🎯 AI职业规划师 · 专业职业咨询助手
    </p>
    <p style='margin: 0.5rem 0; font-size: 0.8rem; opacity: 0.6;'>
        💡 提示：所有AI建议仅供参考，请结合自身情况决策
    </p>
</div>
""", unsafe_allow_html=True)

# 6. 对话反馈（如果有对话）
if len(st.session_state.messages) >= 2:
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("👍 有帮助", use_container_width=True):
            try:
                feedback_data = {
                    "type": "对话反馈",
                    "rating": 5,
                    "content": "用户表示对话有帮助"
                }
                st.session_state.agent.submit_feedback(feedback_data)
                st.success("感谢反馈！")
                time.sleep(1)
                st.rerun()
            except:
                st.success("感谢认可！")
    with col2:
        if st.button("💡 提建议", use_container_width=True):
            st.info("感谢您的关注，我们会持续改进！")
            time.sleep(1)