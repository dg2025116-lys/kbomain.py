import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── 페이지 설정 ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KBO 팬 선호도 분석 대시보드",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Bebas+Neue&display=swap');

:root {
    --kbo-navy:   #003087;
    --kbo-blue:   #005BAC;
    --kbo-sky:    #0099D8;
    --kbo-gold:   #FFB81C;
    --kbo-white:  #F5F8FF;
    --card-bg:    #FFFFFF;
    --text-main:  #0A1628;
    --text-sub:   #4A6080;
    --border:     #D0DCEE;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--kbo-white);
    color: var(--text-main);
}

/* 헤더 배너 */
.kbo-header {
    background: linear-gradient(135deg, #003087 0%, #005BAC 60%, #0099D8 100%);
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,48,135,0.28);
}
.kbo-header::before {
    content: "⚾";
    position: absolute;
    right: 40px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 120px;
    opacity: 0.08;
    line-height: 1;
}
.kbo-header h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #FFFFFF;
    letter-spacing: 3px;
    margin: 0 0 6px;
}
.kbo-header p {
    color: rgba(255,255,255,0.80);
    font-size: 0.95rem;
    margin: 0;
}
.kbo-badge {
    display: inline-block;
    background: var(--kbo-gold);
    color: #003087;
    font-weight: 700;
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

/* KPI 카드 */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: var(--card-bg);
    border-radius: 14px;
    padding: 22px 20px 18px;
    border-top: 4px solid var(--kbo-blue);
    box-shadow: 0 2px 12px rgba(0,91,172,0.10);
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-card .kpi-label {
    font-size: 0.78rem;
    color: var(--text-sub);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.kpi-card .kpi-value {
    font-size: 2rem;
    font-weight: 900;
    color: var(--kbo-navy);
    line-height: 1;
}
.kpi-card .kpi-delta {
    font-size: 0.80rem;
    color: #1DA462;
    font-weight: 700;
    margin-top: 4px;
}

/* 섹션 타이틀 */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--kbo-navy);
    border-left: 4px solid var(--kbo-gold);
    padding-left: 12px;
    margin: 28px 0 14px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003087 0%, #005BAC 100%);
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Plotly 차트 카드 */
.chart-card {
    background: var(--card-bg);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,48,135,0.08);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 데이터 생성
# ══════════════════════════════════════════════════════════════════════════════
np.random.seed(42)

TEAMS = {
    "서울 블루제이스":   {"color": "#003087", "region": "서울",  "stadium": "블루 파크"},
    "부산 타이거즈":     {"color": "#C8102E", "region": "부산",  "stadium": "남항 돔"},
    "인천 이글스":       {"color": "#00703C", "region": "인천",  "stadium": "송도 필드"},
    "대구 파이어버즈":   {"color": "#FF6B00", "region": "대구",  "stadium": "수성 아레나"},
    "광주 다이아몬즈":   {"color": "#7B2D8B", "region": "광주",  "stadium": "무등 스타디움"},
    "대전 블랙홀즈":     {"color": "#1D1D1D", "region": "대전",  "stadium": "한빛 구장"},
    "수원 로켓츠":       {"color": "#005BAC", "region": "수원",  "stadium": "팔달 파크"},
    "창원 씨호스":       {"color": "#00A9CE", "region": "창원",  "stadium": "마산 베이"},
    "전주 피닉스":       {"color": "#E4B429", "region": "전주",  "stadium": "완산 그라운드"},
    "제주 스톰":         {"color": "#2E7D32", "region": "제주",  "stadium": "한라 필드"},
}
TEAM_NAMES  = list(TEAMS.keys())
TEAM_COLORS = [TEAMS[t]["color"] for t in TEAM_NAMES]
YEARS       = list(range(2015, 2025))
REGIONS     = ["서울/경기", "부산/경남", "대구/경북", "광주/전라", "대전/충청", "강원", "제주"]
AGE_GROUPS  = ["10대", "20대", "30대", "40대", "50대 이상"]
GENDERS     = ["남성", "여성"]

# 1) 팀별 전국 선호도 (%)
base_popularity = np.array([22, 18, 12, 10, 8, 7, 7, 6, 5, 5], dtype=float)
team_popularity  = pd.DataFrame({
    "team":       TEAM_NAMES,
    "popularity": base_popularity,
    "color":      TEAM_COLORS,
    "region":     [TEAMS[t]["region"] for t in TEAM_NAMES],
    "stadium":    [TEAMS[t]["stadium"] for t in TEAM_NAMES],
    "fans_est":   (base_popularity / 100 * 51_000_000).astype(int),
})

# 2) 연도별 팀 선호도 추이
year_data = []
for team in TEAM_NAMES:
    base = team_popularity.loc[team_popularity.team == team, "popularity"].values[0]
    trend = np.cumsum(np.random.normal(0, 0.5, len(YEARS)))
    vals  = np.clip(base + trend, 1, 35)
    for y, v in zip(YEARS, vals):
        year_data.append({"year": y, "team": team, "popularity": round(v, 2),
                          "color": TEAMS[team]["color"]})
df_year = pd.DataFrame(year_data)

# 3) 지역별 선호도 히트맵
region_pref = {}
for team in TEAM_NAMES:
    home = TEAMS[team]["region"]
    prefs = np.random.dirichlet(np.ones(len(REGIONS)) * 0.5) * 100
    # 연고지 보정
    home_idx = 0
    for i, r in enumerate(REGIONS):
        if home in r or r.split("/")[0] == home:
            home_idx = i
            break
    prefs[home_idx] = prefs[home_idx] * 3
    prefs = prefs / prefs.sum() * 100
    region_pref[team] = prefs
df_region = pd.DataFrame(region_pref, index=REGIONS).T.reset_index()
df_region.columns = ["team"] + REGIONS

# 4) 연령대별 선호도
age_data = []
for team in TEAM_NAMES:
    vals = np.random.dirichlet(np.ones(len(AGE_GROUPS)) + np.random.rand(len(AGE_GROUPS))) * 100
    for age, v in zip(AGE_GROUPS, vals):
        age_data.append({"team": team, "age": age, "pct": round(v, 2), "color": TEAMS[team]["color"]})
df_age = pd.DataFrame(age_data)

# 5) 성별 선호도
gender_data = []
for team in TEAM_NAMES:
    male_pct = np.random.uniform(48, 72)
    gender_data.append({"team": team, "gender": "남성", "pct": round(male_pct, 1), "color": TEAMS[team]["color"]})
    gender_data.append({"team": team, "gender": "여성", "pct": round(100 - male_pct, 1), "color": TEAMS[team]["color"]})
df_gender = pd.DataFrame(gender_data)

# 6) 경기장 관중 수 (시즌별)
stadium_data = []
for team in TEAM_NAMES:
    cap = np.random.randint(15000, 28000)
    for y in YEARS:
        base_att = cap * np.random.uniform(0.55, 0.92)
        trend    = (y - 2015) * np.random.uniform(-200, 600)
        att      = int(np.clip(base_att + trend, cap * 0.3, cap) * 70)
        stadium_data.append({
            "team": team, "year": y, "attendance": att,
            "capacity": cap * 70, "fill_rate": round(att / (cap * 70) * 100, 1),
            "color": TEAMS[team]["color"],
        })
df_stadium = pd.DataFrame(stadium_data)

# 7) 선수 인기도 Top 20
players_raw = [
    ("김준혁", "서울 블루제이스", "투수",   95, 1988), ("박성민", "부산 타이거즈",   "외야수", 91, 1992),
    ("이재원", "서울 블루제이스", "내야수", 88, 1990), ("최동훈", "인천 이글스",     "포수",   85, 1994),
    ("정우성", "대구 파이어버즈", "투수",   83, 1991), ("강민준", "부산 타이거즈",   "내야수", 81, 1996),
    ("윤태양", "광주 다이아몬즈", "외야수", 79, 1993), ("한지수", "대전 블랙홀즈",   "투수",   76, 1989),
    ("오세진", "수원 로켓츠",     "내야수", 74, 1997), ("임도현", "서울 블루제이스", "외야수", 72, 1995),
    ("신현우", "창원 씨호스",     "투수",   70, 1992), ("조민혁", "전주 피닉스",     "내야수", 68, 1990),
    ("권성훈", "제주 스톰",       "외야수", 66, 1994), ("배준서", "인천 이글스",     "투수",   64, 1998),
    ("류재현", "대구 파이어버즈", "포수",   62, 1991), ("노정민", "광주 다이아몬즈", "내야수", 61, 1996),
    ("황성빈", "수원 로켓츠",     "외야수", 59, 1993), ("문태준", "대전 블랙홀즈",   "투수",   57, 1997),
    ("서동현", "창원 씨호스",     "내야수", 55, 1995), ("안재영", "전주 피닉스",     "외야수", 53, 1992),
]
df_players = pd.DataFrame(players_raw, columns=["name", "team", "position", "score", "birth"])
df_players["color"] = df_players["team"].map(lambda t: TEAMS[t]["color"])
df_players["age"]   = 2024 - df_players["birth"]

# ══════════════════════════════════════════════════════════════════════════════
# Plotly 공통 테마
# ══════════════════════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    font=dict(family="Noto Sans KR, sans-serif", color="#0A1628"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#D0DCEE", borderwidth=1),
)

