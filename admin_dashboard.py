# admin_dashboard.py - 后台数据面板入口
import streamlit as st
from metrics_dashboard import MetricsDashboard

def main():
    """后台数据面板主函数"""
    st.set_page_config(
        page_title="Agent 数据监控后台",
        page_icon="📊",
        layout="wide"
    )
    
    # 添加密码保护（简单版）
    password = st.sidebar.text_input("管理员密码", type="password")
    
    if password == "admin123":  # 在实际使用中应该使用更安全的认证方式
        dashboard = MetricsDashboard()
        dashboard.show_dashboard()
    else:
        if password:
            st.error("密码错误！")
        
        st.title("🔒 Agent 数据监控后台")
        st.warning("请输入管理员密码访问数据面板")
        
        st.info("""
        ### 📊 监控指标包括：
        - API 调用成功率
        - 平均响应时间
        - 用户会话统计
        - 系统健康状态
        - 趋势分析图表
        - 实时性能监控
        """)

if __name__ == "__main__":
    main()