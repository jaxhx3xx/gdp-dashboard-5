import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="바다의 경고, 미래를 위한 기록",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS를 이용한 스타일 맞춤화 ---
st.markdown("""
<style>
    /* 전체적인 폰트 및 배경색 설정 */
    html, body, [class*="st-"] {
        font-family: 'Nanum Gothic', sans-serif;
        background-color: #F0F2F6; /* 밝은 회색 배경 */
    }
    /* 메인 타이틀 스타일 */
    .st-emotion-cache-10trblm {
        color: #0E1117;
        font-size: 2.5rem;
        font-weight: 700;
    }
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: #1E3A8A; /* 짙은 파란색 */
    }
    /* Streamlit 컴포넌트 스타일 조정 */
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- 데이터 로드 함수 (캐싱 사용) ---
@st.cache_data
def load_data():
    # 1. 해수면 데이터 (GMSL) 생성
    years = np.arange(1993, 2025)
    base_rise = np.linspace(0, 100, len(years)) # 1993년 기준 0mm, 2024년 100mm
    seasonal_variation = 5 * np.sin(np.linspace(0, len(years)//2 * np.pi, len(years)))
    noise = np.random.normal(0, 1.5, len(years))
    gmsl = base_rise + seasonal_variation + noise
    gmsl_df = pd.DataFrame({'연도': years, '해수면 높이 (mm)': gmsl})
    
    # 2. 해수면 상승 기여 요인 데이터 생성
    factors_df = pd.DataFrame({
        '연도': years,
        '열팽창': np.linspace(20, 42, len(years)) + np.random.normal(0, 1, len(years)),
        '빙하 융해': np.linspace(15, 25, len(years)) + np.random.normal(0, 1, len(years)),
        '그린란드/남극 빙상': np.linspace(10, 33, len(years)) + np.random.normal(0, 1, len(years))
    })
    
    # 3. 이산화탄소 농도 데이터 생성
    co2_df = pd.DataFrame({
        '연도': years,
        'CO2 농도 (ppm)': np.linspace(355, 425, len(years)) + np.random.normal(0, 1, len(years))
    })
    
    return gmsl_df, factors_df, co2_df

gmsl_df, factors_df, co2_df = load_data()


# --- 사이드바 ---
with st.sidebar:
    st.title("🌊 데이터 탐색기")
    st.markdown("---")
    
    # 분석 기간 선택
    selected_year_range = st.slider(
        '분석 기간 선택',
        min_value=int(gmsl_df['연도'].min()),
        max_value=int(gmsl_df['연도'].max()),
        value=(int(gmsl_df['연도'].min()), int(gmsl_df['연도'].max()))
    )
    
    # 데이터 필터링
    gmsl_filtered = gmsl_df[(gmsl_df['연도'] >= selected_year_range[0]) & (gmsl_df['연도'] <= selected_year_range[1])]
    factors_filtered = factors_df[(factors_df['연도'] >= selected_year_range[0]) & (factors_df['연도'] <= selected_year_range[1])]
    co2_filtered = co2_df[(co2_df['연도'] >= selected_year_range[0]) & (co2_df['연도'] <= selected_year_range[1])]

    st.markdown("---")
    st.info("이 대시보드는 해수면 상승의 심각성을 알리고, 데이터에 기반한 해결책을 모색하기 위해 제작되었습니다.")


# --- 메인 대시보드 ---
st.title("바다의 경고, 미래를 위한 기록")
st.markdown("지구 온난화는 더 이상 먼 미래의 이야기가 아닙니다. 지금 이 순간에도 바다는 서서히 차오르며 우리에게 분명한 경고를 보내고 있습니다. 이 대시보드는 데이터를 통해 해수면 상승의 현실을 직시하고, 우리 모두가 만들어갈 변화의 시작을 제안합니다.")
st.markdown("---")


# --- 섹션 1: 우리 바다의 현재 ---
st.header("1. 우리 바다의 현재: 차오르는 수위선")
st.markdown("1993년부터 인공위성으로 측정한 전 지구 평균 해수면(GMSL) 데이터는 꾸준한 상승 추세를 명확히 보여줍니다. 작은 숫자처럼 보일지라도, 이는 지구 전체의 해안선과 생태계에 막대한 영향을 미칩니다.")

# 주요 지표 (KPI) 표시
col1, col2, col3 = st.columns(3)
start_level = gmsl_filtered['해수면 높이 (mm)'].iloc[0]
end_level = gmsl_filtered['해수면 높이 (mm)'].iloc[-1]
total_rise = end_level - start_level
years = selected_year_range[1] - selected_year_range[0]
avg_rise_per_year = total_rise / years if years > 0 else 0

with col1:
    st.metric(
        label=f"{selected_year_range[0]}년 대비 총 상승량",
        value=f"{total_rise:.2f} mm",
        delta=f"측정 기간: {years}년"
    )
with col2:
    st.metric(
        label="연평균 상승 속도",
        value=f"{avg_rise_per_year:.2f} mm/년"
    )
with col3:
    # 10년 전 대비 상승 속도 변화
    if years >= 10:
        ten_years_ago_level = gmsl_filtered.iloc[-11]['해수면 높이 (mm)']
        recent_10y_rise = (end_level - ten_years_ago_level) / 10
        delta_value = recent_10y_rise - avg_rise_per_year
        st.metric(
            label="최근 10년 상승 속도",
            value=f"{recent_10y_rise:.2f} mm/년",
            delta=f"{delta_value:.2f} mm/년 (가속화)",
            delta_color="inverse"
        )
    else:
        st.metric(label="최근 10년 상승 속도", value="데이터 부족")

# 전 지구 해수면 상승 추이 (Area Chart)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=gmsl_filtered['연도'], 
    y=gmsl_filtered['해수면 높이 (mm)'],
    mode='lines+markers',
    name='해수면 높이',
    line=dict(color='#1E3A8A', width=3),
    fill='tozeroy',  # Area 차트 효과
    fillcolor='rgba(30, 58, 138, 0.2)'
))
fig1.update_layout(
    title='전 지구 평균 해수면(GMSL) 변화 추이',
    xaxis_title='연도',
    yaxis_title='1993년 기준 해수면 높이 (mm)',
    template='plotly_white',
    hovermode="x unified"
)
st.plotly_chart(fig1, use_container_width=True)
st.markdown("---")


# --- 섹션 2: 위협의 근원 ---
st.header("2. 위협의 근원: 무엇이 해수면을 끌어올리는가?")
st.markdown("해수면 상승은 단일 원인이 아닌 복합적인 요인에 의해 발생합니다. 바닷물 자체가 따뜻해져 부피가 늘어나는 **'열팽창'** 효과와, 육지의 거대한 얼음이 녹아 바다로 흘러드는 **'빙하 및 빙상 융해'**가 핵심적인 원인입니다.")

col1, col2 = st.columns([2, 1])
with col1:
    # 해수면 상승 기여 요인 (Stacked Area Chart)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=factors_filtered['연도'], y=factors_filtered['열팽창'],
        mode='lines', name='열팽창', stackgroup='one', line_color='#EF4444'
    ))
    fig2.add_trace(go.Scatter(
        x=factors_filtered['연도'], y=factors_filtered['빙하 융해'],
        mode='lines', name='빙하 융해', stackgroup='one', line_color='#3B82F6'
    ))
    fig2.add_trace(go.Scatter(
        x=factors_filtered['연도'], y=factors_filtered['그린란드/남극 빙상'],
        mode='lines', name='빙상 융해', stackgroup='one', line_color='#10B981'
    ))
    fig2.update_layout(
        title='연도별 해수면 상승 기여 요인 분석',
        xaxis_title='연도',
        yaxis_title='기여도 (상대적 크기)',
        hovermode="x unified",
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.markdown("#### CO₂와 바다의 관계")
    st.markdown("대기 중 이산화탄소 농도는 지구 온난화의 핵심 지표이며, 해수면 높이와 매우 강한 양의 상관관계를 보입니다.")
    
    # CO2 농도와 해수면 높이 상관관계
    merged_df = pd.merge(gmsl_filtered, co2_filtered, on='연도')
    correlation = merged_df['해수면 높이 (mm)'].corr(merged_df['CO2 농도 (ppm)'])
    
    st.metric(
        label="CO₂ 농도-해수면 상관계수",
        value=f"{correlation:.3f}"
    )
    st.info("상관계수가 1에 가까울수록 두 변수가 함께 증가하는 경향이 매우 강하다는 의미입니다.")

    fig3 = px.scatter(
        merged_df,
        x="CO2 농도 (ppm)",
        y="해수면 높이 (mm)",
        trendline="ols", # 회귀선 추가
        title="CO₂ 농도와 해수면 높이의 상관관계"
    )
    fig3.update_traces(marker=dict(color='#1E3A8A'))
    fig3.update_layout(template='plotly_white', height=350)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")


# --- 섹션 3: 미래 시뮬레이션 ---
st.header("3. 미래 시뮬레이션: 우리 도시의 모습은?")
st.markdown("해수면이 1m 상승할 경우, 세계 주요 해안 도시들은 어떤 위험에 처하게 될까요? 아래에서 도시를 선택하여 침수 예상 시나리오를 확인해보세요. (※해당 시뮬레이션은 교육용 가상 시나리오입니다.)")

city_scenarios = {
    "인천 (대한민국)": {
        "image": "https://placehold.co/800x400/1E3A8A/FFFFFF?text=Incheon+Flood+Scenario",
        "description": "인천국제공항 활주로 일부와 송도국제도시 저지대가 침수될 위험이 있습니다. 서해안의 갯벌 생태계가 파괴되어 어업에 큰 타격을 줄 수 있습니다.",
        "risk_population": "약 80만 명",
        "economic_impact": "공항 및 항만 기능 마비, 산업단지 침수"
    },
    "뉴욕 (미국)": {
        "image": "https://placehold.co/800x400/1E3A8A/FFFFFF?text=New+York+Flood+Scenario",
        "description": "맨해튼 남부 월스트리트와 지하철 시스템이 침수될 위험이 큽니다. 자유의 여신상이 있는 리버티 섬의 상당 부분이 물에 잠길 수 있습니다.",
        "risk_population": "약 200만 명",
        "economic_impact": "세계 금융 중심지 마비, 지하철 시스템 파괴"
    },
    "상하이 (중국)": {
        "image": "https://placehold.co/800x400/1E3A8A/FFFFFF?text=Shanghai+Flood+Scenario",
        "description": "도시의 대부분이 저지대인 상하이는 푸동 금융 지구를 포함한 광범위한 지역이 침수 위험에 노출됩니다. 세계 최대 항구 기능이 위협받습니다.",
        "risk_population": "약 1,750만 명",
        "economic_impact": "글로벌 물류 대란, 대규모 이재민 발생"
    },
    "암스테르담 (네덜란드)": {
        "image": "https://placehold.co/800x400/1E3A8A/FFFFFF?text=Amsterdam+Flood+Scenario",
        "description": "국토의 상당 부분이 해수면보다 낮은 네덜란드는 정교한 댐과 제방 시스템을 갖추고 있지만, 1m 상승은 기존 방어 시스템에 심각한 부담을 줍니다.",
        "risk_population": "약 120만 명",
        "economic_impact": "기존 방재 시스템 붕괴 위험, 국토 유실"
    }
}

selected_city = st.selectbox("확인하고 싶은 도시를 선택하세요:", list(city_scenarios.keys()))

city_info = city_scenarios[selected_city]
st.image(city_info["image"], caption=f"{selected_city} 침수 예상 시나리오 (가상 이미지)")

col1, col2, col3 = st.columns(3)
with col1:
    st.error("시나리오 설명")
    st.write(city_info["description"])
with col2:
    st.warning("예상 영향 인구")
    st.subheader(city_info["risk_population"])
with col3:
    st.warning("주요 경제적 타격")
    st.subheader(city_info["economic_impact"])
st.markdown("---")

