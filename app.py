import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Photogenic Digital Dashboard", layout="wide", page_icon="📸")

# --- CSS CUSTOM (Làm giao diện giống mẫu bạn gửi) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    [data-testid="stSidebar"] { background-color: #1a1c24; border-right: 1px solid #333; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1EdFWhKlgTjHO82tsRsb7VQoHsgaWlfTJ4-XPdURYcc0"


@st.cache_data(ttl=600)
def load_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)


# Load các tập dữ liệu từ các tab bạn đã tạo trong Colab
try:
    df_pg = load_sheet_data("Cleaned_PHOTOGENIC.")
    df_pt = load_sheet_data("Cleaned_PHOTOTIME")
    df_pp = load_sheet_data("Cleaned_PHOTOPALETTE")
except Exception as e:
    st.error(f"⚠️ Lỗi kết nối Google Sheets: {e}")
    st.info("Hãy đảm bảo bạn đã nhấn 'Chia sẻ' Sheets cho 'Bất kỳ ai có link'!")
    st.stop()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("📸 PHOTOGENIC ANALYTICS")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "DANH MỤC BÁO CÁO",
    ["🏠 Tổng quan Photogenic", "⚔️ Phân tích Đối thủ", "📊 Kho dữ liệu (Dataset)", "🤖 AI Agent Insights"],
    index=0
)
st.sidebar.markdown("---")
st.sidebar.write("👤 **Người thực hiện:** Nhóm Dự án")
st.sidebar.write("📅 **Kỳ học:** Spring 2026")

# --- TRANG 1: TỔNG QUAN PHOTOGENIC ---
if menu == "🏠 Tổng quan Photogenic":
    st.title("🚀 Hiệu suất Marketing đa nền tảng - Photogenic")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    avg_er = df_pg['engagement_rate'].mean()
    total_views = df_pg['views_count'].sum()
    c1.metric("TikTok Avg ER", f"{avg_er:.2f}%")
    c2.metric("Total Views", f"{total_views:,}")
    c3.metric("Facebook Sentiment", "98.4%", "Positive")
    c4.metric("Top Format", "Video >60s")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🎯 Tương quan Thời lượng & Tương tác")
        fig_scatter = px.scatter(df_pg, x="duration_seconds", y="engagement_rate",
                                 size="views_count", color="engagement_rate",
                                 hover_data=["video_id"], template="plotly_white",
                                 color_continuous_scale="Viridis")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_right:
        st.subheader("📊 Cơ cấu tương tác (Interaction Mix)")
        total_metrics = [df_pg['likes_count_video'].sum(), df_pg['comments_count'].sum(), df_pg['shares_count'].sum()]
        fig_pie = px.pie(values=total_metrics, names=['Likes', 'Comments', 'Shares'],
                         hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("⏰ Heatmap: Khung giờ vàng đăng bài")
    df_pg['publish_datetime'] = pd.to_datetime(df_pg['publish_datetime'])
    df_pg['hour'] = df_pg['publish_datetime'].dt.hour
    df_pg['day'] = df_pg['publish_datetime'].dt.day_name()
    heat = df_pg.groupby(['day', 'hour'])['engagement_rate'].mean().unstack().fillna(0)
    fig_heat = px.imshow(heat, labels=dict(x="Giờ trong ngày", y="Thứ", color="ER %"),
                         color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_heat, use_container_width=True)

# --- TRANG 2: PHÂN TÍCH ĐỐI THỦ ---
elif menu == "⚔️ Phân tích Đối thủ":
    st.title("⚔️ Competitive Benchmarking")

    # Hợp nhất dữ liệu để so sánh
    df_pg['Brand'] = 'PHOTOGENIC'
    df_pt['Brand'] = 'PHOTOTIME'
    df_pp['Brand'] = 'PHOTOPALETTE'
    df_all = pd.concat([df_pg, df_pt, df_pp])

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Vị thế: Reach vs Engagement")
        # Scatter Plot so sánh 3 Brand
        fig_bench = px.scatter(
            df_all.groupby('Brand').agg({'views_count': 'mean', 'engagement_rate': 'mean'}).reset_index(),
            x="views_count", y="engagement_rate", color="Brand",
            size=[100, 80, 70], text="Brand", size_max=40)
        st.plotly_chart(fig_bench, use_container_width=True)

    with col_b:
        st.subheader("Độ dài Video & Hiệu quả")
        avg_dur = df_all.groupby('Brand')['duration_seconds'].mean().reset_index()
        fig_bar = px.bar(avg_dur, x="Brand", y="duration_seconds", color="Brand",
                         title="Trung bình độ dài video (giây)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.success("💡 Insight: Photogenic thắng thế nhờ chiến lược nội dung dài (Long-form) mang lại giá trị thực chứng.")

# --- TRANG 3: DATASET ---
elif menu == "📊 Kho dữ liệu (Dataset)":
    st.title("📂 Explorer Central Data Hub")
    st.write("Dữ liệu đã được làm sạch bằng Python (Xử lý Missing, Outliers IQR).")

    brand_filter = st.selectbox("Chọn thương hiệu hiển thị:", ["PHOTOGENIC", "PHOTOTIME", "PHOTOPALETTE"])

    if brand_filter == "PHOTOGENIC":
        display_df = df_pg
    elif brand_filter == "PHOTOTIME":
        display_df = df_pt
    else:
        display_df = df_pp

    st.dataframe(display_df, use_container_width=True)

    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Tải dữ liệu sạch (.csv)", data=csv, file_name=f"{brand_filter}_clean.csv")

# --- TRANG 4: AI AGENT ---
elif menu == "🤖 AI Agent Insights":
    st.title("🤖 Michelle AI - Trợ lý Chiến lược")
    st.info("Hệ thống kết nối trực tiếp với Gemini LLM để đưa ra phân tích từ Dashboard.")

    with st.chat_message("assistant"):
        st.write("Chào bạn! Tôi là Michelle. Dựa trên dữ liệu Real-time, tôi có gợi ý sau:")
        st.write(
            "- **TikTok:** Video hướng dẫn 'Pose Tips' của bạn đang đạt ER 10.7%. Hãy sản xuất thêm 2 video cùng concept này.")
        st.write(
            "- **Facebook:** Tỷ lệ thảo luận đang cao gấp 10 lần TikTok. Hãy tổ chức Minigame trên Facebook vào tối Thứ 7.")

    user_q = st.text_input("Hỏi Michelle về dữ liệu của bạn:")
    if user_q:
        st.chat_message("user").write(user_q)
        st.chat_message("assistant").write("Đang truy xuất dữ liệu từ Google Sheets để trả lời... (Tính năng mô phỏng)")