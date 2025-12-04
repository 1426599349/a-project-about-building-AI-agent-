# admin_dashboard.py - 简化版（不依赖pyarrow）
import streamlit as st
from metrics_dashboard import MetricsDashboard
from feedback_system import FeedbackSystem
from datetime import datetime
import json

def main():
    """后台数据面板主函数"""
    st.set_page_config(
        page_title="Agent 数据监控后台",
        page_icon="📊",
        layout="wide"
    )
    
    # 添加密码保护
    password = st.sidebar.text_input("管理员密码", type="password", key="admin_pwd")
    
    if password == "315315zjh":
        dashboard = MetricsDashboard()
        feedback_system = FeedbackSystem()
        
        # 顶部导航
        st.sidebar.title("📊 导航")
        tab = st.sidebar.radio(
            "选择功能",
            ["📈 性能监控", "💬 用户反馈", "📊 系统分析"]
        )
        
        if tab == "📈 性能监控":
            show_performance_dashboard(dashboard)
        elif tab == "💬 用户反馈":
            show_feedback_dashboard(feedback_system)
        elif tab == "📊 系统分析":
            show_system_analysis(dashboard, feedback_system)
        
    else:
        if password:
            st.error("密码错误！")
        
        st.title("🔒 Agent 数据监控后台")
        st.warning("请输入管理员密码访问数据面板")

def show_performance_dashboard(dashboard):
    """显示性能监控面板"""
    dashboard.show_dashboard()

def show_feedback_dashboard(feedback_system):
    """显示用户反馈面板"""
    st.title("💬 用户反馈分析")
    st.markdown("查看用户的反馈和建议，了解系统改进方向")
    
    try:
        # 获取反馈统计
        feedback_stats = feedback_system.get_feedback_stats()
        
        # KPI 指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总反馈数", feedback_stats.get("total_feedbacks", 0))
        
        with col2:
            avg_rating = feedback_stats.get("average_rating", 0)
            st.metric("平均评分", f"{avg_rating:.1f}/5")
        
        with col3:
            agent_feedback = feedback_stats.get("agent_feedback", 0)
            st.metric("Agent反馈", agent_feedback)
        
        with col4:
            bug_reports = feedback_stats.get("bug_reports", 0)
            st.metric("Bug报告", bug_reports)
        
        st.divider()
        
        # 获取所有反馈
        all_feedbacks = feedback_system.get_all_feedbacks()
        
        if all_feedbacks:
            st.subheader(f"📋 所有反馈记录 (共{len(all_feedbacks)}条)")
            
            # 搜索和筛选
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 搜索反馈内容", "")
            with col2:
                st.write("")
                show_all = st.checkbox("显示全部", True)
            
            # 显示反馈列表
            for i, fb in enumerate(all_feedbacks):
                # 如果搜索关键词不为空，检查是否匹配
                if search_term and search_term.lower() not in fb.get("content", "").lower():
                    continue
                
                # 格式化时间
                timestamp = fb.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        display_time = timestamp
                else:
                    display_time = "未知时间"
                
                # 创建可折叠的反馈卡片
                with st.expander(f"📄 {display_time} - {fb.get('type', '未知类型')}", expanded=(i==0 and not search_term)):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown(f"**反馈ID:** {fb.get('id', 'N/A')}")
                        st.markdown(f"**类型:** {fb.get('type', '未知')}")
                        
                        rating = fb.get('rating')
                        if rating:
                            stars = "⭐" * int(rating)
                            st.markdown(f"**评分:** {stars} ({rating}/5)")
                        else:
                            st.markdown("**评分:** 未评分")
                        
                        contact = fb.get('contact', '')
                        if contact:
                            st.markdown(f"**联系方式:** {contact}")
                    
                    with col2:
                        content = fb.get('content', '无内容')
                        st.markdown("**反馈内容:**")
                        st.write(content)
            
            st.divider()
            
            # 评分分布
            st.subheader("📊 评分分布")
            rating_dist = feedback_system.get_rating_distribution()
            
            if any(rating_dist.values()):
                # 使用Streamlit原生图表
                ratings = list(rating_dist.keys())
                counts = list(rating_dist.values())
                
                # 显示表格
                rating_data = []
                for rating, count in rating_dist.items():
                    if count > 0:
                        rating_data.append({
                            "评分": rating,
                            "数量": count,
                            "百分比": f"{(count/sum(counts))*100:.1f}%"
                        })
                
                if rating_data:
                    # 显示表格
                    for item in rating_data:
                        cols = st.columns([1, 2, 1])
                        with cols[0]:
                            st.markdown(f"**{item['评分']} 星**")
                        with cols[1]:
                            progress = item['数量'] / max(counts) if max(counts) > 0 else 0
                            st.progress(progress)
                        with cols[2]:
                            st.markdown(f"{item['数量']} 条 ({item['百分比']})")
            
            # 导出功能（使用JSON格式）
            st.divider()
            st.subheader("📥 数据导出")
            
            if st.button("导出反馈数据 (JSON)"):
                export_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_feedbacks": len(all_feedbacks),
                    "feedbacks": all_feedbacks
                }
                
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="下载JSON文件",
                    data=json_str,
                    file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
        else:
            st.info("暂无用户反馈，鼓励用户提供反馈来改进系统！")
            
    except Exception as e:
        st.error(f"加载反馈数据失败: {e}")
        st.info("请确保反馈系统正常运行")

