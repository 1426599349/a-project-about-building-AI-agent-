# test_final.py
import streamlit as st

st.title("🎯 最终测试")
st.write("这是一个简单的测试页面")

name = st.text_input("你的名字")
if name:
    st.write(f"你好, {name}!")

if st.button("点击我"):
    st.balloons()
    st.success("成功！")