def apply_theme(fig, title=""):
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=16, color="#003087")))
    fig.update_xaxes(showgrid=True,  gridcolor="#E8EFF8", zeroline=False)
    fig.update_yaxes(showgrid=True,  gridcolor="#E8EFF8", zeroline=False)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚾ 필터")
    selected_teams = st.multiselect(
        "팀 선택", TEAM_NAMES, default=TEAM_NAMES[:5],
        help="분석할 팀을 선택하세요"
    )
    selected_years = st.slider("기간", 2015, 2024, (2018, 2024))
    selected_section = st.radio(
        "섹션 이동",
        ["📊 전체 개요", "📈 연도별 추이", "🗺️ 지역·연령·성별", "🏟️ 경기장 관중", "🌟 선수 인기도"],
    )
    st.markdown("---")
    st.caption("🔵 데이터 기준: 가상 KBO 리그 (2015–2024)\n팬 선호도 설문 N=50,000")

if not selected_teams:
    st.warning("최소 1개 이상의 팀을 선택해 주세요.")
    st.stop()

# 필터 적용
df_year_f    = df_year[(df_year.team.isin(selected_teams)) & (df_year.year.between(*selected_years))]
df_stadium_f = df_stadium[(df_stadium.team.isin(selected_teams)) & (df_stadium.year.between(*selected_years))]
df_age_f     = df_age[df_age.team.isin(selected_teams)]
df_gender_f  = df_gender[df_gender.team.isin(selected_teams)]
df_region_f  = df_region[df_region.team.isin(selected_teams)]

