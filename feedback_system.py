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
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            if not os.path.exists(self.data_file):
                print(f"📁 创建反馈数据文件: {self.data_file}")
                initial_data = {
                    "feedbacks": [],
                    "summary": {
                        "total_feedbacks": 0,
                        "average_rating": 0,
                        "usage_feedback": 0,
                        "suggestion": 0,
                        "bug_report": 0,
                        "other": 0
                    }
                }
                self._save_data(initial_data)
                return True
            return True
        except Exception as e:
            print(f"❌ 确保数据文件失败: {e}")
            return False
    
    def _load_data(self):
        """加载数据"""
        try:
            if not os.path.exists(self.data_file):
                self.ensure_data_file()
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保数据结构完整
                if "feedbacks" not in data:
                    data["feedbacks"] = []
                if "summary" not in data:
                    data["summary"] = {
                        "total_feedbacks": 0,
                        "average_rating": 0,
                        "usage_feedback": 0,
                        "suggestion": 0,
                        "bug_report": 0,
                        "other": 0
                    }
                return data
        except json.JSONDecodeError:
            # 文件损坏，重新创建
            print("⚠️ 数据文件损坏，重新创建")
            self.ensure_data_file()
            return self._load_data()
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return {"feedbacks": [], "summary": {
                "total_feedbacks": 0,
                "average_rating": 0,
                "usage_feedback": 0,
                "suggestion": 0,
                "bug_report": 0,
                "other": 0
            }}
    
    def _save_data(self, data):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
    
    def submit_feedback(self, feedback_data):
        """提交新反馈"""
        try:
            data = self._load_data()
            
            # 生成唯一ID和时间戳
            feedback_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().isoformat()
            
            feedback_record = {
                "id": feedback_id,
                "timestamp": timestamp,
                "type": feedback_data.get("type", "其他"),
                "rating": int(feedback_data.get("rating", 5)),
                "content": feedback_data.get("content", ""),
                "contact": feedback_data.get("contact", "")
            }
            
            # 添加到列表
            data["feedbacks"].append(feedback_record)
            
            # 更新统计
            self._update_summary(data)
            
            # 保存
            if self._save_data(data):
                return feedback_id
            return None
            
        except Exception as e:
            print(f"❌ 提交反馈失败: {e}")
            return None
    
    def _update_summary(self, data):
        """更新统计摘要"""
        feedbacks = data["feedbacks"]
        
        # 基础统计
        total = len(feedbacks)
        data["summary"]["total_feedbacks"] = total
        
        # 类型统计
        type_counts = {
            "usage_feedback": 0,  # 使用体验
            "suggestion": 0,      # 功能建议
            "bug_report": 0,      # 问题报告
            "other": 0            # 其他
        }
        
        # 评分统计
        ratings = []
        
        for fb in feedbacks:
            # 类型统计
            fb_type = fb.get("type", "").lower()
            if "体验" in fb_type or "使用" in fb_type:
                type_counts["usage_feedback"] += 1
            elif "建议" in fb_type or "功能" in fb_type:
                type_counts["suggestion"] += 1
            elif "问题" in fb_type or "报告" in fb_type or "bug" in fb_type:
                type_counts["bug_report"] += 1
            else:
                type_counts["other"] += 1
            
            # 评分统计
            rating = fb.get("rating", 0)
            if isinstance(rating, (int, float)) and 1 <= rating <= 5:
                ratings.append(rating)
        
        # 更新类型统计
        for key in type_counts:
            data["summary"][key] = type_counts[key]
        
        # 计算平均分
        if ratings:
            data["summary"]["average_rating"] = round(sum(ratings) / len(ratings), 2)
        else:
            data["summary"]["average_rating"] = 0
    
    def get_feedback_stats(self):
        """获取反馈统计"""
        try:
            data = self._load_data()
            return data["summary"]
        except:
            return {
                "total_feedbacks": 0,
                "average_rating": 0,
                "usage_feedback": 0,
                "suggestion": 0,
                "bug_report": 0,
                "other": 0
            }
    
    def get_all_feedbacks(self):
        """获取所有反馈"""
        try:
            data = self._load_data()
            feedbacks = data.get("feedbacks", [])
            
            # 按时间排序（最新的在前）
            def get_time(fb):
                ts = fb.get("timestamp", "")
                try:
                    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    return datetime.min
            
            return sorted(feedbacks, key=get_time, reverse=True)
        except Exception as e:
            print(f"❌ 获取所有反馈失败: {e}")
            return []
    
    def get_recent_feedbacks(self, limit=10):
        """获取最近反馈"""
        try:
            all_feedbacks = self.get_all_feedbacks()
            return all_feedbacks[:limit]
        except:
            return []
    
    def get_rating_distribution(self):
        """获取评分分布"""
        try:
            feedbacks = self.get_all_feedbacks()
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            for fb in feedbacks:
                rating = fb.get("rating", 0)
                if rating in distribution:
                    distribution[rating] += 1
            
            return distribution
        except:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

# 测试代码
if __name__ == "__main__":
    print("🧪 测试反馈系统...")
    fs = FeedbackSystem("test_feedback.json")
    
    # 测试提交
    test_data = {
        "type": "使用体验",
        "rating": 5,
        "content": "测试反馈内容",
        "contact": "test@example.com"
    }
    
    fid = fs.submit_feedback(test_data)
    print(f"提交结果: {fid}")
    
    # 查看统计
    stats = fs.get_feedback_stats()
    print(f"统计: {stats}")
    
    # 查看所有反馈
    feedbacks = fs.get_all_feedbacks()
    print(f"反馈数量: {len(feedbacks)}")