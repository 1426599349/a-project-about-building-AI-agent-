# metrics_dashboard.py - 修复版（避免使用pyarrow）
import streamlit as st
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

class MetricsDashboard:
    def __init__(self, data_file="data/metrics.json"):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = {
                "api_calls": [],
                "sessions": [],
                "user_feedback": [],
                "performance_metrics": {
                    "total_api_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_response_time": 0,
                    "average_response_time": 0
                },
                "daily_stats": {}
            }
            self.save_data(initial_data)
    
    def load_data(self):
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据文件失败: {e}")
            self.ensure_data_file()
            return self.load_data()
    
    def save_data(self, data):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def record_api_call(self, success=True, response_time=None, user_input=None, error_msg=None):
        """记录API调用"""
        try:
            data = self.load_data()
            
            # 确保 api_calls 是列表
            if "api_calls" not in data or not isinstance(data["api_calls"], list):
                data["api_calls"] = []
            
            api_call = {
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "response_time": response_time,
                "user_input": user_input[:100] if user_input else None,
                "error_msg": error_msg
            }
            
            data["api_calls"].append(api_call)
            
            # 确保 performance_metrics 存在
            if "performance_metrics" not in data:
                data["performance_metrics"] = {
                    "total_api_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_response_time": 0,
                    "average_response_time": 0
                }
            
            # 更新性能指标
            data["performance_metrics"]["total_api_calls"] += 1
            if success:
                data["performance_metrics"]["successful_calls"] += 1
                if response_time:
                    data["performance_metrics"]["total_response_time"] += response_time
                    if data["performance_metrics"]["successful_calls"] > 0:
                        data["performance_metrics"]["average_response_time"] = (
                            data["performance_metrics"]["total_response_time"] / 
                            data["performance_metrics"]["successful_calls"]
                        )
            else:
                data["performance_metrics"]["failed_calls"] += 1
            
            # 确保 daily_stats 存在
            if "daily_stats" not in data:
                data["daily_stats"] = {}
            
            # 更新日统计
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in data["daily_stats"]:
                data["daily_stats"][today] = {
                    "api_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_response_time": 0,
                    "sessions": 0
                }
            
            data["daily_stats"][today]["api_calls"] += 1
            if success:
                data["daily_stats"][today]["successful_calls"] += 1
                if response_time:
                    data["daily_stats"][today]["total_response_time"] += response_time
            else:
                data["daily_stats"][today]["failed_calls"] += 1
            
            self.save_data(data)
            
        except Exception as e:
            print(f"记录API调用失败: {e}")
    
    def record_session(self, user_input=None, response=None):
        """记录用户会话"""
        try:
            data = self.load_data()
            
            # 确保 sessions 是列表
            if "sessions" not in data or not isinstance(data["sessions"], list):
                data["sessions"] = []
            
            session = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input[:100] if user_input else None,
                "response_preview": response[:200] if response else None,
                "session_duration": None
            }
            
            data["sessions"].append(session)
            
            # 确保 daily_stats 存在
            if "daily_stats" not in data:
                data["daily_stats"] = {}
            
            # 更新日统计
            today = datetime.now().strftime("%Y-%m-%d")
            if today in data["daily_stats"]:
                data["daily_stats"][today]["sessions"] += 1
            
            self.save_data(data)
            
        except Exception as e:
            print(f"记录会话失败: {e}")
    
    def record_feedback(self, feedback_data):
        """记录用户反馈"""
        try:
            data = self.load_data()
            
            # 确保 user_feedback 是列表
            if "user_feedback" not in data or not isinstance(data["user_feedback"], list):
                data["user_feedback"] = []
            
            feedback_record = {
                "timestamp": datetime.now().isoformat(),
                "rating": feedback_data.get("rating"),
                "type": feedback_data.get("type"),
                "content_preview": feedback_data.get("content", "")[:100]
            }
            
            data["user_feedback"].append(feedback_record)
            self.save_data(data)
            
        except Exception as e:
            print(f"记录反馈失败: {e}")
    
    def get_performance_metrics(self):
        """获取性能指标"""
        try:
            data = self.load_data()
            
            # 确保 performance_metrics 存在
            if "performance_metrics" not in data:
                data["performance_metrics"] = {
                    "total_api_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_response_time": 0,
                    "average_response_time": 0
                }
            
            metrics = data["performance_metrics"]
            
            # 计算成功率
            if metrics["total_api_calls"] > 0:
                success_rate = (metrics["successful_calls"] / metrics["total_api_calls"]) * 100
            else:
                success_rate = 0
            
            return {
                "total_api_calls": metrics["total_api_calls"],
                "successful_calls": metrics["successful_calls"],
                "failed_calls": metrics["failed_calls"],
                "success_rate": round(success_rate, 2),
                "average_response_time": round(metrics["average_response_time"], 2) if metrics["average_response_time"] > 0 else 0,
                "total_sessions": len(data.get("sessions", [])),
                "total_feedback": len(data.get("user_feedback", []))
            }
        except Exception as e:
            print(f"获取性能指标失败: {e}")
            return {
                "total_api_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "success_rate": 0,
                "average_response_time": 0,
                "total_sessions": 0,
                "total_feedback": 0
            }
    
    def get_recent_activity(self, hours=24):
        """获取最近活动"""
        try:
            data = self.load_data()
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_api_calls = [
                call for call in data.get("api_calls", [])
                if datetime.fromisoformat(call["timestamp"]) > cutoff_time
            ]
            
            recent_sessions = [
                session for session in data.get("sessions", [])
                if datetime.fromisoformat(session["timestamp"]) > cutoff_time
            ]
            
            recent_api_count = len(recent_api_calls)
            recent_success_count = len([c for c in recent_api_calls if c.get("success", False)])
            
            return {
                "recent_api_calls": recent_api_count,
                "recent_sessions": len(recent_sessions),
                "recent_success_rate": (recent_success_count / recent_api_count * 100) if recent_api_count > 0 else 0
            }
        except Exception as e:
            print(f"获取最近活动失败: {e}")
            return {
                "recent_api_calls": 0,
                "recent_sessions": 0,
                "recent_success_rate": 0
            }
    
    def get_daily_stats(self, days=7):
        """获取日统计数据 - 简化版"""
        try:
            data = self.load_data()
            
            if "daily_stats" not in data:
                data["daily_stats"] = {}
            
            # 获取最近days天的数据
            dates = []
            api_calls = []
            success_rates = []
            avg_response_times = []
            sessions = []
            
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                dates.insert(0, date)
                
                if date in data["daily_stats"]:
                    stats = data["daily_stats"][date]
                    total_calls = stats.get("api_calls", 0)
                    successful = stats.get("successful_calls", 0)
                    
                    api_calls.insert(0, total_calls)
                    success_rates.insert(0, (successful / total_calls * 100) if total_calls > 0 else 0)
                    avg_response_times.insert(0, (stats.get("total_response_time", 0) / successful) if successful > 0 else 0)
                    sessions.insert(0, stats.get("sessions", 0))
                else:
                    api_calls.insert(0, 0)
                    success_rates.insert(0, 0)
                    avg_response_times.insert(0, 0)
                    sessions.insert(0, 0)
            
            return {
                'dates': dates,
                'api_calls': api_calls,
                'success_rates': success_rates,
                'avg_response_times': avg_response_times,
                'sessions': sessions
            }
                
        except Exception as e:
            print(f"获取日统计数据失败: {e}")
            return {
                'dates': [],
                'api_calls': [],
                'success_rates': [],
                'avg_response_times': [],
                'sessions': []
            }
    
    def show_dashboard(self):
        """显示数据面板"""
        st.title("📊 Agent 数据监控面板")
        st.markdown("实时监控AI职业规划师的性能指标和使用情况")
        
        try:
            # 获取数据
            metrics = self.get_performance_metrics()
            recent_activity = self.get_recent_activity(24)
            daily_data = self.get_daily_stats(7)
            
            if not daily_data['dates']:
                st.info("暂无数据可显示，请先使用Agent进行一些对话")
                return
            
            # KPI 指标卡片
            st.subheader("📈 关键性能指标")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "API 成功率",
                    f"{metrics['success_rate']}%",
                    f"{recent_activity['recent_success_rate']:.1f}% (24h)"
                )
            
            with col2:
                st.metric(
                    "平均响应时间", 
                    f"{metrics['average_response_time']}s",
                    f"{recent_activity['recent_api_calls']} 次调用(24h)"
                )
            
            with col3:
                st.metric(
                    "总会话数",
                    f"{metrics['total_sessions']}",
                    f"{recent_activity['recent_sessions']} (24h)"
                )
            
            with col4:
                st.metric(
                    "用户反馈数",
                    f"{metrics['total_feedback']}",
                    "满意度监控"
                )
            
            # 图表区域
            st.subheader("📊 趋势分析")
            
            # API性能图表
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=daily_data['dates'], 
                y=daily_data['success_rates'],
                mode='lines+markers',
                name='API成功率',
                line=dict(color='#00ff88', width=3)
            ))
            fig1.update_layout(
                title='API 成功率趋势 (7天)',
                xaxis_title='日期',
                yaxis_title='成功率 (%)',
                template='plotly_dark'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # 响应时间图表
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=daily_data['dates'], 
                y=daily_data['avg_response_times'],
                mode='lines+markers',
                name='平均响应时间',
                line=dict(color='#ffaa00', width=3)
            ))
            fig2.update_layout(
                title='平均响应时间趋势 (7天)',
                xaxis_title='日期',
                yaxis_title='响应时间 (秒)',
                template='plotly_dark'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # 使用情况图表
            col1, col2 = st.columns(2)
            
            with col1:
                # API调用量柱状图
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=daily_data['dates'], 
                    y=daily_data['api_calls'],
                    name='API调用量',
                    marker_color='#636efa'
                ))
                fig3.update_layout(
                    title='每日API调用量',
                    xaxis_title='日期',
                    yaxis_title='调用次数'
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # 会话数图表
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    x=daily_data['dates'],
                    y=daily_data['sessions'],
                    name='用户会话数',
                    marker_color='#ef553b'
                ))
                fig4.update_layout(
                    title='每日用户会话数',
                    xaxis_title='日期',
                    yaxis_title='会话数'
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            # 详细数据
            st.subheader("📋 详细统计数据")
            for i in range(len(daily_data['dates'])):
                with st.expander(f"日期: {daily_data['dates'][i]}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("API调用", daily_data['api_calls'][i])
                    with col2:
                        st.metric("成功率", f"{daily_data['success_rates'][i]:.1f}%")
                    with col3:
                        st.metric("响应时间", f"{daily_data['avg_response_times'][i]:.2f}s")
                    with col4:
                        st.metric("会话数", daily_data['sessions'][i])
            
            # 系统状态
            st.subheader("🔧 系统状态")
            col1, col2 = st.columns(2)
            
            with col1:
                # 健康状态指示器
                success_rate = metrics['success_rate']
                if success_rate >= 95:
                    status = "🟢 优秀"
                    color = "green"
                elif success_rate >= 85:
                    status = "🟡 良好"
                    color = "yellow"
                else:
                    status = "🔴 需关注"
                    color = "red"
                
                st.info(f"**系统健康状态**: {status}")
                st.progress(success_rate / 100, text=f"API成功率: {success_rate}%")
            
            with col2:
                # 响应时间状态
                avg_time = metrics['average_response_time']
                if avg_time <= 2:
                    time_status = "🟢 快速"
                elif avg_time <= 5:
                    time_status = "🟡 正常"
                else:
                    time_status = "🔴 较慢"
                
                st.info(f"**响应时间**: {time_status} ({avg_time}s)")
            
            # 实时监控
            st.subheader("🕒 实时监控")
            if st.button("🔄 刷新数据"):
                st.rerun()
            
            # 显示最近活动
            st.write(f"**最近24小时活动**:")
            st.write(f"- API调用: {recent_activity['recent_api_calls']} 次")
            st.write(f"- 用户会话: {recent_activity['recent_sessions']} 次")
            st.write(f"- 成功率: {recent_activity['recent_success_rate']:.1f}%")
            
        except Exception as e:
            st.error(f"显示数据面板时出错: {e}")
            st.info("请检查数据文件是否完整")

def main():
    """数据面板主函数"""
    dashboard = MetricsDashboard()
    dashboard.show_dashboard()

if __name__ == "__main__":
    main()