def show_system_analysis(dashboard, feedback_system):
    """显示系统综合分析"""
    st.title("📊 系统综合分析")
    
    try:
        # 获取数据
        metrics = dashboard.get_performance_metrics()
        feedback_stats = feedback_system.get_feedback_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 系统健康度
            success_rate = metrics.get('success_rate', 0)
            
            if success_rate >= 95:
                health_status = "🟢 优秀"
            elif success_rate >= 85:
                health_status = "🟡 良好"
            else:
                health_status = "🔴 需关注"
            
            st.info(f"**系统健康度**: {health_status}")
            st.progress(success_rate / 100, text=f"API成功率: {success_rate}%")
        
        with col2:
            # 用户满意度
            avg_rating = feedback_stats.get('average_rating', 0)
            
            if avg_rating >= 4.5:
                satisfaction = "🟢 非常满意"
            elif avg_rating >= 4.0:
                satisfaction = "🟡 满意"
            elif avg_rating >= 3.0:
                satisfaction = "🟠 一般"
            else:
                satisfaction = "🔴 需改进"
            
            st.info(f"**用户满意度**: {satisfaction}")
            st.progress(avg_rating / 5, text=f"平均评分: {avg_rating:.1f}/5")
        
        st.divider()
        
        # 数据汇总
        st.subheader("📈 数据汇总")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API总调用", metrics.get('total_api_calls', 0))
            st.metric("成功调用", metrics.get('successful_calls', 0))
        
        with col2:
            st.metric("用户会话", metrics.get('total_sessions', 0))
            st.metric("平均响应时间", f"{metrics.get('average_response_time', 0):.2f}s")
        
        with col3:
            st.metric("用户反馈", feedback_stats.get('total_feedbacks', 0))
            st.metric("Bug报告", feedback_stats.get('bug_reports', 0))
        
        st.divider()
        
        # 改进建议
        st.subheader("💡 改进建议")
        
        suggestions = []
        
        if metrics.get('success_rate', 0) < 85:
            suggestions.append("优化API调用逻辑，提高成功率")
        
        if metrics.get('average_response_time', 0) > 5:
            suggestions.append("检查网络连接，优化响应时间")
        
        if feedback_stats.get('bug_reports', 0) > 0:
            suggestions.append("优先处理用户报告的Bug问题")
        
        if feedback_stats.get('total_feedbacks', 0) < 5:
            suggestions.append("增加反馈入口，收集更多用户意见")
        
        if suggestions:
            st.info("基于当前数据，建议：")
            for i, suggestion in enumerate(suggestions, 1):
                st.write(f"{i}. {suggestion}")
        else:
            st.success("✅ 系统运行状况良好，继续保持！")
            
    except Exception as e:
        st.error(f"系统分析失败: {e}")

if __name__ == "__main__":
    main()