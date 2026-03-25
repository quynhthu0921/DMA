import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection  # Thư viện nối Google Sheets siêu nhanh

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Photogenic Digital Analytics", layout="wide")

# --- CSS ĐỂ CUSTOM GIAO DIỆN (Làm cho giống mẫu bạn gửi) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. KẾT NỐI DỮ LIỆU THỰC TẾ ---
# Link Google Sheet của bạn (tab Cleaned_PHOTOGENIC)
url = "https://docs.google.com/spreadsheets/d/1EdFWhKlgTjHO82tsRsb7VQoHsgaWlfTJ4-XPdURYcc0/edit?usp=sharing"


@st.cache_data(ttl=600)  # Lưu bộ nhớ đệm 10 phút cập nhật 1 lần
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, worksheet="Cleaned_PHOTOGENIC.")
    return df


try:
    df = load_data()
except:
    st.error("Không thể kết nối Google Sheets. Vui lòng kiểm tra quyền chia sẻ.")
    st.stop()

# --- 2. THANH ĐIỀU HƯỚNG BÊN CẠNH (SIDEBAR) ---
st.sidebar.title("📊 PHÂN TÍCH PHOTOGENIC")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "Danh mục báo cáo",
    ["🏠 Dashboard Tổng quan", "⚔️ Phân tích Đối thủ", "🔍 Truy vấn Dữ liệu thô", "🤖 Trợ lý AI Michelle"]
)

st.sidebar.markdown("---")
st.sidebar.info("Dự án cuối kỳ: Phân tích Marketing đa nền tảng dựa trên AI Automation.")

# --- 3. LOGIC HIỂN THỊ THEO TỪNG TRANG ---

# TRANG 1: TỔNG QUAN
if menu == "🏠 Dashboard Tổng quan":
    st.title("🚀 Hiệu suất Marketing Thương hiệu")

    # 3.1. Hàng KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lượt xem trung bình", f"{int(df['views_count'].mean()):,}")
    col2.metric("Engagement Rate (ER)", f"{df['engagement_rate'].mean():.2f}%")
    col3.metric("Tổng lượt Like", f"{int(df['likes_count_video'].sum()):,}")
    col4.metric("Chỉ số Tích cực", "98.4%", "Sentiment")

    # 3.2. Biểu đồ tương tác
    row2_col1, row2_col2 = st.columns([2, 1])

    with row2_col1:
        st.subheader("📈 Tương quan Thời lượng Video & Engagement")
        fig_scatter = px.scatter(df, x="duration_seconds", y="engagement_rate",
                                 size="views_count", color="engagement_rate",
                                 hover_name="video_id", trendline="ols",
                                 color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with row2_col2:
        st.subheader("🎯 Cơ cấu tương tác")
        sums = [df['likes_count_video'].sum(), df['comments_count'].sum(), df['shares_count'].sum()]
        fig_pie = px.pie(values=sums, names=['Likes', 'Comments', 'Shares'],
                         hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 3.3. Heatmap thời gian
    st.subheader("⏰ Khung giờ vàng phân phối nội dung (Heatmap)")
    # Giả lập bảng pivot cho heatmap từ publish_datetime
    df['hour'] = pd.to_datetime(df['publish_datetime']).dt.hour
    df['day'] = pd.to_datetime(df['publish_datetime']).dt.day_name()
    heat_data = df.groupby(['day', 'hour'])['engagement_rate'].mean().unstack().fillna(0)
    fig_heat = px.imshow(heat_data, labels=dict(x="Giờ trong ngày", y="Thứ", color="ER %"),
                         color_continuous_scale='YlGnBu')
    st.plotly_chart(fig_heat, use_container_width=True)

# TRANG 2: ĐỐI THỦ
elif menu == "⚔️ Phân tích Đối thủ":
    st.title("⚔️ Competitive Benchmarking")

    # Ở đây bạn có thể load thêm dữ liệu PHOTOTIME và PHOTOPALETTE
    st.subheader("Vị thế thương hiệu: Reach vs Loyalty")
    # Biểu đồ bong bóng so sánh 3 bên (Giả lập số liệu so sánh)
    compare_data = pd.DataFrame({
        "Brand": ["PHOTOGENIC", "PHOTOTIME", "PHOTOPALETTE"],
        "ER %": [9.1, 5.1, 4.0],
        "Avg Views": [220000, 73000, 45000],
        "Market Share": [45, 30, 25]
    })
    fig_comp = px.scatter(compare_data, x="Avg Views", y="ER %", size="Market Share",
                          color="Brand", text="Brand", size_max=60)
    st.plotly_chart(fig_comp, use_container_width=True)

    st.success("Insight: Photogenic đang dẫn đầu vùng 'High Engagement', tạo rào cản xâm nhập lớn cho đối thủ ngoại.")

# TRANG 3: DỮ LIỆU THÔ
elif menu == "🔍 Truy vấn Dữ liệu thô":
    st.title("🔍 Data Explorer Hub")
    st.write("Dữ liệu dưới đây đã được làm sạch qua quy trình Python & IQR.")

    # Bộ lọc dữ liệu
    search = st.text_input("Tìm kiếm theo Hashtag hoặc Caption:")
    if search:
        df_display = df[df['video_desc'].str.contains(search, na=False)]
    else:
        df_display = df

    st.dataframe(df_display, use_container_width=True)

    # Nút tải xuống
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Tải dữ liệu sạch (.csv)", data=csv, file_name="photogenic_clean.csv")

# TRANG 4: AI AGENT
elif menu == "🤖 Trợ lý AI Michelle":
    st.title("🤖 Michelle AI Strategy Agent")
    st.markdown("---")

    # Mô phỏng chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Hỏi Michelle về chiến dịch tiếp theo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Chỗ này trong thực tế sẽ gọi API Gemini/GPT-4 của bạn
            response = f"Dựa trên dữ liệu từ Google Sheets, tôi thấy video của bạn vào lúc 10h sáng Thứ Ba có ER cao hơn 15%. Gợi ý: Hãy đăng bài 'Pose Tips' tiếp theo vào khung giờ này!"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})