# ══════════════════════════════════════════════════════════════════════════════
# 헤더
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="kbo-header">
  <div class="kbo-badge">⚾ OFFICIAL FAN ANALYTICS</div>
  <h1>KBO 팬 선호도 대시보드</h1>
  <p>가상 KBO 리그 10개 구단 · 팬 선호도 종합 분석 · 2015 – 2024 시즌</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 섹션 1: 전체 개요
# ══════════════════════════════════════════════════════════════════════════════
if selected_section in ["📊 전체 개요"]:
    # KPI 카드
    total_fans = team_popularity["fans_est"].sum()
    top_team   = team_popularity.iloc[0]
    avg_fill   = df_stadium_f["fill_rate"].mean()
    top_player = df_players.iloc[0]

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">전체 추정 팬 수</div>
        <div class="kpi-value">{total_fans/1_000_000:.1f}M</div>
        <div class="kpi-delta">↑ +3.2% YoY</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">1위 구단</div>
        <div class="kpi-value">{top_team['team'].split()[1]}</div>
        <div class="kpi-delta">선호도 {top_team['popularity']:.0f}%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">평균 관중 점유율</div>
        <div class="kpi-value">{avg_fill:.1f}%</div>
        <div class="kpi-delta">↑ +1.8%p YoY</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">최고 인기 선수</div>
        <div class="kpi-value">{top_player['name']}</div>
        <div class="kpi-delta">인기지수 {top_player['score']}점</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])

    with col1:
        # 팀별 선호도 가로 막대그래프
        df_pop_sorted = team_popularity.sort_values("popularity", ascending=True)
        fig = go.Figure(go.Bar(
            x=df_pop_sorted["popularity"],
            y=df_pop_sorted["team"],
            orientation="h",
            marker=dict(
                color=df_pop_sorted["color"],
                line=dict(width=0),
            ),
            text=[f"{v:.1f}%" for v in df_pop_sorted["popularity"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>선호도: %{x:.1f}%<extra></extra>",
        ))
        apply_theme(fig, "팀별 전국 팬 선호도")
        fig.update_layout(height=400, xaxis_title="선호도 (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 도넛 차트
        fig2 = go.Figure(go.Pie(
            labels=team_popularity["team"],
            values=team_popularity["popularity"],
            hole=0.52,
            marker=dict(colors=TEAM_COLORS, line=dict(color="#FFFFFF", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            textinfo="label+percent",
            textfont=dict(size=10),
        ))
        apply_theme(fig2, "팬 점유율 분포")
        fig2.update_layout(height=400, showlegend=False)
        fig2.add_annotation(text="전체<br>팬점유율", x=0.5, y=0.5, showarrow=False,
                             font=dict(size=13, color="#003087", family="Noto Sans KR"))
        st.plotly_chart(fig2, use_container_width=True)

    # 추정 팬 수 트리맵
    st.markdown('<div class="section-title">🗃️ 구단별 추정 팬 수 (트리맵)</div>', unsafe_allow_html=True)
    fig3 = px.treemap(
        team_popularity,
        path=["team"], values="fans_est",
        color="fans_est",
        color_continuous_scale=["#BDD7EE", "#003087"],
        hover_data={"fans_est": ":,", "popularity": ":.1f"},
        custom_data=["region", "stadium"],
    )
    fig3.update_traces(
        hovertemplate="<b>%{label}</b><br>추정 팬 수: %{value:,}명<extra></extra>",
        textfont=dict(size=14),
    )
    apply_theme(fig3, "")
    fig3.update_layout(height=320, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 섹션 2: 연도별 추이
# ══════════════════════════════════════════════════════════════════════════════
elif selected_section == "📈 연도별 추이":
    st.markdown('<div class="section-title">📈 연도별 팀 선호도 추이</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for team in selected_teams:
        d = df_year_f[df_year_f.team == team]
        fig.add_trace(go.Scatter(
            x=d["year"], y=d["popularity"],
            mode="lines+markers",
            name=team,
            line=dict(color=TEAMS[team]["color"], width=2.5),
            marker=dict(size=7, color=TEAMS[team]["color"]),
            hovertemplate=f"<b>{team}</b><br>%{{x}}년: %{{y:.2f}}%<extra></extra>",
        ))
    apply_theme(fig, "시즌별 팬 선호도 변화")
    fig.update_layout(height=420, xaxis_title="시즌", yaxis_title="선호도 (%)",
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # 연도별 스택 영역 차트
    st.markdown('<div class="section-title">📊 연도별 팬 점유 비중 (스택 영역)</div>', unsafe_allow_html=True)
    pivot = df_year_f.pivot_table(index="year", columns="team", values="popularity").fillna(0)
    pivot_norm = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig2 = go.Figure()
    for team in pivot_norm.columns:
        fig2.add_trace(go.Scatter(
            x=pivot_norm.index, y=pivot_norm[team],
            name=team,
            stackgroup="one",
            fillcolor=TEAMS[team]["color"] + "CC",
            line=dict(color=TEAMS[team]["color"], width=0.5),
            hovertemplate=f"<b>{team}</b><br>%{{x}}년: %{{y:.1f}}%<extra></extra>",
        ))
    apply_theme(fig2, "")
    fig2.update_layout(height=380, xaxis_title="시즌", yaxis_title="점유 비중 (%)")
    st.plotly_chart(fig2, use_container_width=True)

    # 연평균 성장률 (CAGR) 막대
    st.markdown('<div class="section-title">📉 팀별 선호도 연평균 증감률 (2015→2024)</div>', unsafe_allow_html=True)
    cagr_data = []
    for team in selected_teams:
        d = df_year[df_year.team == team]
        v0 = d[d.year == 2015]["popularity"].values[0]
        v1 = d[d.year == 2024]["popularity"].values[0]
        cagr = ((v1 / v0) ** (1/9) - 1) * 100
        cagr_data.append({"team": team, "cagr": round(cagr, 2), "color": TEAMS[team]["color"]})
    df_cagr = pd.DataFrame(cagr_data).sort_values("cagr", ascending=False)

    colors_cagr = [TEAMS[t]["color"] if v >= 0 else "#C8102E"
                   for t, v in zip(df_cagr["team"], df_cagr["cagr"])]
    fig3 = go.Figure(go.Bar(
        x=df_cagr["team"], y=df_cagr["cagr"],
        marker_color=colors_cagr,
        text=[f"{v:+.2f}%" for v in df_cagr["cagr"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>CAGR: %{y:+.2f}%<extra></extra>",
    ))
    apply_theme(fig3, "")
    fig3.update_layout(height=360, yaxis_title="연평균 증감률 (%)")
    fig3.add_hline(y=0, line_dash="dash", line_color="#888", line_width=1)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 섹션 3: 지역·연령·성별
# ══════════════════════════════════════════════════════════════════════════════
elif selected_section == "🗺️ 지역·연령·성별":
    st.markdown('<div class="section-title">🗺️ 지역별 팬 분포 히트맵</div>', unsafe_allow_html=True)
    heat_data = df_region_f.set_index("team")[REGIONS]
    fig = px.imshow(
        heat_data,
        color_continuous_scale=["#EBF3FF", "#003087"],
        aspect="auto",
        text_auto=".1f",
        labels=dict(x="지역", y="구단", color="비중(%)"),
    )
    apply_theme(fig, "")
    fig.update_layout(height=420, coloraxis_showscale=True)
    fig.update_traces(textfont=dict(size=11))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">👥 연령대별 팬 비중</div>', unsafe_allow_html=True)
        pivot_age = df_age_f.pivot_table(index="team", columns="age", values="pct").fillna(0)
        fig2 = go.Figure()
        palette_age = ["#BDD7EE", "#70ACD4", "#2E75B6", "#003087", "#00152E"]
        for i, age in enumerate(AGE_GROUPS):
            if age in pivot_age.columns:
                fig2.add_trace(go.Bar(
                    name=age, x=pivot_age.index, y=pivot_age[age],
                    marker_color=palette_age[i],
                    hovertemplate=f"<b>%{{x}}</b><br>{age}: %{{y:.1f}}%<extra></extra>",
                ))
        apply_theme(fig2, "")
        fig2.update_layout(barmode="stack", height=420,
                           xaxis_tickangle=-30, yaxis_title="비중 (%)")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">⚤ 성별 팬 비율</div>', unsafe_allow_html=True)
        df_m = df_gender_f[df_gender_f.gender == "남성"].sort_values("pct", ascending=True)
        df_f = df_gender_f[df_gender_f.gender == "여성"]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="남성", x=df_m["pct"], y=df_m["team"],
            orientation="h", marker_color="#003087",
            hovertemplate="<b>%{y}</b><br>남성: %{x:.1f}%<extra></extra>",
        ))
        fig3.add_trace(go.Bar(
            name="여성",
            x=[df_f[df_f.team == t]["pct"].values[0] for t in df_m["team"]],
            y=df_m["team"],
            orientation="h", marker_color="#E8A0BF",
            hovertemplate="<b>%{y}</b><br>여성: %{x:.1f}%<extra></extra>",
        ))
        apply_theme(fig3, "")
        fig3.update_layout(barmode="stack", height=420, xaxis_title="비율 (%)")
        st.plotly_chart(fig3, use_container_width=True)

    # 레이더 차트 (연령대)
    st.markdown('<div class="section-title">🕸️ 팀별 연령대 팬 분포 레이더</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    for team in selected_teams[:6]:
        d = df_age_f[df_age_f.team == team]
        vals = [d[d.age == a]["pct"].values[0] if len(d[d.age == a]) else 0 for a in AGE_GROUPS]
        vals_closed = vals + [vals[0]]
        angles_closed = AGE_GROUPS + [AGE_GROUPS[0]]
        fig4.add_trace(go.Scatterpolar(
            r=vals_closed, theta=angles_closed,
            name=team, fill="toself",
            fillcolor=TEAMS[team]["color"] + "33",
            line=dict(color=TEAMS[team]["color"], width=2),
        ))
    apply_theme(fig4, "")
    fig4.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 50], gridcolor="#D0DCEE"),
                   angularaxis=dict(gridcolor="#D0DCEE")),
        height=420,
    )
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 섹션 4: 경기장 관중
# ══════════════════════════════════════════════════════════════════════════════
elif selected_section == "🏟️ 경기장 관중":
    st.markdown('<div class="section-title">🏟️ 시즌별 경기장 관중 수 추이</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for team in selected_teams:
        d = df_stadium_f[df_stadium_f.team == team]
        fig.add_trace(go.Bar(
            x=d["year"], y=d["attendance"],
            name=team,
            marker_color=TEAMS[team]["color"],
            hovertemplate=f"<b>{team}</b><br>%{{x}}년: %{{y:,}}명<extra></extra>",
        ))
    apply_theme(fig, "시즌별 홈 경기 총 관중 수")
    fig.update_layout(barmode="group", height=420,
                      xaxis_title="시즌", yaxis_title="관중 수 (명)")
    st.plotly_chart(fig, use_container_width=True)

    # 점유율 라인
    st.markdown('<div class="section-title">📊 경기장 점유율 (%)</div>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for team in selected_teams:
        d = df_stadium_f[df_stadium_f.team == team]
        fig2.add_trace(go.Scatter(
            x=d["year"], y=d["fill_rate"],
            name=team,
            mode="lines+markers",
            line=dict(color=TEAMS[team]["color"], width=2.5),
            marker=dict(size=7),
            hovertemplate=f"<b>{team}</b><br>%{{x}}년: %{{y:.1f}}%<extra></extra>",
        ))
    apply_theme(fig2, "")
    fig2.update_layout(height=380, xaxis_title="시즌", yaxis_title="점유율 (%)",
                       hovermode="x unified")
    fig2.add_hline(y=80, line_dash="dot", line_color="#FFB81C",
                   annotation_text="80% 목표선", annotation_position="bottom right")
    st.plotly_chart(fig2, use_container_width=True)

    # 총 관중 합계 (버블)
    st.markdown('<div class="section-title">🔵 구단별 누적 관중 vs 선호도 (버블)</div>', unsafe_allow_html=True)
    bubble = df_stadium[df_stadium.team.isin(selected_teams)].groupby("team")["attendance"].sum().reset_index()
    bubble = bubble.merge(team_popularity[["team", "popularity", "color"]], on="team")
    bubble["avg_fill"] = df_stadium[df_stadium.team.isin(selected_teams)].groupby("team")["fill_rate"].mean().values

    fig3 = go.Figure(go.Scatter(
        x=bubble["popularity"], y=bubble["attendance"] / 1_000_000,
        mode="markers+text",
        text=bubble["team"].str.split().str[1],
        textposition="top center",
        marker=dict(
            size=bubble["avg_fill"] * 0.9,
            color=bubble["color"],
            opacity=0.85,
            line=dict(color="#FFFFFF", width=2),
        ),
        hovertemplate="<b>%{text}</b><br>선호도: %{x:.1f}%<br>누적관중: %{y:.2f}M명<extra></extra>",
    ))
    apply_theme(fig3, "팬 선호도 vs 누적 관중 수")
    fig3.update_layout(height=420, xaxis_title="선호도 (%)", yaxis_title="누적 관중 (백만 명)")
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 섹션 5: 선수 인기도
# ══════════════════════════════════════════════════════════════════════════════
elif selected_section == "🌟 선수 인기도":
    st.markdown('<div class="section-title">🌟 선수 인기도 Top 20</div>', unsafe_allow_html=True)

    df_pl_f = df_players[df_players.team.isin(selected_teams)].sort_values("score", ascending=True)

    fig = go.Figure(go.Bar(
        x=df_pl_f["score"],
        y=df_pl_f["name"] + " (" + df_pl_f["team"].str.split().str[1] + ")",
        orientation="h",
        marker=dict(
            color=df_pl_f["score"],
            colorscale=[[0, "#BDD7EE"], [1, "#003087"]],
            showscale=True,
            colorbar=dict(title="인기지수"),
        ),
        text=df_pl_f["score"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>인기지수: %{x}<extra></extra>",
    ))
    apply_theme(fig, "")
    fig.update_layout(height=max(400, len(df_pl_f) * 28), xaxis_title="인기지수 (100점 만점)")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">🥎 포지션별 평균 인기지수</div>', unsafe_allow_html=True)
        pos_avg = df_players[df_players.team.isin(selected_teams)].groupby("position")["score"].mean().reset_index()
        fig2 = px.bar(
            pos_avg, x="position", y="score",
            color="score", color_continuous_scale=["#BDD7EE", "#003087"],
            text_auto=".1f",
        )
        apply_theme(fig2, "")
        fig2.update_layout(height=360, coloraxis_showscale=False,
                            yaxis_title="평균 인기지수", xaxis_title="포지션")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">📅 연령대별 선수 분포</div>', unsafe_allow_html=True)
        fig3 = px.scatter(
            df_players[df_players.team.isin(selected_teams)],
            x="age", y="score",
            color="team",
            color_discrete_map={t: TEAMS[t]["color"] for t in TEAM_NAMES},
            symbol="position",
            size="score",
            size_max=20,
            hover_name="name",
            hover_data={"team": True, "position": True, "score": True, "age": True},
        )
        apply_theme(fig3, "")
        fig3.update_layout(height=360, xaxis_title="선수 나이", yaxis_title="인기지수")
        st.plotly_chart(fig3, use_container_width=True)

    # 팀별 스타 선수 비교
    st.markdown('<div class="section-title">🏆 팀별 최고 인기 선수 비교</div>', unsafe_allow_html=True)
    top_per_team = df_players[df_players.team.isin(selected_teams)].groupby("team").apply(
        lambda x: x.nlargest(1, "score")).reset_index(drop=True)

    fig4 = go.Figure(go.Bar(
        x=top_per_team["team"],
        y=top_per_team["score"],
        marker_color=[TEAMS[t]["color"] for t in top_per_team["team"]],
        text=[f"{row['name']}<br>{row['position']}" for _, row in top_per_team.iterrows()],
        textposition="inside",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{x}</b><br>선수: %{text}<br>인기지수: %{y}<extra></extra>",
    ))
    apply_theme(fig4, "")
    fig4.update_layout(height=380, xaxis_tickangle=-20, yaxis_title="인기지수",
                       xaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)

# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⚾ KBO 팬 선호도 분석 대시보드 | 모든 데이터는 가상 시뮬레이션 데이터입니다 | Powered by Streamlit + Plotly")
