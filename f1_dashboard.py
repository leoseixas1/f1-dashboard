import streamlit as st
import fastf1
import pandas as pd
import plotly.express as px
import os

# =========================
# CONFIG GERAL
# =========================

st.set_page_config(
    page_title="Dashboard Profissional F1",
    layout="wide",
    page_icon="🏎️"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #111;
}
</style>
""", unsafe_allow_html=True)

st.title("🏎️ Dashboard Profissional de Fórmula 1")
st.markdown("Análises completas por temporada com rankings, gráficos e exportações.")

# =========================
# CACHE
# =========================

CACHE_DIR = "cache_f1_data"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

# =========================
# SIDEBAR
# =========================

st.sidebar.header("⚙️ Configurações")

season = st.sidebar.selectbox("Temporada", list(range(2018, 2025))[::-1])
round_number = st.sidebar.number_input("Rodada", 1, 23, 1)
session_type = st.sidebar.selectbox("Sessão", ["R", "Q", "FP1", "FP2", "FP3"])

# =========================
# FUNÇÃO PRINCIPAL
# =========================

@st.cache_data(show_spinner=False)
def load_session_data(season, round_number, session_type):
    session = fastf1.get_session(season, round_number, session_type)
    session.load()

    results = session.results.copy()
    results["Driver"] = results["BroadcastName"]
    results["Team"] = results["TeamName"]

    return results, session.event["EventName"]

# =========================
# EXECUÇÃO PRINCIPAL
# =========================

try:
    results_df, gp_name = load_session_data(season, round_number, session_type)

    st.subheader(f"📍 {gp_name} — Sessão: {session_type}")

    base = results_df[[
        "Position", "Driver", "Team",
        "Status", "Points", "Laps"
    ]]

    # =========================
    # KPIs
    # =========================

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏁 Total de Pilotos", len(base))
    col2.metric("🥇 Vencedor", base.iloc[0]["Driver"])
    col3.metric("🏎️ Equipe Vencedora", base.iloc[0]["Team"])
    col4.metric("🟢 Concluíram", (base["Status"] == "Finished").sum())

    # =========================
    # TABELA
    # =========================

    st.subheader("📊 Classificação Oficial")
    st.dataframe(base, use_container_width=True)

    # =========================
    # GRÁFICO DE PONTOS POR PILOTO
    # =========================

    fig1 = px.bar(
        base.sort_values("Points", ascending=False),
        x="Driver",
        y="Points",
        color="Team",
        title="🏆 Pontuação por Piloto"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # GRÁFICO DE VOLTAS
    # =========================

    fig2 = px.line(
        base,
        x="Driver",
        y="Laps",
        markers=True,
        title="🔁 Voltas Completadas"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # RANKING DE CONSTRUTORES
    # =========================

    team_rank = base.groupby("Team")["Points"].sum().reset_index().sort_values("Points", ascending=False)

    fig3 = px.bar(
        team_rank,
        x="Team",
        y="Points",
        title="🏎️ Ranking de Construtores"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # EXPORTAÇÃO CSV
    # =========================

    csv = base.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Exportar classificação em CSV",
        data=csv,
        file_name=f"f1_{season}_round_{round_number}_{session_type}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error("❌ Erro ao carregar dados da temporada. Tente outra rodada.")
    st.exception(e)