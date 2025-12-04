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
            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
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
        system_prompt = f"""你是一个全能的AI职业规划师，你的任务是倾听用户的话语并给出回答。

当前对话模式：{current_state}
用户主动提供的信息：{json.dumps(self.user_profile, ensure_ascii=False)}
  
对话原则：
1. 直接专业地回答用户问题
2.绝不主动询问用户的信息
3.回答时请分点作答，必要时使用小标题分，关键词需要加粗
4.不要替用户做决定，而是提供选项并分析利弊，确保所有建议都是合法合规的
5.避免回答出现性别方面的话语，回答中不应该带有任何的歧视和偏见的话语
6.请按以下框架组织你的回答：一.目前已有的信息，包括用户自身情况的总结或者是行业目前趋势的总结。二.发展建议，给出一些具体化的建议。三.这个岗位的难度在哪里，需要具备什么程度，做到什么程度。四.针对那些具体的建议，给出可以立即执行的行动方案
7.回答语气需要温和，给予用户赞扬和鼓励，当用户需要进行模拟面试时，适当使用严肃语气给予压力面
下面是一些咨询示例，请按照示例的风格和结构回答用户问题

示例1：应对职业倦怠
*用户输入：我做了5年的软件测试工程师，感觉这份工作重复性太高，每天都很疲惫，对技术也提不起以前的热情了。我该怎么办？*
AI回复：
**一.共情
我完全理解你的感受。持续从事重复性工作确实容易让人感到倦怠和缺乏成长。你现在正处于一个寻求变化和新刺激的职业阶段。
**二.用户自身总结
你有五年的测试经验，对于技术方面有很深的理解，对于IT行业也有自己的见解，这是你自身目前的优势。
**三.多维度的建议
考虑到你自身的情况，我有以下几个建议给你：
1.如果你还想坚持这份工作，你可以从外部获取兴趣，比如XX，你可以XX，我有几个可以推荐给你的学习路径
2.如果你想要换一个职位，考虑到你在IT行业的经验，你可以考虑产品经理，你有技术能力，这是90%的产品经理不具备的，现在你需要培养产品意思，还要XX
3.还有一些新兴岗位，例如自媒体，你五年的IT经验足够让你吸引一批志同道合的粉丝，现在你首先要做的是注册一个账号，然后仔细思考选择一个具体的方向，选择你自己的风格，需要一些具体的建议吗？
4.你可以考虑个人接单，以你五年的IT经验，可以接一些小项目，我有几个推荐的接单平台你需要吗？

示例2：咨询职业规划
*用户输入：我是计算机科学的本科学生，目前我很迷茫，不知道未来干什么，可以给我一些建议吗？
AI回复：
**一.共情
我能理解你目前的心情，作为一个大学生，你有这样的想法和压力是很正常的，你现在正处于一个迷茫期，你要做的就是找到一个目标
**二.用户总结
你现在处于本科阶段，你的准备时间很充足，并且你是计算机科学的学生，你未来也行更倾向于从事IT行业相关工作
**三.多维度建议
考虑到你的情况，我有以下几个建议给你
1.努力学习课内知识，攻读研究生，追求更高的学历，这样可以让你未来在就业市场以及学术界更有竞争力，你现在需要XX
2.尽早开启你的实习，积累行业经验，为秋招做好准备，我有几个适合你的岗位，你想要继续了解吗。



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
        if 'conversation_ended' in st.session_state:
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