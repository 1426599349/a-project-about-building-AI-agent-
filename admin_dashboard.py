# admin_dashboard.py - 反馈查看后台
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from feedback_system import FeedbackSystem

def main():
    st.set_page_config(
        page_title="AI职业规划师 - 后台管理系统",
        page_icon="📊",
        layout="wide"
    )
    
    # 登录验证
    if not authenticate():
        return
    
    # 初始化反馈系统
    feedback_system = FeedbackSystem()
    
    # 侧边栏导航
    st.sidebar.title("📊 导航")
    page = st.sidebar.radio("选择页面", ["📈 数据概览", "📋 反馈详情", "⚙️ 系统管理"])
    
    if page == "📈 数据概览":
        show_overview(feedback_system)
    elif page == "📋 反馈详情":
        show_feedback_details(feedback_system)
    elif page == "⚙️ 系统管理":
        show_system_management(feedback_system)

def authenticate():
    """用户认证"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # 登录界面
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔒 后台管理系统")
            
            with st.form("login_form"):
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                submitted = st.form_submit_button("登录")
                
                if submitted:
                    if username == "zjh" and password == "315315zjh":  # 可修改密码
                        st.session_state.authenticated = True
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")
            return False
    
    return True

def show_overview(feedback_system):
    """显示数据概览"""
    st.title("📈 数据概览")
    
    try:
        # 获取统计数据
        stats = feedback_system.get_feedback_stats()
        
        # 关键指标
        st.markdown("### 📊 关键指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总反馈数", stats.get("total_feedbacks", 0))
        
        with col2:
            avg_rating = stats.get("average_rating", 0)
            st.metric("平均评分", f"{avg_rating:.1f}/5")
        
        with col3:
            suggestions = stats.get("suggestion", 0)
            st.metric("功能建议", suggestions)
        
        with col4:
            bug_reports = stats.get("bug_report", 0)
            st.metric("问题报告", bug_reports)
        
        # 获取最近反馈
        st.markdown("### 📋 最近反馈")
        recent_feedbacks = feedback_system.get_recent_feedbacks(5)
        
        if recent_feedbacks:
            for fb in recent_feedbacks:
                with st.expander(f"📄 {fb.get('type', '未知')} - {fb.get('timestamp', '')[:10]}", expanded=False):
                    show_feedback_card(fb)
        else:
            st.info("暂无反馈记录")
        
        # 评分分布
        st.markdown("### ⭐ 评分分布")
        rating_dist = feedback_system.get_rating_distribution()
        
        if any(rating_dist.values()):
            # 显示分布图
            import plotly.graph_objects as go
            
            ratings = list(rating_dist.keys())
            counts = list(rating_dist.values())
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"{r}星" for r in ratings],
                    y=counts,
                    marker_color=['#ff4444', '#ff8844', '#ffcc44', '#88cc44', '#44aa44'],
                    text=counts,
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='用户评分分布',
                xaxis_title='评分',
                yaxis_title='数量',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 表格显示详细数据
            total = sum(counts)
            if total > 0:
                st.markdown("**详细数据:**")
                dist_data = []
                for rating, count in rating_dist.items():
                    if count > 0:
                        percentage = (count / total) * 100
                        dist_data.append({
                            "评分": f"{rating} 星",
                            "数量": count,
                            "百分比": f"{percentage:.1f}%"
                        })
                
                if dist_data:
                    st.dataframe(dist_data, use_container_width=True)
        
        # 反馈类型分布
        st.markdown("### 📊 反馈类型分布")
        
        try:
            all_feedbacks = feedback_system.get_all_feedbacks()
            
            type_data = {
                "使用体验": stats.get("usage_feedback", 0),
                "功能建议": stats.get("suggestion", 0),
                "问题报告": stats.get("bug_report", 0),
                "其他": stats.get("other", 0)
            }
            
            # 创建饼图
            import plotly.graph_objects as go
            
            labels = list(type_data.keys())
            values = list(type_data.values())
            
            # 只显示有数据的类型
            filtered_labels = []
            filtered_values = []
            for label, value in zip(labels, values):
                if value > 0:
                    filtered_labels.append(label)
                    filtered_values.append(value)
            
            if filtered_values:
                fig = go.Figure(data=[go.Pie(
                    labels=filtered_labels,
                    values=filtered_values,
                    hole=.3,
                    marker_colors=['#667eea', '#764ba2', '#f093fb', '#4facfe']
                )])
                
                fig.update_layout(
                    title='反馈类型分布',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无反馈数据")
                
        except Exception as e:
            st.error(f"生成类型分布图失败: {e}")
    
    except Exception as e:
        st.error(f"加载数据概览失败: {e}")

def show_feedback_details(feedback_system):
    """显示反馈详情"""
    st.title("📋 反馈详情")
    
    try:
        # 获取所有反馈
        all_feedbacks = feedback_system.get_all_feedbacks()
        
        if not all_feedbacks:
            st.info("暂无用户反馈记录")
            return
        
        # 搜索和筛选
        st.markdown("### 🔍 搜索与筛选")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("搜索关键词")
        
        with col2:
            # 获取所有类型
            all_types = ["全部", "使用体验", "功能建议", "问题报告", "其他"]
            filter_type = st.selectbox("反馈类型", all_types)
        
        with col3:
            min_rating = st.selectbox("最低评分", ["全部", "1星+", "2星+", "3星+", "4星+", "5星"])
        
        # 应用筛选
        filtered_feedbacks = []
        for fb in all_feedbacks:
            # 搜索过滤
            if search_term:
                if search_term.lower() not in fb.get("content", "").lower():
                    continue
            
            # 类型过滤
            if filter_type != "全部" and fb.get("type", "") != filter_type:
                continue
            
            # 评分过滤
            if min_rating != "全部":
                min_stars = int(min_rating[0])
                fb_rating = fb.get("rating", 0)
                if fb_rating < min_stars:
                    continue
            
            filtered_feedbacks.append(fb)
        
        # 显示统计
        st.info(f"📊 找到 {len(filtered_feedbacks)} 条反馈（共 {len(all_feedbacks)} 条）")
        
        # 批量操作
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 刷新数据", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📥 导出数据", use_container_width=True):
                export_data(filtered_feedbacks)
        
        # 分页显示
        items_per_page = 10
        total_pages = max(1, (len(filtered_feedbacks) + items_per_page - 1) // items_per_page)
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # 分页控制
        if total_pages > 1:
            page_cols = st.columns([2, 1, 2])
            with page_cols[0]:
                page_num = st.number_input("页码", min_value=1, max_value=total_pages, 
                                         value=st.session_state.current_page)
                st.session_state.current_page = page_num
            with page_cols[2]:
                st.caption(f"共 {total_pages} 页")
        
        # 计算当前页数据
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_feedbacks = filtered_feedbacks[start_idx:end_idx]
        
        # 显示反馈列表
        st.markdown(f"### 📄 反馈列表（第 {st.session_state.current_page} 页）")
        
        for i, fb in enumerate(page_feedbacks):
            with st.expander(f"#{start_idx + i + 1} {fb.get('type', '未知')} - {fb.get('timestamp', '')[:10]}", expanded=False):
                show_feedback_detail(fb)
        
        # 如果没有数据
        if not page_feedbacks:
            st.warning("没有找到匹配的反馈记录")
    
    except Exception as e:
        st.error(f"加载反馈详情失败: {e}")

def show_feedback_card(fb):
    """显示反馈卡片（简略版）"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 基本信息
        st.markdown(f"**ID:** `{fb.get('id', 'N/A')}`")
        
        rating = fb.get('rating', 0)
        stars = "⭐" * rating if rating > 0 else "未评分"
        st.markdown(f"**评分:** {stars}")
        
        contact = fb.get('contact', '')
        if contact:
            st.markdown(f"**联系方式:**")
            st.code(contact)
    
    with col2:
        # 内容预览
        content = fb.get('content', '')
        preview = content[:200] + "..." if len(content) > 200 else content
        
        st.markdown("**反馈内容:**")
        st.markdown(f"""
        <div style='
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 5px;
            border-left: 3px solid #667eea;
            margin: 0.5rem 0;
        '>
            {preview}
        </div>
        """, unsafe_allow_html=True)
        
        # 时间信息
        timestamp = fb.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.caption(f"提交时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                st.caption(f"提交时间: {timestamp}")

def show_feedback_detail(fb):
    """显示反馈详情（详细版）"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📋 基本信息")
        
        st.markdown(f"**反馈ID:**")
        st.code(fb.get('id', 'N/A'), language="text")
        
        st.markdown(f"**反馈类型:**")
        st.info(fb.get('type', '未知'))
        
        rating = fb.get('rating', 0)
        stars = "⭐" * rating if rating > 0 else "未评分"
        st.markdown(f"**用户评分:**")
        st.markdown(f"<h3>{stars}</h3>", unsafe_allow_html=True)
        
        contact = fb.get('contact', '')
        if contact:
            st.markdown(f"**联系方式:**")
            st.code(contact, language="text")
        
        # 时间信息
        timestamp = fb.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.markdown(f"**提交时间:**")
                st.markdown(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 计算时间差
                time_diff = datetime.now() - dt
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} 天前"
                elif time_diff.seconds > 3600:
                    time_ago = f"{time_diff.seconds // 3600} 小时前"
                elif time_diff.seconds > 60:
                    time_ago = f"{time_diff.seconds // 60} 分钟前"
                else:
                    time_ago = "刚刚"
                st.caption(f"（{time_ago}）")
            except:
                st.markdown(f"**提交时间:** {timestamp}")
    
    with col2:
        st.markdown("### 📝 反馈内容")
        
        content = fb.get('content', '')
        
        st.markdown(f"""
        <div style='
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            min-height: 200px;
            white-space: pre-wrap;
            line-height: 1.6;
        '>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # 内容统计
        st.markdown("---")
        content_length = len(content)
        word_count = len(content.split())
        char_count = len(content.replace(' ', ''))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总字数", content_length)
        with col2:
            st.metric("词数", word_count)
        with col3:
            st.metric("字符数", char_count)
        
        # 操作按钮
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 复制内容", key=f"copy_{fb.get('id')}", use_container_width=True):
                st.code(content, language="text")
                st.success("内容已复制到剪贴板")
        
        with col2:
            if st.button("🗑️ 删除反馈", key=f"delete_{fb.get('id')}", use_container_width=True, type="secondary"):
                st.warning("此操作不可恢复！")
                confirm = st.checkbox("确认删除", key=f"confirm_{fb.get('id')}")
                if confirm:
                    # 这里需要实现删除逻辑
                    st.error("删除功能需要数据库支持")

def export_data(feedbacks):
    """导出数据"""
    if not feedbacks:
        st.warning("没有数据可导出")
        return
    
    # 创建导出数据
    export_data = {
        "export_time": datetime.now().isoformat(),
        "total_feedbacks": len(feedbacks),
        "feedbacks": feedbacks
    }
    
    # 转换为JSON
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    # 提供下载
    st.download_button(
        label="📥 下载JSON文件",
        data=json_str,
        file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def show_system_management(feedback_system):
    """显示系统管理"""
    st.title("⚙️ 系统管理")
    
    st.markdown("### 📊 数据统计")
    
    try:
        stats = feedback_system.get_feedback_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 基础统计")
            for key, value in stats.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### 系统信息")
            
            # 检查数据文件
            data_file = "data/feedback.json"
            if os.path.exists(data_file):
                file_size = os.path.getsize(data_file)
                file_time = datetime.fromtimestamp(os.path.getmtime(data_file))
                
                st.info(f"""
                **数据文件信息:**
                - 路径: `{data_file}`
                - 大小: {file_size:,} 字节
                - 修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}
                """)
            else:
                st.warning("数据文件不存在")
    
    except Exception as e:
        st.error(f"获取系统信息失败: {e}")
    
    st.markdown("### ⚠️ 危险操作")
    
    with st.expander("数据管理", expanded=False):
        st.warning("⚠️ 以下操作不可恢复，请谨慎操作！")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 重新加载数据", type="secondary", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清空所有数据", type="secondary", use_container_width=True):
                confirm = st.checkbox("我确认要清空所有数据")
                confirm2 = st.checkbox("我知道此操作不可恢复")
                
                if confirm and confirm2:
                    try:
                        # 创建备份
                        backup_file = f"data/feedback_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        if os.path.exists("data/feedback.json"):
                            import shutil
                            shutil.copy2("data/feedback.json", backup_file)
                            st.info(f"已创建备份: {backup_file}")
                        
                        # 清空数据
                        feedback_system = FeedbackSystem()
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
                        
                        import json
                        with open("data/feedback.json", 'w', encoding='utf-8') as f:
                            json.dump(initial_data, f, ensure_ascii=False, indent=2)
                        
                        st.success("✅ 所有数据已清空")
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"清空数据失败: {e}")

if __name__ == "__main__":
    main()