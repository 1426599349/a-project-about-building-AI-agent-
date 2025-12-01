# agent_ui.py - 改进反馈触发（已移除API密钥输入）
import streamlit as st
from career_agent import CareerAgent
from feedback_system import FeedbackSystem

class AgentUI:
    def __init__(self):
        self.feedback_system = FeedbackSystem()
        self.init_session_state()
    
    def init_session_state(self):
        """初始化session state"""
        if 'career_agent' not in st.session_state:
            st.session_state.career_agent = None
        if 'agent_active' not in st.session_state:
            st.session_state.agent_active = False
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ""
        if 'show_feedback' not in st.session_state:
            st.session_state.show_feedback = False
        if 'conversation_ended' not in st.session_state:
            st.session_state.conversation_ended = False
        if 'last_user_input' not in st.session_state:
            st.session_state.last_user_input = ""
    
    def render_sidebar(self):
        """渲染侧边栏 - 已移除API密钥输入"""
        with st.sidebar:
            st.title("⚙️ 系统配置")
        
        # 不再显示API密钥输入框
        # API密钥现在从环境变量自动获取
        
        st.divider()
        
        # Agent控制
        st.markdown("### 🤖 Agent控制")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 启动Agent", type="primary", use_container_width=True):
                try:
                    # 直接从config获取API密钥
                    from config import DEEPSEEK_API_KEY
                    api_key = DEEPSEEK_API_KEY
                    
                    if not api_key:
                        st.error("""
                        ❌ API密钥未配置！
                        
                        请设置环境变量：
                        1. 本地：创建 `.env` 文件，内容：DEEPSEEK_API_KEY=sk-你的密钥
                        2. 云端：在 Streamlit Secrets 中添加 DEEPSEEK_API_KEY
                        """)
                        return
                    
                    st.session_state.career_agent = CareerAgent(api_key)
                    st.session_state.agent_active = True
                    st.success("✅ Agent已启动！")
                    st.rerun()
                except Exception as e:
                    st.error(f"启动Agent失败: {e}")
        
        with col2:
            if st.button("🔄 重置对话", use_container_width=True):
                if st.session_state.get('career_agent') is not None:
                    st.session_state.career_agent.conversation_history = []
                    st.session_state.career_agent.user_profile = {}
                st.session_state.conversation_ended = False
                st.success("对话已重置")
                st.rerun()
        
        # Agent状态显示
        if st.session_state.agent_active:
            if hasattr(st.session_state, 'career_agent') and st.session_state.career_agent is not None:
                try:
                    status = st.session_state.career_agent.get_status()
                    st.success("✅ Agent运行中")
                    st.write(f"**当前模式**: {status['state']}")
                    st.write(f"**收集信息**: {status['profile_items']}项")
                    st.write(f"**对话轮次**: {status['conversation_count']}")
                    
                    if status['user_profile']:
                        with st.expander("📋 用户信息摘要"):
                            for key, value in status['user_profile'].items():
                                st.write(f"**{key}**: {value}")
                except Exception as e:
                    st.error(f"获取Agent状态失败: {e}")
                    st.session_state.agent_active = False
            else:
                st.warning("❌ Agent未正确初始化")
                st.session_state.agent_active = False
        else:
            st.warning("❌ Agent未启动")
        
        # 反馈按钮
        self.render_feedback_button()
        
        # 手动触发反馈（测试用）
        if st.checkbox("显示调试选项"):
            if st.button("手动触发反馈"):
                st.session_state.conversation_ended = True
                st.rerun()
            
            # 显示调试信息
            st.write("---")
            st.write("🔧 调试信息:")
            st.write(f"Agent对象: {st.session_state.get('career_agent')}")
            st.write(f"Agent活跃: {st.session_state.agent_active}")
    
    def render_feedback_button(self):
        """渲染反馈按钮"""
        with st.sidebar:
            st.divider()
            st.markdown("### 📝 用户反馈")
            
            if st.button("💬 我要反馈", use_container_width=True, key="sidebar_feedback"):
                st.session_state.show_feedback = True
                st.rerun()
            
            # 显示反馈统计
            stats = self.feedback_system.get_feedback_stats()
            st.caption(f"已收到 {stats['total_feedbacks']} 条反馈")
            if stats['average_rating'] > 0:
                st.caption(f"平均评分: {stats['average_rating']:.1f}⭐")
    
    def render_feedback_form(self):
        """渲染反馈表单"""
        st.markdown("### 💬 用户反馈")
        st.write("我们重视您的每一个建议！")
        
        with st.form("feedback_form"):
            # 反馈类型
            feedback_type = st.selectbox(
                "反馈类型",
                ["Agent使用体验", "功能建议", "Bug报告", "其他反馈"],
                help="请选择最符合的反馈类型"
            )
            
            # 满意度评分
            rating = st.slider(
                "整体满意度", 
                min_value=1, 
                max_value=5, 
                value=5,
                help="1分-很不满意，5分-非常满意"
            )
            
            # 反馈内容
            feedback_content = st.text_area(
                "详细反馈",
                placeholder="请详细描述您的建议、遇到的问题或使用体验...",
                height=150,
                help="您的详细描述能帮助我们更好地改进产品"
            )
            
            # 联系方式（可选）
            contact = st.text_input(
                "联系方式（可选）",
                placeholder="邮箱/微信/电话，方便我们回复您",
                help="如需回复请留下联系方式"
            )
            
            # 提交按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("📤 提交反馈", type="primary")
            
            if submitted:
                if not feedback_content.strip():
                    st.error("请填写反馈内容")
                else:
                    feedback_data = {
                        "type": feedback_type,
                        "rating": rating,
                        "content": feedback_content,
                        "contact": contact if contact else "未提供"
                    }
                    
                    # 提交反馈
                    feedback_id = self.feedback_system.submit_feedback(feedback_data)
                    
                    st.session_state.show_feedback = False
                    st.success(f"✅ 感谢您的反馈！(ID: {feedback_id})")
                    st.balloons()
                    st.rerun()
    
    def render_main_content(self):
        """渲染主内容区域"""
        st.title("🎯 AI职业规划师")
        st.markdown("""
        欢迎使用智能职业规划助手！我是一个能够理解你需求的AI职业顾问，通过自然对话为你提供专业建议。

        ### 💡 我能帮你什么？
        直接告诉我你的需求，我会智能识别并提供专业建议：

        **🎯 职业发展**
        - "帮我规划职业发展路径"
        - "我想转行到AI行业该怎么做？"
        - "如何提升职场竞争力？"

        **📝 简历优化**  
        - "帮我看看这份简历怎么优化？"
        - "产品经理简历应该突出哪些重点？"
        - "如何让简历更吸引HR？"

        **🎤 面试指导**
        - "如何准备AI产品经理的面试？"
        - "面试时被问到职业规划该怎么回答？"
        - "技术面试要注意什么？"

        **🚀 技能提升**
        - "我需要学习什么技能来转行？"
        - "AI时代应该掌握哪些核心能力？"
        - "如何快速学习新技能？"

        **💰 薪资谈判**
        - "怎么谈薪资？"
        - "期望薪资该怎么设定？"
        - "如何争取更好的待遇？"
        """)

        # 对话界面
        st.markdown("---")

        if not st.session_state.agent_active:
            st.info("""
            ## 🚀 开始使用
            1. 点击左侧边栏的"启动Agent"按钮
            2. 开始与我对话！

            **💡 小贴士**：直接告诉我你的需求，我会自动识别并提供最合适的帮助！
            """)
        else:
            agent = st.session_state.career_agent
            
            # 显示对话历史
            if agent.conversation_history:
                st.subheader("💬 对话历史")
                for msg in agent.conversation_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            else:
                st.info("""
                ## 💬 开始对话吧！
                
                **试试这些指令：**
                - "帮我看看这份简历怎么优化？"
                - "如何准备AI产品经理的面试？"  
                - "我该学习什么技能来转行？"
                - "帮我制定职业发展计划"
                - "薪资谈判有什么技巧？"
                """)
            
            # 聊天输入
            if user_input := st.chat_input("请输入你的职业问题..."):
                # 保存用户输入用于反馈
                st.session_state.last_user_input = user_input
                
                with st.chat_message("user"):
                    st.write(user_input)
                
                with st.chat_message("assistant"):
                    with st.spinner("🤖 Agent思考中..."):
                        response = agent.passive_chat(user_input)
                        st.write(response)
            
            # 快速反馈 - 现在应该能正确触发了
            self.render_quick_feedback()
    
    def render_quick_feedback(self):
        """渲染快速反馈 - 修复触发逻辑"""
        # 检查是否有对话完成
        if (st.session_state.get('conversation_ended') and 
            st.session_state.career_agent and 
            st.session_state.career_agent.conversation_history):
            
            st.markdown("---")
            st.markdown("#### 🎯 本次对话体验如何？")
            st.caption("您的反馈能帮助我们提供更好的服务！")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🤔 不太满意", use_container_width=True, key="quick_bad"):
                    feedback_data = {
                        "type": "Agent使用体验",
                        "rating": 2,
                        "content": f"快速反馈：对话体验不佳\n用户问题：{st.session_state.last_user_input}",
                        "contact": "快速反馈"
                    }
                    self.feedback_system.submit_feedback(feedback_data)
                    st.session_state.conversation_ended = False
                    st.success("感谢反馈！我们会改进体验")
                    st.rerun()
            
            with col2:
                if st.button("😐 一般", use_container_width=True, key="quick_ok"):
                    feedback_data = {
                        "type": "Agent使用体验", 
                        "rating": 3,
                        "content": f"快速反馈：对话体验一般\n用户问题：{st.session_state.last_user_input}",
                        "contact": "快速反馈"
                    }
                    self.feedback_system.submit_feedback(feedback_data)
                    st.session_state.conversation_ended = False
                    st.success("感谢反馈！")
                    st.rerun()
            
            with col3:
                if st.button("😊 满意", use_container_width=True, key="quick_good"):
                    feedback_data = {
                        "type": "Agent使用体验",
                        "rating": 4,
                        "content": f"快速反馈：对话体验良好\n用户问题：{st.session_state.last_user_input}",
                        "contact": "快速反馈" 
                    }
                    self.feedback_system.submit_feedback(feedback_data)
                    st.session_state.conversation_ended = False
                    st.success("感谢您的认可！")
                    st.rerun()
            
            with col4:
                if st.button("💬 详细反馈", use_container_width=True, key="quick_detail"):
                    st.session_state.show_feedback = True
                    st.rerun()
    
    def render_usage_guide(self):
        """渲染使用指南"""
        with st.expander("📚 使用指南"):
            st.markdown("""
            ### 🎯 最佳实践
            
            **1. 明确表达需求**
            ```
            ✅ 好： "我想优化产品经理简历"
            ❌ 不好： "优化简历"
            ```
            
            **2. 提供背景信息**
            ```
            ✅ 好： "我今年25岁，有2年运营经验，想转行产品经理"
            ❌ 不好： "我想转行"
            ```
            
            **3. 具体描述问题**
            ```
            ✅ 好： "面试时被问到'为什么选择我们公司'该怎么回答？"
            ❌ 不好： "面试问题"
            ```
            
            ### 🔧 功能特点
            - 🎯 **智能识别**：自动理解你的需求类型
            - 📝 **信息提取**：从对话中学习你的背景
            - 💬 **上下文记忆**：记住之前的对话
            - 🚫 **隐私保护**：不会主动询问敏感信息
            - 🚀 **全能助手**：涵盖职业发展所有方面
            - 📊 **反馈系统**：每次对话后可以评价体验
            """)
    
    def run(self):
        """运行UI"""
        # 设置页面配置
        st.set_page_config(
            page_title="AI职业规划师",
            page_icon="🎯",
            layout="wide"
        )
        
        # 渲染各个部分
        self.render_sidebar()
        self.render_main_content()
        self.render_usage_guide()
        
        # 全局反馈表单显示
        if st.session_state.show_feedback:
            with st.container():
                st.markdown("---")
                self.render_feedback_form()
        
        # 页脚
        st.markdown("---")
        st.caption("🎯 AI职业规划师 | 智能对话 | 全能职业顾问 | 反馈系统")

def main():
    """主函数"""
    ui = AgentUI()
    ui.run()

if __name__ == "__main__":
    main()