import streamlit as st
import pandas as pd
import platform
import plotly.express as px  # 모듈 오류 방지를 위해 명확히 import
import plotly.graph_objects as go
from matplotlib import font_manager, rc

# 1. 환경 설정 (폰트 설정)
def setup_font():
    system_os = platform.system()
    if system_os == 'Windows':
        rc('font', family='Malgun Gothic')
    elif system_os == 'Darwin':
        rc('font', family='AppleGothic')
    else:
        # Streamlit Cloud(Linux) 환경 대응
        rc('font', family='NanumGothic')

setup_font()

# 2. 데이터 로드 및 전처리
@st.cache_data
def load_data(path):
    for enc in ['utf-8-sig', 'cp949', 'euc-kr']:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = df.columns.str.strip()
            # 수치 데이터 '만 톤' 단위 변환
            target_cols = ['총계', '외항소계', '외항입항', '외항출항', '외항입항환적', '외항출항환적', '내항연안화물']
            for col in target_cols:
                if col in df.columns:
                    df[f'{col}_만톤'] = df[col] / 10000
            return df
        except:
            continue
    return None

st.set_page_config(page_title="부산항 물동량 대시보드", layout="wide")

# --- [디자인 요소: CSS 애니메이션 및 세련된 타이포그래피] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;300;700;900&display=swap');

    /* 애니메이션 정의 */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 헤더 세션 스타일 */
    .header-container {
        padding: 50px 0px 30px 0px;
        text-align: left;
        border-bottom: 3px solid #1A1A1A;
        margin-bottom: 40px;
        animation: fadeInUp 0.8s ease-out;
    }
    .main-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 900;
        font-size: 3.5rem;
        color: #1A1A1A;
        letter-spacing: -2.5px;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    .sub-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 100;
        font-size: 1.5rem;
        color: #888888;
        letter-spacing: 5px;
    }
    .accent-point {
        color: #004e92;
        font-weight: 900;
    }

    /* 핵심 지표 세션 스타일 (미니멀리즘 카드) */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 40px;
    }
    .metric-card {
        flex: 1;
        background: #ffffff;
        padding: 25px 20px;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
        animation: fadeInUp 1s ease-out backwards;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.05);
        border-color: #004e92;
    }
    .metric-label { font-size: 0.9rem; color: #666; font-weight: 500; margin-bottom: 10px; }
    .metric-value { font-size: 2.2rem; font-weight: 900; color: #1A1A1A; margin-bottom: 5px; }
    .metric-delta { font-size: 0.95rem; font-weight: 700; }
    .delta-up { color: #d11212; }
    .delta-down { color: #125bd1; }

    /* 지표 카드별 순차 애니메이션 지연 */
    .delay-1 { animation-delay: 0.2s; }
    .delay-2 { animation-delay: 0.4s; }
    .delay-3 { animation-delay: 0.6s; }
    .delay-4 { animation-delay: 0.8s; }
    </style>
    """, unsafe_allow_html=True)

file_path = "부산항만공사_부산항 연도별 물동량 추이_20241231.csv"
df = load_data(file_path)

if df is not None:
    # --- [세션 1: 헤더] ---
    st.markdown("""
        <div class="header-container">
            <p class="sub-title">BUSAN PORT DATA INSIGHT</p>
            <h1 class="main-title">부산항 연도별 <span class="accent-point">물동량</span> 대시보드 ⚓</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # --- [세션 2: 핵심 지표 (미니멀리즘 카드)] ---
    latest_year = df['년도'].max()
    latest_df = df[df['년도'] == latest_year]
    total_val = latest_df['총계_만톤'].sum()
    prev_val = df[df['년도'] == (latest_year - 1)]['총계_만톤'].sum()
    delta = total_val - prev_val
    growth_rate = (delta/prev_val*100) if prev_val != 0 else 0
    top_port = latest_df.loc[latest_df['총계_만톤'].idxmax(), '항구분']

    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card delay-1">
                <div class="metric-label">전체 물동량 (만 톤)</div>
                <div class="metric-value">{total_val:,.0f}</div>
                <div class="metric-delta {'delta-up' if delta >= 0 else 'delta-down'}">
                    {'▲' if delta >= 0 else '▼'} {abs(delta):,.1f}
                </div>
            </div>
            <div class="metric-card delay-2">
                <div class="metric-label">전년 대비 성장률</div>
                <div class="metric-value">{growth_rate:.1f}%</div>
                <div class="metric-delta">Annual Growth</div>
            </div>
            <div class="metric-card delay-3">
                <div class="metric-label">최대 실적 거점</div>
                <div class="metric-value" style="font-size: 1.8rem; padding-top:10px;">{top_port}</div>
                <div class="metric-delta">Top Performing Port</div>
            </div>
            <div class="metric-card delay-4">
                <div class="metric-label">분석 기준 연도</div>
                <div class="metric-value">{latest_year}</div>
                <div class="metric-delta">Data Updated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- [나머지 세션: 카테고리별 분석] ---
    tab1, tab2, tab3 = st.tabs(["📊 연도별 추이 분석", "🚢 항구별 비교 분석", "📦 화물 세부 구성"])

    with tab1:
        st.subheader("연도별 물동량 변화 흐름")
        yearly_total = df.groupby('년도')['총계_만톤'].sum().reset_index()
        fig1 = px.area(yearly_total, x='년도', y='총계_만톤', template="plotly_white")
        fig1.update_traces(line_color='#1A1A1A', fillcolor='rgba(150, 150, 150, 0.1)')
        fig1.update_layout(transition_duration=1000)
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader(f"항구별 점유율 ({latest_year})")
            fig2 = px.pie(latest_df, values='총계_만톤', names='항구분', hole=0.7,
                          color_discrete_sequence=px.colors.sequential.Greys_r)
            fig2.update_traces(textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        with col_c2:
            st.subheader("항구별 성장 역사 비교")
            selected_ports = st.multiselect("비교 항구 선택", df['항구분'].unique(), default=['북항', '신항'])
            filtered_port = df[df['항구분'].isin(selected_ports)]
            fig3 = px.line(filtered_port, x='년도', y='총계_만톤', color='항구분', markers=True)
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.subheader("화물 유형별 상세 분포")
        comp_map = {'외항입항_만톤': '외항 입항', '외항출항_만톤': '외항 출항', '외항입항환적_만톤': '입항 환적', '외항출항환적_만톤': '출항 환적', '내항연안화물_만톤': '내항/연안'}
        comp_data = latest_df[list(comp_map.keys())].sum().sort_values()
        comp_data.index = [comp_map[idx] for idx in comp_data.index]
        fig4 = px.bar(x=comp_data.values, y=comp_data.index, orientation='h', color_continuous_scale='Greys')
        fig4.update_layout(coloraxis_showscale=False, xaxis_title="만 톤")
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("📝 전체 데이터 테이블 확인하기"):
        st.dataframe(df.sort_values(by='년도', ascending=False), use_container_width=True)

else:
    st.error("데이터 파일을 로드할 수 없습니다. 파일명과 경로를 확인해 주세요.")