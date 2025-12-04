import json
import os
import uuid
from datetime import datetime

class FeedbackSystem:
    def __init__(self, data_file="data/feedback.json"):
        self.data_file = data_file
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
        except Exception as e:
            print(f"加载反馈数据失败: {e}")
            # 如果文件损坏，重建
            self.ensure_data_file()
            return self.load_feedback_data()
    
    def save_feedback_data(self, data):
        """保存反馈数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存反馈数据失败: {e}")
    
    def submit_feedback(self, feedback_data):
        """提交新反馈"""
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
        self.update_summary(data)
        
        self.save_feedback_data(data)
        
        return feedback_id
    
    def update_summary(self, data):
        """更新统计摘要"""
        total_feedbacks = len(data["feedbacks"])
        data["summary"]["total_feedbacks"] = total_feedbacks
        
        # 计算平均评分
        ratings = []
        category_counts = {
            "agent_feedback": 0,
            "general_feedback": 0,
            "bug_reports": 0,
            "feature_requests": 0
        }
        
        for fb in data["feedbacks"]:
            if "rating" in fb:
                ratings.append(fb["rating"])
            
            # 分类统计
            fb_type = fb.get("type", "").lower()
            if "agent" in fb_type:
                category_counts["agent_feedback"] += 1
            elif fb_type == "bug报告" or "bug" in fb_type:
                category_counts["bug_reports"] += 1
            elif fb_type == "功能建议" or "feature" in fb_type:
                category_counts["feature_requests"] += 1
            else:
                category_counts["general_feedback"] += 1
        
        # 更新平均评分
        if ratings:
            data["summary"]["average_rating"] = sum(ratings) / len(ratings)
        
        # 更新分类统计
        for key, value in category_counts.items():
            data["summary"][key] = value
    
    def get_feedback_stats(self):
        """获取反馈统计"""
        data = self.load_feedback_data()
        return data["summary"]
    
    def get_recent_feedbacks(self, limit=10):
        """获取最近反馈"""
        data = self.load_feedback_data()
        # 按时间戳排序（最新的在前）
        feedbacks = sorted(data["feedbacks"], 
                          key=lambda x: x.get("timestamp", ""), 
                          reverse=True)
        return feedbacks[:limit]
    
    def get_all_feedbacks(self):
        """获取所有反馈"""
        data = self.load_feedback_data()
        return sorted(data["feedbacks"], 
                     key=lambda x: x.get("timestamp", ""), 
                     reverse=True)
    
    def get_feedback_by_id(self, feedback_id):
        """根据ID获取反馈"""
        data = self.load_feedback_data()
        for feedback in data["feedbacks"]:
            if feedback.get("id") == feedback_id:
                return feedback
        return None
    
    def get_feedbacks_by_type(self, feedback_type):
        """根据类型获取反馈"""
        data = self.load_feedback_data()
        results = []
        for fb in data["feedbacks"]:
            if fb.get("type", "").lower() == feedback_type.lower():
                results.append(fb)
        return results
    
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
                rating = int(feedback["rating"])
                if rating in distribution:
                    distribution[rating] += 1
        
        return distribution
    
    def clear_all_feedbacks(self):
        """清空所有反馈（谨慎使用）"""
        self.ensure_data_file()
        print("所有反馈已清空")

# 测试函数
if __name__ == "__main__":
    fs = FeedbackSystem()
    
    # 测试数据
    test_feedbacks = [
        {"type": "Agent使用体验", "rating": 5, "content": "非常好用，建议很专业", "contact": "user1@example.com"},
        {"type": "Bug报告", "rating": 2, "content": "偶尔会超时", "contact": "user2@example.com"},
        {"type": "功能建议", "rating": 4, "content": "希望能添加简历模板", "contact": "user3@example.com"},
        {"type": "一般反馈", "rating": 5, "content": "界面很美观", "contact": ""}
    ]
    
    for fb in test_feedbacks:
        fs.submit_feedback(fb)
    
    # 显示统计
    stats = fs.get_feedback_stats()
    print("📊 反馈统计:", stats)
    
    # 显示最近反馈
    recent = fs.get_recent_feedbacks(3)
    print("\n📋 最近反馈:")
    for fb in recent:
        print(f"  - {fb['type']}: {fb['content'][:30]}...")