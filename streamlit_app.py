import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import json
import random

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="바다의 경고: 해수면 상승과 우리 식탁의 미래",
    page_icon="🌊",
    layout="wide"
)

# --- CSS를 이용한 스타일 맞춤화 ---
st.markdown("""
<style>
    html, body, [class*="st-"] {
        font-family: 'Nanum Gothic', sans-serif;
        background-color: #F0F2F6;
    }
    h1, h2, h3 { color: #1E3A8A; }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1gwan2g {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 데이터 로드 함수 (캐싱 사용) ---
@st.cache_data
def load_data():
    # 1. 해수면 데이터 (GMSL) 생성
    years = np.arange(1993, 2025)
    base_rise = np.linspace(0, 100, len(years))
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

    # 3. 지도 데이터 생성 (연도별)
    map_years = np.arange(1993, 2025)
    map_df_list = []
    countries = ['USA', 'CHN', 'IND', 'RUS', 'JPN', 'DEU', 'KOR', 'CAN', 'BRA', 'AUS', 'IDN', 'MEX', 'SAU', 'GBR', 'FRA', 'ITA', 'NLD', 'BGD', 'VNM', 'EGY', 'NGA']
    base_rates = {country: np.random.uniform(2.5, 5.5) for country in countries}
    for year in map_years:
        for country in countries:
            rate = base_rates[country] + (year - 1993) * np.random.uniform(0.01, 0.05)
            map_df_list.append({'연도': year, 'country_iso': country, 'rise_rate_mm_year': rate})
    map_df = pd.DataFrame(map_df_list)

    # 4. 영양 섭취 데이터 생성
    nutrition_data = {
        '연도': [2002, 2007, 2014, 2023],
        '칼슘 섭취지수(%)': [100, 95, 88, 81],
        '철 섭취지수(%)': [100, 94, 86, 80],
        '오메가3 섭취지수(%)': [100, 93, 83, 76]
    }
    nutrition_df = pd.DataFrame(nutrition_data)

    # 5. 플라스틱 쓰레기 데이터
    plastic_data = {
        '연도': [2019, 2020, 2021, 2022, 2023],
        '플라스틱 비율 (%)': [81.0, 84.5, 90.6, 92.2, 87.0]
    }
    plastic_df = pd.DataFrame(plastic_data)

    # 6. 전체 해양 쓰레기 데이터
    debris_data = {
        '연도': [2019, 2020, 2021, 2022, 2023],
        '해안쓰레기 (톤)': [37900, 40350, 35850, 37600, 40200],
        '침적쓰레기 (톤)': [59400, 81000, 73600, 79000, 81600],
        '부유쓰레기 (톤)': [11344, 16012, 11286, 9435, 10130]
    }
    debris_df = pd.DataFrame(debris_data)

    # 7. 어획량 데이터
    fish_production_data = {
        '연도': [2019, 2020, 2021, 2022, 2023, 2024],
        '멸치 생산량 (톤)': [171677, 216748, 143414, 132152, 147770, 120028],
        '갈치 생산량 (톤)': [43479, 65719, 63056, 54024, 60671, 44506],
        '살오징어 생산량 (톤)': [27779, 25000, 24000, 22000, 20000, 14000]
    }
    fish_production_df = pd.DataFrame(fish_production_data)

    # 8. 양식 생산량 데이터
    aquaculture_data = {
        '연도': [2014, 2016, 2018, 2020, 2022],
        '김 생산량 (톤)': [523648, 567827, 536127, 523000, 500000],
        '미역 생산량 (톤)': [622613, 515666, 501501, 490000, 460000],
        '굴 생산량 (톤)': [31092, 25805, 20000, 18000, 16000]
    }
    aquaculture_df = pd.DataFrame(aquaculture_data)

    # 9. 온실가스 데이터
    ghg_data = {
        '연도': [1990, 1995, 2000, 2005, 2010, 2015, 2020],
        '총 배출량(백만 톤 CO2eq)': [3060, 3700, 4000, 4500, 5200, 6000, 6562],
        'CO2 비율(%)': [86.5, 87, 87, 88, 89, 90, 91.4],
        'CH4 비율(%)': [5.5, 5, 5, 4.8, 4.5, 4.3, 4.1],
        'N2O 비율(%)': [3.5, 3, 3, 3, 2.5, 2.3, 2.1],
        '기타 가스 비율(%)': [1.5, 2, 2, 1.2, 1.5, 1.7, 2.4]
    }
    ghg_df = pd.DataFrame(ghg_data)

    # 10. 대한민국 지역별 어획량 데이터
    kr_fishery_data_str = """
연도,여수,부산,목포,통영,인천,군산,울산
2000,92000,105000,78000,82000,88000,50000,47000
2002,91200,104300,76000,80700,87000,48600,46000
2004,89400,102500,75800,79000,85400,47300,45000
2006,88500,101200,73600,77500,84500,46000,44200
2008,87200,99400,72000,76000,83000,45400,43000
2010,86000,97000,70000,74500,81000,44000,42100
2012,85200,95800,68200,73000,80000,43000,41000
2014,84000,93000,66600,71500,78400,42000,40300
2016,83000,89400,64800,70000,75400,40500,39000
2018,81800,87200,63500,69000,72800,39600,38100
2020,80000,83000,61000,67500,70000,38000,37000
2022,79000,81000,59800,66000,68000,36800,36200
2024,78000,78000,58500,64000,66500,35600,35000
"""
    df_wide = pd.read_csv(io.StringIO(kr_fishery_data_str.strip()))
    df_long = df_wide.melt(id_vars='연도', var_name='도시', value_name='어획량_톤')
    region_map = {
        '여수': '전라남도', '부산': '부산광역시', '목포': '전라남도', '통영': '경상남도',
        '인천': '인천광역시', '군산': '전라북도', '울산': '울산광역시'
    }
    df_long['지역'] = df_long['도시'].map(region_map)
    regional_fishery_df = df_long.groupby(['연도', '지역'])['어획량_톤'].sum().reset_index()

    return gmsl_df, factors_df, map_df, nutrition_df, plastic_df, debris_df, fish_production_df, aquaculture_df, ghg_df, regional_fishery_df

# --- 대한민국 지도 GeoJSON 데이터 로드 ---
@st.cache_data
def load_korea_geojson():
    # 출처: https://github.com/southkorea/southkorea-maps
    # 라이선스에 따라 출처 명시
    with open('skorea-provinces-2013-geo.json', 'r', encoding='utf-8') as f:
        korea_geojson_data = json.load(f)
    return korea_geojson_data
    
# --- 데이터 로드 ---
(gmsl_df, factors_df, map_df, nutrition_df, plastic_df, debris_df, 
 fish_production_df, aquaculture_df, ghg_df, regional_fishery_df) = load_data()

# GeoJSON 파일이 없을 경우를 대비한 예외 처리
try:
    korea_geojson = load_korea_geojson()
except FileNotFoundError:
    st.error("대한민국 지도 파일('skorea-provinces-2013-geo.json')을 찾을 수 없습니다. 코드와 같은 폴더에 지도 파일을 넣어주세요.")
    korea_geojson = None # 지도가 없어도 앱이 멈추지 않도록 설정

baseline_2020_level = gmsl_df[gmsl_df['연도'] == 2020]['해수면 높이 (mm)'].iloc[0]
gmsl_df['해수면 높이 (mm)'] = gmsl_df['해수면 높이 (mm)'] - baseline_2020_level

st.title("바다의 경고: 해수면 상승과 우리 식탁의 미래")
st.markdown("### 문제 제기\n최근 여름철 기온이 꾸준히 상승하고 있습니다. 이는 지구온난화로 인한 현상이며, 단순한 온도 상승이 아닌 다양한 연쇄적 위기를 불러옵니다.")
st.markdown("""
- **빙하 융해:** 북극·남극의 빙하가 급속도로 녹아내립니다.
- **해양 생태계 파괴:** 해수온이 상승하며 해양 생물의 서식지가 파괴됩니다.
- **해수면 상승:** 위의 두 요인으로 인해 해수면이 상승하여 해안 도시와 섬 국가가 침수 위기에 처합니다.
""")
st.info("이미 태평양의 투발루는 일부 섬이 사라지고 있으며, 몰디브는 국토의 대부분이 해발 1m 이하로, 해수면 상승에 직접적인 위협을 받고 있습니다.")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 전 지구 현황", "🇰🇷 대한민국 현황", "🐟 우리의 식탁", "🏙️ 미래 시나리오", "🎮 인터랙티브 게임", "📑 종합 보고서"])

with tab1:
    st.header("1. 전 지구 평균 해수면(GMSL) 변화 추이")
    st.markdown("1993년부터 인공위성으로 측정한 전 지구 평균 해수면 데이터는 장기적으로 꾸준한 상승 추세를 명확히 보여줍니다. **꺾은선은 각 연도의 평균 해수면 높이를, 파란색으로 채워진 영역은 기준 연도(2020년) 대비 총 상승량을 시각적으로 나타냅니다.** 그래프의 미세한 상하 변동은 계절에 따른 해수의 열팽창/수축, 빙하의 융해/결빙 주기 등 자연적인 요인을 포함하고 있기 때문입니다.")
    
    selected_year_range = st.slider('해수면 데이터 분석 기간 선택', min_value=int(gmsl_df['연도'].min()), max_value=int(gmsl_df['연도'].max()), value=(int(gmsl_df['연도'].min()), int(gmsl_df['연도'].max())))
    gmsl_filtered = gmsl_df[(gmsl_df['연도'] >= selected_year_range[0]) & (gmsl_df['연도'] <= selected_year_range[1])]

    col1, col2, col3 = st.columns(3)
    start_level = gmsl_filtered['해수면 높이 (mm)'].iloc[0]
    end_level = gmsl_filtered['해수면 높이 (mm)'].iloc[-1]
    total_rise = end_level - start_level
    years_diff = selected_year_range[1] - selected_year_range[0]
    avg_rise_per_year = total_rise / years_diff if years_diff > 0 else 0
    with col1:
        st.metric(label=f"총 상승량", value=f"{total_rise:.2f} mm", delta=f"측정 기간: {years_diff}년")
    with col2:
        st.metric(label="연평균 상승 속도", value=f"{avg_rise_per_year:.2f} mm/년")
    with col3:
        if years_diff >= 10:
            ten_years_ago_level = gmsl_filtered.iloc[-11]['해수면 높이 (mm)']
            recent_10y_rise = (end_level - ten_years_ago_level) / 10
            delta_value = recent_10y_rise - avg_rise_per_year
            st.metric(label="최근 10년 상승 속도", value=f"{recent_10y_rise:.2f} mm/년", delta=f"{delta_value:.2f} mm/년 (가속화)", delta_color="inverse")
        else:
            st.metric(label="최근 10년 상승 속도", value="데이터 부족")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=gmsl_filtered['연도'], y=gmsl_filtered['해수면 높이 (mm)'], mode='lines+markers', name='해수면 높이', line=dict(color='#1E3A8A', width=3), fill='tozeroy', fillcolor='rgba(30, 58, 138, 0.2)'))
    fig1.update_layout(title='전 지구 평균 해수면(GMSL) 변화 추이', xaxis_title='연도', yaxis_title='2020년 기준 해수면 높이 (mm)', template='plotly_white', hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("자료 출처: [NASA, Global Average Sea Level](https://climate.nasa.gov/vital-signs/sea-level/) 데이터를 기반으로 생성된 가상 데이터")
    st.markdown("---")
    
    st.header("2. 무엇이 해수면을 끌어올리는가?")
    factors_filtered = factors_df[(factors_df['연도'] >= selected_year_range[0]) & (factors_df['연도'] <= selected_year_range[1])]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=factors_filtered['연도'], y=factors_filtered['열팽창'], mode='lines', name='열팽창', stackgroup='one', line_color='#EF4444'))
    fig2.add_trace(go.Scatter(x=factors_filtered['연도'], y=factors_filtered['빙하 융해'], mode='lines', name='빙하 융해', stackgroup='one', line_color='#3B82F6'))
    fig2.add_trace(go.Scatter(x=factors_filtered['연도'], y=factors_filtered['그린란드/남극 빙상'], mode='lines', name='빙상 융해', stackgroup='one', line_color='#10B981'))
    fig2.update_layout(title='해수면 상승 기여 요인 분석', height=500, template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("자료 출처: [IPCC AR6 보고서](https://www.ipcc.ch/report/ar6/wg1/)의 기여도 분석을 기반으로 생성된 가상 데이터")
    st.markdown("---")

    st.header("3. 어느 지역이 더 위험한가?")
    st.markdown("해수면 상승은 전 지구적 현상이지만, 지역에 따라 그 속도와 영향은 다르게 나타납니다. 아래 지도는 국가별 연평균 해수면 상승률을 보여주며, 색이 진할수록 상승 속도가 빠르다는 의미입니다. (회색으로 표시된 국가는 해당 데이터셋에 포함되지 않은 지역입니다.)")
    map_selected_year = st.slider('지도 데이터 연도 선택', min_value=int(map_df['연도'].min()), max_value=int(map_df['연도'].max()), value=int(map_df['연도'].max()))
    map_filtered = map_df[map_df['연도'] == map_selected_year]
    fig_map = px.choropleth(map_filtered, locations="country_iso", color="rise_rate_mm_year", hover_name="country_iso", color_continuous_scale=px.colors.sequential.Blues, title=f"{map_selected_year}년 국가별 연평균 해수면 상승률 (mm/년)", range_color=(2, 8))
    fig_map.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("자료 출처: [NOAA, Regional Sea Level Rise](https://tidesandcurrents.noaa.gov/sltrends/sltrends.html) 데이터를 기반으로 생성된 가상 데이터")
    st.markdown("---")
    
    st.header("4. 온실가스: 위기의 근본 원인")
    st.markdown("해수면 상승을 가속하는 가장 근본적인 원인은 대기 중 온실가스 농도 증가입니다. 아래 데이터는 전 세계 온실가스 배출량의 변화와 그 구성의 변화를 보여줍니다. (데이터는 5년 단위로 제공됩니다.)")
    ghg_year_range = st.slider('온실가스 데이터 분석 기간 선택', min_value=int(ghg_df['연도'].min()), max_value=int(ghg_df['연도'].max()), value=(int(ghg_df['연도'].min()), int(ghg_df['연도'].max())))
    ghg_filtered = ghg_df[(ghg_df['연도'] >= ghg_year_range[0]) & (ghg_df['연도'] <= ghg_year_range[1])]
    st.subheader("전 세계 총 온실가스 배출량 추이")
    fig_ghg_total = px.line(ghg_filtered, x='연도', y='총 배출량(백만 톤 CO2eq)', markers=True)
    fig_ghg_total.update_layout(template='plotly_white')
    st.plotly_chart(fig_ghg_total, use_container_width=True)
    st.subheader("온실가스 종류별 구성 비율 변화")
    ghg_melted = ghg_filtered.melt(id_vars='연도', value_vars=['CO2 비율(%)', 'CH4 비율(%)', 'N2O 비율(%)', '기타 가스 비율(%)'], var_name='가스 종류', value_name='비율(%)')
    fig_ghg_composition = px.area(ghg_melted, x='연도', y='비율(%)', color='가스 종류', title='연도별 온실가스 구성 비율', markers=True)
    fig_ghg_composition.update_layout(template='plotly_white')
    st.plotly_chart(fig_ghg_composition, use_container_width=True)
    st.caption("출처: [온실가스종합정보센터](https://www.gir.go.kr/home/index.do?menuId=36), [KOSIS 국가통계포털](https://www.index.go.kr/unify/idx-info.do?idxCd=4288), [탄소중립정보포털](https://www.gihoo.or.kr/gallery.es?mid=a30202000000&bid=0010&act=view&list_no=552)")

with tab2:
    st.markdown("<h3>대한민국 어획량 변화 지도</h3>", unsafe_allow_html=True)
    if korea_geojson:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("""
                **서론**

                최근 30년간 한국 연안의 해수면은 꾸준히 상승해왔습니다. 
                이는 우리 밥상에 오르는 수산물의 양과 종류에 직접적인 영향을 미치고 있습니다.

                아래 슬라이더를 움직여 연도에 따라 각 지역의 어획량이 어떻게 변하는지 확인해보세요. 
                시간이 지날수록 해안 지역의 색이 점차 옅어지는 것을 통해 어획량 감소 추세를 시각적으로 파악할 수 있습니다.
                """)
                map_year_kr = st.slider('**지도 연도 선택 (대한민국):**', 
                                    min_value=int(regional_fishery_df['연도'].min()), 
                                    max_value=int(regional_fishery_df['연도'].max()), 
                                    value=int(regional_fishery_df['연도'].max()), 
                                    step=2,
                                    key="slider_kr")
            
            with col2:
                map_data_kr = regional_fishery_df[regional_fishery_df['연도'] == map_year_kr]
                min_catch = regional_fishery_df['어획량_톤'].min()
                max_catch = regional_fishery_df['어획량_톤'].max()

                fig_map_kr = px.choropleth(map_data_kr, geojson=korea_geojson, locations='지역',
                                        featureidkey="properties.name", color='어획량_톤',
                                        color_continuous_scale="Blues_r", 
                                        hover_name='지역',
                                        labels={'어획량_톤': '어획량(톤)'}, 
                                        range_color=[min_catch, max_catch])
                
                fig_map_kr.update_geos(fitbounds="locations", visible=False)
                fig_map_kr.update_layout(title_text=f'<b>{map_year_kr}년 지역별 어획량</b>', title_x=0.5, margin={"r":0,"t":40,"l":0,"b":0})
                st.plotly_chart(fig_map_kr, use_container_width=True)
        st.caption("※ 이 표는 흐름과 경향성을 보여주는 예시로, 시도별 연근해 어획량이 꾸준히 감소하고 있음을 시각적으로 정리한 것입니다.\n\n출처: 해양수산부 통계시스템, 2024년 어업생산동향조사 결과(잠정), 해양수산부 일반해면어업생산량현황(품종별) 공공데이터 기반")
    else:
        st.warning("대한민국 지도 데이터를 불러오는 데 실패했습니다.")

with tab3:
    st.header("점점 오염되는 우리 바다")
    st.markdown("해수면 상승뿐만 아니라, 인간이 버린 쓰레기는 바다를 병들게 하는 또 다른 주범입니다. 특히 플라스틱은 해양 생태계를 직접적으로 파괴하며, 결국 우리 식탁의 안전까지 위협합니다.")
    st.subheader("국내 연도별 해양쓰레기 수거량 변화")
    debris_melted = debris_df.melt(id_vars='연도', var_name='쓰레기 종류', value_name='발생량 (톤)')
    fig_debris = px.line(debris_melted, x='연도', y='발생량 (톤)', color='쓰레기 종류', markers=True)
    fig_debris.update_layout(template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_debris, use_container_width=True)
    st.caption("출처: [국회 농림축산식품해양수산위 자료](https://futurechosun.com/archives/77470), [광주NBN뉴스](https://gj.newdaily.co.kr/site/data/html/2024/10/07/2024100700075.html), [뉴시스](https://www.newsis.com/view/NISX20241006_0002909956)")
    
    st.subheader("해양 쓰레기 중 플라스틱이 차지하는 비율")
    fig_plastic = px.bar(plastic_df, x='연도', y='플라스틱 비율 (%)', text='플라스틱 비율 (%)')
    fig_plastic.update_traces(textposition='outside', marker_color='#DC2626')
    fig_plastic.update_layout(yaxis_range=[0,110], template='plotly_white')
    st.plotly_chart(fig_plastic, use_container_width=True)
    st.caption("출처: [국회입법조사처](https://argos.nanet.go.kr/lawstat/arc/attach/145987?view=1)")
    st.markdown("---")

    st.header("수온 상승과 어획량의 변화: 식탁 위 지각변동")
    st.markdown("해수면 상승과 함께 찾아온 바닷물 온도 상승은 어종의 서식지를 바꾸고 있습니다. 비교적 찬 바다에 살던 살오징어, 굴, 미역 등은 점차 자취를 감추고, 따뜻한 바다를 선호하는 멸치, 갈치 등은 일시적으로 생산량이 늘기도 합니다. 이는 우리 식탁에 오르는 수산물의 종류가 바뀌는 '식탁 위 지각변동'을 의미합니다.")
    
    st.subheader("주요 어종 어획량 변화")
    fish_melted = fish_production_df.melt(id_vars='연도', var_name='어종', value_name='생산량 (톤)')
    fig_fish = px.line(fish_melted, x='연도', y='생산량 (톤)', color='어종', markers=True)
    fig_fish.update_layout(template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_fish, use_container_width=True)
    st.caption("출처: 2024년 어업생산동향조사(통계청, 해양수산부), 국가통계포털")

    st.subheader("주요 양식 품목 생산량 변화")
    aquaculture_melted = aquaculture_df.melt(id_vars='연도', var_name='품목', value_name='생산량 (톤)')
    fig_aqua = px.line(
        aquaculture_melted, 
        x='연도', 
        y='생산량 (톤)', 
        color='품목', 
        markers=True,
        facet_row='품목',
        height=800
    )
    fig_aqua.update_yaxes(matches=None, showticklabels=True)
    fig_aqua.update_layout(template='plotly_white', showlegend=False)
    st.plotly_chart(fig_aqua, use_container_width=True)
    st.caption("출처: 한국해양수산개발원(KMI), 국가통계포털 어업생산동향조사 자료 재구성")
    st.markdown("---")
    
    st.header("해양 환경 악화가 초래한 식탁의 변화")
    st.markdown("이러한 생산량 변화와 해양 오염에 대한 우려는 결국 우리의 영양 섭취 불균형으로 이어질 수 있습니다. 특히 청소년기에 필수적인 영양소의 섭취가 줄어드는 것은 장기적인 건강 문제로 이어질 수 있습니다.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        nutrition_melted = nutrition_df.melt(id_vars='연도', var_name='영양소', value_name='섭취지수(%)')
        fig_nutrition = px.line(nutrition_melted, x='연도', y='섭취지수(%)', color='영양소', markers=True, title='청소년 주요 영양소 섭취 지수 변화')
        fig_nutrition.update_layout(yaxis_range=[70, 105], template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_nutrition, use_container_width=True)
    with col2:
        st.warning("주요 영양소의 역할")
        st.markdown("""- **🐟 오메가-3:** 뇌 기능 발달, 심혈관 질환 예방\n- **🥛 칼슘:** 뼈와 치아 건강의 핵심\n- **🥩 철분:** 혈액 생성과 빈혈 예방""")
        st.info("물론 청소년의 영양 섭취 변화는 단일 원인으로 설명하기 어렵습니다. 특히 코로나19 이후 초가공식품 및 패스트푸드 섭취가 늘어나는 등 전반적인 식생활 패턴의 변화가 큰 영향을 미친다는 분석이 많습니다. 하지만 해양 환경 악화가 수산물 공급 감소와 소비 기피로 이어져 영양 불균형을 심화시키는 **중요한 요인 중 하나**라는 점은 분명합니다.")

    st.caption("※ 위 표에 사용된 섭취지수(%)는 권장량 대비 섭취 경향을 단순화한 지표입니다. (자료 출처: 청소년건강행태온라인조사, 국민건강영양조사 등 재구성)")
    st.dataframe(nutrition_df, use_container_width=True)

with tab4:
    st.header("미래 시뮬레이션: 도시의 운명과 2100년의 갈림길")
    st.markdown("해수면이 상승할 때 주요 해안 도시들은 어떤 위험에 처하게 될까요? 슬라이더를 조절하여 미래의 침수 시나리오와 우리의 선택이 만들어낼 2100년의 모습을 확인해보세요.")

    rise_level_m = st.slider("미래 해수면 상승 높이 선택 (단위: m)", 0.5, 2.0, 1.0, 0.1)

    city_scenarios = {
        "인천 (대한민국)": {"img": "/workspaces/gdp-dashboard-5/incheon.png", "base_pop": 800000, "base_econ": "공항/항만 기능"},
        "뉴욕 (미국)": {"img": "/workspaces/gdp-dashboard-5/newyork.png", "base_pop": 2000000, "base_econ": "세계 금융 중심지"},
        "상하이 (중국)": {"img": "/workspaces/gdp-dashboard-5/shanghai.png", "base_pop": 17500000, "base_econ": "글로벌 물류 허브"},
        "암스테르담 (네덜란드)": {"img": "/workspaces/gdp-dashboard-5/amsterdam.png", "base_pop": 1200000, "base_econ": "기존 방재 시스템"},
        "도쿄 (일본)": {"img": "/workspaces/gdp-dashboard-5/tokyo.png", "base_pop": 1500000, "base_econ": "수도 기능 및 경제 중심지"}
    }
    selected_city = st.selectbox("확인하고 싶은 도시를 선택하세요:", list(city_scenarios.keys()))
    city_info = city_scenarios[selected_city]
    
    st.image(city_info["img"], caption=f"{selected_city} {rise_level_m}m 상승 시 침수 예상 시나리오 (가상 이미지)")
    
    impact_pop = int(city_info["base_pop"] * (rise_level_m / 1.0))
    col1, col2 = st.columns(2)
    with col1:
        st.warning(f"예상 영향 인구 ({rise_level_m}m 상승 시)")
        st.subheader(f"약 {impact_pop:,} 명")
    with col2:
        st.error("주요 경제적 타격")
        st.subheader(f"{city_info['base_econ']} 마비/붕괴 위험")
    st.markdown("---")

    st.subheader("2100년의 갈림길: 우리가 만드는 미래")
    future_years = np.arange(2025, 2101)
    current_level = gmsl_df['해수면 높이 (mm)'].iloc[-1]
    high_carbon_rise = 0.001 * (future_years - 2024)**2.2 + 4.5 * (future_years - 2024)
    low_carbon_rise = 0.0005 * (future_years - 2024)**2 + 2.8 * (future_years - 2024)
    projection_df = pd.DataFrame({'연도': np.concatenate([future_years, future_years]), '상승량 (mm)': np.concatenate([current_level + high_carbon_rise, current_level + low_carbon_rise]), '시나리오': ['현재 추세 유지 (고탄소)'] * len(future_years) + ['적극적 감축 (저탄소)'] * len(future_years)})
    
    fig5 = px.line(projection_df, x='연도', y='상승량 (mm)', color='시나리오', title='2100년 해수면 상승 예측 시나리오', labels={'상승량 (mm)': '2020년 기준 해수면 높이 (mm)'}, color_discrete_map={'현재 추세 유지 (고탄소)': '#D32F2F', '적극적 감축 (저탄소)': '#1976D2'})
    fig5.update_layout(template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig5, use_container_width=True)

    st.success("**결론:** 데이터는 명확한 사실을 보여줍니다. 우리의 행동은 미래를 바꿀 수 있는 유일한 변수입니다. 적극적인 탄소 감축 시나리오는 해수면 상승 속도를 늦춰 해안 도시를 보호하고, 나아가 해양 생태계와 우리의 건강한 식탁을 지키는 길입니다. 이 대시보드가 그 변화를 위한 작은 시작점이 되기를 바랍니다.")

with tab5:
    subtab1, subtab2 = st.tabs(["🏛️ 시장 시뮬레이션", "🃏 환경 정책 카드 게임"])

    with subtab1:
        st.header("🌊 해수면 상승 & 바다오염 시뮬레이션")
        st.write("당신은 해안 도시의 시장입니다. 도시를 지켜내고, 바다를 보호하세요!")

        if "mayor_stage" not in st.session_state:
            st.session_state.mayor_stage = 0
            st.session_state.mayor_score = 50

        scenarios = [
            {"text": "해수면이 10cm 상승했습니다. 주민들이 불안해합니다. 무엇을 하시겠습니까?", "options": {"방파제 건설 (예산 감소, 안정 ↑)": 10, "예산 절약 (주민 불만 ↑)": -15}},
            {"text": "바닷속에서 미세플라스틱이 발견되었습니다. 대응책은?", "options": {"플라스틱 규제 정책 시행 (환경 개선 ↑)": 20, "무시 (환경 악화 ↓)": -20}},
            {"text": "해변에 쓰레기가 쌓였습니다. 처리 방법을 선택하세요.", "options": {"대규모 정화 활동 (지속가능 지수 ↑)": 15, "그냥 둔다 (관광객 감소 ↓)": -10}},
            {"text": "도시 근처 공장에서 화학물질이 바다로 흘러 들어가고 있습니다.", "options": {"엄격한 환경 규제 시행 (환경 ↑, 예산 ↓)": 15, "규제 완화 (경제 유지, 환경 악화 ↓)": -15}},
            {"text": "해안가의 산호초가 백화되고 있습니다. 조치를 선택하세요.", "options": {"산호 복원 프로젝트 지원 (환경 ↑, 예산 ↓)": 20, "무시 (관광객 감소 ↓)": -10}},
            {"text": "도시의 바닷가에 오염된 어류가 발견되었습니다. 어떻게 대응하시겠습니까?", "options": {"어류 회수 및 청소 (환경 개선 ↑)": 15, "그냥 판매 허용 (경제 유지, 환경 악화 ↓)": -15}},
            {"text": "전세계적으로 기후 변화로 폭풍과 홍수가 잦아지고 있습니다.", "options": {"재해 대비 방재 시스템 구축 (주민 안전 ↑)": 20, "대책 없음 (주민 피해 ↑)": -20}}
        ]

        if st.session_state.mayor_stage < len(scenarios):
            sc = scenarios[st.session_state.mayor_stage]
            st.subheader(sc["text"])
            for option, score_change in sc["options"].items():
                if st.button(option, key=f"mayor_option_{st.session_state.mayor_stage}_{option}"):
                    st.session_state.mayor_score += score_change
                    st.session_state.mayor_stage += 1
                    st.rerun()
        else:
            st.subheader("📊 최종 결과")
            st.write(f"당신의 지속가능 지수는 **{st.session_state.mayor_score}점** 입니다.")
            if st.session_state.mayor_score >= 90:
                st.success("🌟 훌륭합니다! 도시는 안전하고 해양 환경이 잘 보존되었습니다.")
            elif st.session_state.mayor_score >= 70:
                st.success("🙂 도시는 대체로 안정적이며 환경도 어느 정도 보호되었습니다.")
            elif st.session_state.mayor_score >= 50:
                st.warning("😐 도시가 간신히 버티고 있습니다. 더 많은 노력이 필요합니다.")
            else:
                st.error("💀 도시가 해수면 상승과 환경오염에 무너졌습니다...")

            if st.button("🔄 다시 시작", key="mayor_restart"):
                st.session_state.mayor_stage = 0
                st.session_state.mayor_score = 50
                st.rerun()

    with subtab2:
        st.header("🃏 환경 정책 카드 게임")
        st.write("카드를 뽑아 도시의 환경 점수를 관리하세요!\n정책 카드와 자연/재난 카드가 랜덤으로 등장합니다.")

        if "card_game_cards" not in st.session_state:
            st.session_state.card_game_cards = [
                ("🌱 재활용 캠페인", 10, "정책"), ("🚯 해변 청소", 15, "정책"), ("🏭 규제 완화", -10, "정책"),
                ("🛑 플라스틱 금지", 20, "정책"), ("💸 환경 예산 삭감", -20, "정책"), ("🌳 해양 보호 구역 지정", 25, "정책"),
                ("🌊 폭풍 해일 발생", -15, "재난"), ("🔥 해양 산불 발생", -20, "재난"), ("🐟 해양 생물 번식 성공", 20, "자연"),
                ("🦀 산호초 회복", 15, "자연"), ("⚡ 태풍 피해", -25, "재난"), ("☀️ 강수량 증가로 수질 개선", 10, "자연"),
            ]
            st.session_state.card_game_score = 50
            st.session_state.card_game_turns = 0
            st.session_state.card_game_history = []
        
        if st.session_state.card_game_turns < 7:
            if st.button("🃏 카드 뽑기"):
                card, effect, category = random.choice(st.session_state.card_game_cards)
                st.session_state.card_game_score += effect
                st.session_state.card_game_turns += 1
                st.session_state.card_game_history.append(f"{st.session_state.card_game_turns}턴: {category} 카드 - {card} ({effect:+})")
                if effect > 0:
                    st.success(f"✅ {card} ({category} 카드) 뽑음! 점수 {effect:+}")
                else:
                    st.error(f"⚠️ {card} ({category} 카드) 뽑음! 점수 {effect:+}")
                st.rerun()
        
        st.metric("환경 점수", st.session_state.card_game_score)
        st.write(f"🔹 뽑은 카드 수: {st.session_state.card_game_turns} / 최대 7턴")

        if st.session_state.card_game_history:
            with st.expander("📜 카드 뽑은 내역 보기"):
                for h in reversed(st.session_state.card_game_history):
                    st.write(h)

        if st.session_state.card_game_turns >= 7:
            st.subheader("📊 최종 결과")
            st.write(f"최종 환경 점수: **{st.session_state.card_game_score}**")
            if st.session_state.card_game_score >= 90:
                st.success("🌟 지속가능한 도시 완성!")
            elif st.session_state.card_game_score >= 70:
                st.success("🙂 도시가 안정적이며 환경이 잘 관리되었습니다.")
            elif st.session_state.card_game_score >= 50:
                st.warning("😐 도시가 간신히 유지됩니다.")
            else:
                st.error("💀 도시가 붕괴했습니다... 환경 관리 실패!")

            if st.button("🔄 다시 시작", key="card_game_restart"):
                st.session_state.card_game_score = 50
                st.session_state.card_game_turns = 0
                st.session_state.card_game_history = []
                st.rerun()

with tab6:
    st.header("📑 종합 보고서: 요약 및 결론")
    st.markdown("### 1. 서론: 바다의 위기는 어떻게 우리 식탁의 위기가 되는가?")
    st.markdown("""
    본 대시보드는 '해수면 상승'이라는 거대한 환경 문제가 단순히 해안선 침수에서 그치지 않고, 해양 생태계 파괴, 수산물 생산량 변화를 거쳐 결국 **우리의 식생활과 건강**이라는 매우 개인적인 문제로 이어지는 연쇄적인 과정을 데이터로 추적하고 분석했습니다.
    """)

    st.markdown("### 2. 데이터 분석 요약: 위기의 연쇄 고리")
    st.markdown("""
    - **1단계 (원인): 전 지구적 위기**
        - 온실가스 배출량의 지속적인 증가는 지구 온난화를 가속하고, 이는 **해수의 열팽창**과 **빙하 융해**를 통해 전 지구적인 해수면 상승을 초래하고 있습니다.
    
    - **2단계 (중간 영향): 병들어 가는 대한민국 바다**
        - 전 지구적 변화는 대한민국 연안의 **수온 상승**을 유발했습니다. 이로 인해 한류성 어종인 **살오징어**와 양식 품목인 **굴, 미역** 등의 생산량은 뚜렷한 감소세를 보였습니다.
        - 동시에, 인간 활동으로 발생한 **해양 쓰레기**, 특히 플라스틱 오염은 해양 생태계 자체를 위협하는 심각한 요인으로 작용하고 있습니다.

    - **3단계 (최종 영향): 우리 식탁의 변화와 건강 문제**
        - 수산물의 생산량 감소와 해양 오염에 대한 우려는 자연스럽게 수산물 소비 감소로 이어졌습니다.
        - 이는 특히 성장기 청소년들에게 필수적인 **오메가-3, 칼슘, 철분**과 같은 핵심 영양소의 섭취 지수가 지속적으로 하락하는 결과로 나타났습니다. 즉, 바다의 위기는 **미래 세대의 건강 문제**로 직결되고 있습니다.
    """)
    
    st.markdown("### 3. 결론 및 시사점")
    st.markdown("""
    - **결론:** 해수면 상승과 해양 오염은 먼바다의 이야기가 아닌, **우리의 식량 안보와 건강을 직접적으로 위협하는 현실적인 문제**입니다. 데이터는 이 모든 과정이 어떻게 연결되어 있는지를 명확하게 보여줍니다.
    - **미래 전망:** 현재의 고탄소 배출 시나리오가 계속된다면, 미래에는 해안 도시의 침수뿐만 아니라 안정적인 수산물 공급망 붕괴와 심각한 영양 불균형 문제에 직면하게 될 것입니다.
    - **우리의 과제:** 따라서 탄소 배출을 줄이고 해양 환경을 보호하는 것은 단순히 지구를 위한 행동을 넘어, **우리의 건강한 식탁과 미래 세대의 건강을 지키기 위한 필수적인 과제**입니다. 이 대시보드가 그 변화를 위한 작은 시작점이 되기를 바랍니다.
    """)
    
    st.markdown("### 📚 참고 자료")
    st.markdown("""
    - NASA/NOAA Sea Level Change Portal
    - IPCC AR6 보고서
    - 온실가스종합정보센터, KOSIS 국가통계포털
    - 해양수산부 통계시스템, 어업생산동향조사
    - 청소년건강행태온라인조사, 국민건강영양조사
    """)