# agent_ui.py - 简化反馈入口版
import streamlit as st
import os
import sys
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 导入Agent和配置 ==========
try:
    from career_agent import CareerAgent
    from config import get_api_key
    from feedback_system import FeedbackSystem
    
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
        st.session_state.agent = CareerAgent(API_KEY)
    except Exception as e:
        st.error(f"❌ 创建Agent失败: {e}")
        st.stop()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'feedback_content' not in st.session_state:
    st.session_state.feedback_content = ""

# 初始化反馈系统
feedback_system = FeedbackSystem()

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI职业规划师",
    page_icon="🎯",
    layout="wide"
)

# ========== CSS样式 ==========
st.markdown("""
<style>
/* 主标题样式 */
.main-header {
    text-align: center;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    margin-bottom: 2rem;
}

/* 卡片样式 */
.category-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    border-left: 5px solid;
    height: 100%;
    margin-bottom: 1rem;
}

/* 按钮样式 */
.stButton > button {
    border-radius: 8px;
    transition: all 0.2s;
}

/* 反馈按钮特殊样式 */
.feedback-btn {
    background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%) !important;
    color: white !important;
    border: none !important;
}

/* 消息样式 */
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 0 18px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
}

.ai-message {
    background: #f8f9fa;
    color: #212529;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 0;
    margin: 8px 0;
    max-width: 80%;
    border: 1px solid #e9ecef;
}
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h3 style='color: #667eea; margin: 0;'>🎯 AI职业规划师</h3>
        <p style='color: #666; margin: 0; font-size: 0.8rem;'>专业职业咨询助手</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 系统状态
    if st.session_state.agent:
        try:
            status = st.session_state.agent.get_status()
            st.info(f"**当前模式:** {status['state']}")
            st.info(f"**对话轮次:** {len(st.session_state.messages)//2}")
        except:
            pass
    
    st.divider()
    
    # 反馈入口
    st.markdown("### 💬 用户反馈")
    
    feedback_content = st.text_area(
        "请留下您的宝贵意见",
        placeholder="您的反馈对我们非常重要！\n请告诉我们您的使用体验、建议或遇到的问题...",
        height=120,
        key="feedback_text"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        rating = st.selectbox("评分", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"], index=0)
    with col2:
        feedback_type = st.selectbox("类型", ["使用体验", "功能建议", "问题报告", "其他"])
    
    if st.button("📤 提交反馈", type="primary", use_container_width=True):
        if not feedback_content.strip():
            st.error("请输入反馈内容")
        else:
            try:
                # 转换评分
                rating_map = {"⭐": 1, "⭐⭐": 2, "⭐⭐⭐": 3, "⭐⭐⭐⭐": 4, "⭐⭐⭐⭐⭐": 5}
                rating_value = rating_map.get(rating, 5)
                
                feedback_data = {
                    "type": feedback_type,
                    "rating": rating_value,
                    "content": feedback_content.strip(),
                    "contact": ""  # 如果需要联系方式，可以添加输入框
                }
                
                feedback_id = feedback_system.submit_feedback(feedback_data)
                if feedback_id:
                    st.success(f"✅ 感谢您的反馈！ID: {feedback_id}")
                    st.session_state.feedback_content = ""
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("提交失败，请重试")
            except Exception as e:
                st.error(f"提交失败: {str(e)}")
    
    st.divider()
    
    # 对话管理
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.agent:
            try:
                st.session_state.agent.clear_conversation()
            except:
                pass
        st.success("对话已清空")
        time.sleep(0.5)
        st.rerun()
    
    st.caption("💡 提示：点击下方问题快速开始对话")

# ========== 主界面 ==========
# 标题
st.markdown("""
<div class="main-header">
    <h1 style='color: white; margin: 0; font-size: 3rem;'>🎯 AI职业规划师</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;'>
        智能职业发展顾问，为您提供专业的职业规划建议
    </p>
</div>
""", unsafe_allow_html=True)

# 快速问题卡片
st.markdown("### 💡 快速提问")

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

cols = st.columns(4)
for idx, (col, category) in enumerate(zip(cols, categories)):
    with col:
        st.markdown(f"""
        <div class="category-card" style='border-color: {category["color"]}'>
            <h4 style='color: {category["color"]}; margin-top: 0;'>{category["title"]}</h4>
        """, unsafe_allow_html=True)
        
        for question in category['questions']:
            if st.button(
                f"💬 {question}",
                key=f"quick_{idx}_{hash(question)}",
                use_container_width=True
            ):
                try:
                    response = st.session_state.agent.passive_chat(question)
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"提问失败: {str(e)[:100]}")
        
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# 对话历史
st.markdown("### 💬 对话历史")

if not st.session_state.messages:
    st.info("👋 请在上方选择问题开始对话，或直接在下方输入您的问题")
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                <div class="user-message">
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"""
                <div class="ai-message">
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

# 用户输入
st.markdown("---")
user_input = st.chat_input("💭 请输入您的问题...")

if user_input and st.session_state.agent:
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div class="user-message">
            {user_input}
        </div>
        """, unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 AI正在思考..."):
            try:
                response = st.session_state.agent.passive_chat(user_input)
                
                st.markdown(f"""
                <div class="ai-message">
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"❌ 处理请求时出错: {str(e)[:100]}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    time.sleep(0.3)
    st.rerun()

# 页面底部
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("🎯 AI职业规划师 · 专业职业咨询助手")
    st.caption("💡 提示：所有AI建议仅供参考，请结合自身情况决策")
with col2:
    if st.button("💬 反馈建议", type="secondary"):
        st.info("感谢您的关注！请在左侧边栏提交反馈")