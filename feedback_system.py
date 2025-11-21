# feedback_system.py - 独立反馈系统模块
import json
import os
import uuid
from datetime import datetime
from metrics_dashboard import MetricsDashboard

class FeedbackSystem:
    def __init__(self, data_file="data/feedback.json"):
        self.data_file = data_file
        self.metrics_dashboard = MetricsDashboard()  # 数据监控
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """确保反馈数据文件存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = {
                "feedbacks": [],
                "summary": {
                    "total_feedbacks": 0,
                    "average_rating": 0,
                    "agent_feedback": 0,
                    "general_feedback": 0,
                    "bug_reports": 0,
                    "feature_requests": 0
                }
            }
            self.save_feedback_data(initial_data)
    
    def load_feedback_data(self):
        """加载反馈数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"feedbacks": [], "summary": {"total_feedbacks": 0, "average_rating": 0}}
    
    def save_feedback_data(self, data):
        """保存反馈数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def submit_feedback(self, feedback_data):
        """提交新反馈 - 集成数据监控"""
        data = self.load_feedback_data()
        
        # 生成反馈ID和时间戳
        feedback_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        feedback_record = {
            "id": feedback_id,
            "timestamp": timestamp,
            **feedback_data
        }
        
        # 添加到反馈列表
        data["feedbacks"].append(feedback_record)
        
        # 更新统计信息
        data["summary"]["total_feedbacks"] = len(data["feedbacks"])
        
        if "rating" in feedback_data:
            ratings = [f["rating"] for f in data["feedbacks"] if "rating" in f]
            if ratings:
                data["summary"]["average_rating"] = sum(ratings) / len(ratings)
        
        # 分类统计
        feedback_type = feedback_data.get("type", "general_feedback")
        if "agent" in feedback_type.lower():
            data["summary"]["agent_feedback"] = data["summary"].get("agent_feedback", 0) + 1
        elif feedback_type == "Bug报告":
            data["summary"]["bug_reports"] = data["summary"].get("bug_reports", 0) + 1
        elif feedback_type == "功能建议":
            data["summary"]["feature_requests"] = data["summary"].get("feature_requests", 0) + 1
        else:
            data["summary"]["general_feedback"] = data["summary"].get("general_feedback", 0) + 1
        
        self.save_feedback_data(data)
        
        # 🔥 记录反馈到数据监控
        self.metrics_dashboard.record_feedback(feedback_data)
        
        return feedback_id
    
    def get_feedback_stats(self):
        """获取反馈统计"""
        data = self.load_feedback_data()
        return data["summary"]
    
    def get_recent_feedbacks(self, limit=10):
        """获取最近反馈"""
        data = self.load_feedback_data()
        return data["feedbacks"][-limit:]
    
    def get_feedback_by_id(self, feedback_id):
        """根据ID获取反馈"""
        data = self.load_feedback_data()
        for feedback in data["feedbacks"]:
            if feedback["id"] == feedback_id:
                return feedback
        return None
    
    def get_feedbacks_by_type(self, feedback_type):
        """根据类型获取反馈"""
        data = self.load_feedback_data()
        return [fb for fb in data["feedbacks"] if fb.get("type") == feedback_type]
    
    def get_average_rating(self):
        """获取平均评分"""
        data = self.load_feedback_data()
        ratings = [f["rating"] for f in data["feedbacks"] if "rating" in f]
        if ratings:
            return sum(ratings) / len(ratings)
        return 0
    
    def get_rating_distribution(self):
        """获取评分分布"""
        data = self.load_feedback_data()
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for feedback in data["feedbacks"]:
            if "rating" in feedback:
                rating = feedback["rating"]
                if rating in distribution:
                    distribution[rating] += 1
        
        return distribution

# 测试函数
def test_feedback_system():
    """测试反馈系统"""
    feedback_system = FeedbackSystem()
    
    # 测试提交反馈
    test_feedback = {
        "type": "Agent使用体验",
        "rating": 5,
        "content": "测试反馈内容",
        "contact": "test@example.com"
    }
    
    feedback_id = feedback_system.submit_feedback(test_feedback)
    print(f"✅ 反馈提交成功! ID: {feedback_id}")
    
    # 测试获取统计
    stats = feedback_system.get_feedback_stats()
    print(f"📊 反馈统计: {stats}")
    
    # 测试获取平均评分
    avg_rating = feedback_system.get_average_rating()
    print(f"⭐ 平均评分: {avg_rating}")

if __name__ == "__main__":
    test_feedback_system()