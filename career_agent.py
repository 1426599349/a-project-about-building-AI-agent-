# career_agent.py - Agent核心类（集成数据监控）
import requests
import json
import streamlit as st
import time
from feedback_system import FeedbackSystem
from metrics_dashboard import MetricsDashboard
from career_knowledge import enhance_prompt

class CareerAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.conversation_history = []
        self.user_profile = {}
        self.current_state = "general"
        self.feedback_system = FeedbackSystem()
        self.metrics_dashboard = MetricsDashboard()  # 数据监控
        
    
    def get_status(self):
        """获取Agent状态"""
        return {
            "state": self.current_state,
            "profile_items": len(self.user_profile),
            "conversation_count": len(self.conversation_history) // 2,
            "user_profile": self.user_profile
        }
    
    def get_conversation_summary(self):
        """获取对话摘要"""
        # ... 现有代码 ...
    
    def detect_state(self, user_input):
        """智能状态检测"""
        user_input_lower = user_input.lower()
        
        # 简历相关
        if any(word in user_input_lower for word in ["简历", "cv", "resume", "求职信"]):
            self.current_state = "resume"
        # 面试相关
        elif any(word in user_input_lower for word in ["面试", "interview", "面经", "面试题"]):
            self.current_state = "interview"
        # 职业分析相关
        elif any(word in user_input_lower for word in ["职业", "规划", "发展", "方向", "转行"]):
            self.current_state = "career"
        # 技能学习相关
        elif any(word in user_input_lower for word in ["技能", "学习", "提升", "课程", "培训"]):
            self.current_state = "skills"
        # 薪资谈判相关
        elif any(word in user_input_lower for word in ["薪资", "工资", "薪水", "谈薪"]):
            self.current_state = "salary"
        else:
            self.current_state = "general"
        
        return self.current_state
    
    def update_profile_from_input(self, user_input):
        """从对话中智能提取用户信息"""
        if any(word in user_input for word in ["我今年", "年龄", "岁"]):
            self.user_profile["age"] = user_input
        elif any(word in user_input for word in ["我学", "学历", "专业", "毕业"]):
            self.user_profile["education"] = user_input
        elif any(word in user_input for word in ["我工作", "经验", "从业", "在职"]):
            self.user_profile["experience"] = user_input
        elif any(word in user_input for word in ["我会", "技能", "擅长", "熟悉"]):
            self.user_profile["skills"] = user_input
        elif any(word in user_input for word in ["我想", "目标", "希望", "打算"]):
            self.user_profile["goals"] = user_input
    
    def call_deepseek(self, messages):
        """调用DeepSeek API - 集成性能监控"""
        start_time = time.time()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                # 记录成功的API调用
                self.metrics_dashboard.record_api_call(
                    success=True,
                    response_time=response_time,
                    user_input=messages[-1]["content"] if messages else None
                )
                return result["choices"][0]["message"]["content"]
            else:
                # 记录失败的API调用
                self.metrics_dashboard.record_api_call(
                    success=False,
                    response_time=response_time,
                    user_input=messages[-1]["content"] if messages else None,
                    error_msg=f"HTTP {response.status_code}"
                )
                return f"❌ API请求失败，请检查网络连接和API密钥"
        except Exception as e:
            # 记录异常的API调用
            self.metrics_dashboard.record_api_call(
                success=False,
                response_time=time.time() - start_time,
                user_input=messages[-1]["content"] if messages else None,
                error_msg=str(e)
            )
            return f"❌ 网络连接异常，请稍后重试"
    
    def passive_chat(self, user_input):
        """智能对话处理 - 集成会话记录"""
        # 1. 状态检测
        current_state = self.detect_state(user_input)
        
        # 2. 信息提取
        self.update_profile_from_input(user_input)
        
        # 3. 构建智能系统提示
        system_prompt = f"""你是一个全能的AI职业规划师，能够处理所有职业发展相关的问题。

🎯 当前对话模式：{current_state}
📊 用户主动提供的信息：{json.dumps(self.user_profile, ensure_ascii=False)}

🚀 全能服务范围：
- 职业发展规划与咨询
- 简历优化与撰写指导
- 面试准备与技巧辅导  
- 技能提升与学习路径
- 薪资谈判与职业晋升
- 职场问题解决
- 行业趋势分析

💡 对话原则：
1. 直接专业地回答用户问题
2. 基于用户提供的信息给出个性化建议
3. 信息不足时提供通用专业建议
4. 绝不主动询问个人信息
5. 保持友好、专业、实用的风格
6. 提供具体可执行的建议

请根据当前对话模式提供最专业的建议。"""

        # 4. 构建对话消息
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加最近的对话历史（保持上下文）
        for msg in self.conversation_history[-4:]:
            messages.append(msg)
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        # 5. 调用API
        response = self.call_deepseek(messages)
        
        # 6. 更新对话历史
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # 限制历史长度
        if len(self.conversation_history) > 8:
            self.conversation_history = self.conversation_history[-8:]
        
        # 🔥 记录用户会话
        self.metrics_dashboard.record_session(user_input, response)
        
        # 修复：正确设置会话结束状态
        st.session_state.conversation_ended = True
        
        return response
    
    def get_status(self):
        """获取Agent状态"""
        return {
            "state": self.current_state,
            "profile_items": len(self.user_profile),
            "conversation_count": len(self.conversation_history),
            "user_profile": self.user_profile
        }
    
    def submit_feedback(self, feedback_data):
        """提交反馈"""
        return self.feedback_system.submit_feedback(feedback_data)
    
    def get_feedback_stats(self):
        """获取反馈统计"""
        return self.feedback_system.get_feedback_stats()
    
    def get_performance_metrics(self):
        """获取性能指标"""
        return self.metrics_dashboard.get_performance_metrics()
    
    def clear_conversation(self):
        """清空对话历史"""
        self.conversation_history = []
        self.user_profile = {}
        self.current_state = "general"
    
    def get_conversation_summary(self):
        """获取对话摘要"""
        if not self.conversation_history:
            return "暂无对话历史"
        
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "assistant"]
        
        return {
            "total_turns": len(self.conversation_history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "last_user_input": user_messages[-1] if user_messages else None,
            "current_state": self.current_state
        }

# 测试函数
def test_agent():
    """测试Agent功能"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
        return
    
    agent = CareerAgent(api_key)
    
    # 测试对话
    test_inputs = [
        "你好，我想优化我的简历",
        "如何准备产品经理面试？",
        "我应该学习什么技能？"
    ]
    
    for i, user_input in enumerate(test_inputs):
        print(f"\n🧪 测试 {i+1}: {user_input}")
        response = agent.passive_chat(user_input)
        print(f"🤖 Agent回复: {response[:100]}...")
        
        # 显示状态
        status = agent.get_status()
        print(f"📊 状态: {status['state']}, 对话轮次: {status['conversation_count']}")
    
    # 显示性能指标
    metrics = agent.get_performance_metrics()
    print(f"\n📈 性能指标: {metrics}")

if __name__ == "__main__":
    test_agent()


class CareerAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.conversation_history = []
        self.user_profile = {}
        self.current_state = "general"
    
    def passive_chat(self, user_input):
        """使用知识库增强的对话"""
        # 使用知识库增强问题
        enhanced_input = enhance_prompt(user_input)
        
        # 原有的对话逻辑
        current_state = self.detect_state(user_input)
        self.update_profile_from_input(user_input)
        
        # 构建消息（使用增强后的问题）
        messages = [
            {"role": "system", "content": "你是专业的职业规划师，提供具体可行的建议。"},
            {"role": "user", "content": enhanced_input}
        ]
        
        # 调用API
        response = self.call_deepseek(messages)
        
        # 更新对话历史
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
