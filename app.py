import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Elden Ring Arsenal Analytics",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "Elden_Ring_PowerBI_Dataset_20_Columns.xlsx"

@st.cache_data
def load_data():
    data = pd.read_excel(DATA_FILE)
    # Normalize numeric columns so charts and filters remain reliable.
    for col in ["Base_Damage", "Upgrade_Level", "Weight_Kg", "Required_Strength"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

df = load_data()

st.markdown("""
<style>
    .stApp { background: #0b0d10; color: #f1f1f1; }
    [data-testid="stSidebar"] { background: #12161c; }
    div[data-testid="stMetric"] {
        background: #151a21; border: 1px solid #2a313b;
        padding: 16px; border-radius: 12px;
    }
    h1, h2, h3 { color: #e5c77b; }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ Elden Ring Arsenal Analytics")
st.caption("Explore 50,000 item records by weapon class, region, affinity, rarity, damage, and requirements.")

# Sidebar filters
st.sidebar.header("Filter the arsenal")
def multiselect_filter(label, column):
    choices = sorted(df[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, choices, default=[])

weapon_types = multiselect_filter("Weapon type", "Weapon_Type")
regions = multiselect_filter("Region found", "Region_Found")
affinities = multiselect_filter("Affinity", "Affinity")
rarities = multiselect_filter("Rarity", "Rarity")
damage_types = multiselect_filter("Primary damage type", "Primary_Damage_Type")
boss_loot = st.sidebar.multiselect(
    "Boss loot", sorted(df["Is_Boss_Loot"].dropna().astype(str).unique()),
    default=[]
)

numeric_cols = st.sidebar.columns(1)
min_damage = float(df["Base_Damage"].min())
max_damage = float(df["Base_Damage"].max())
damage_range = st.sidebar.slider(
    "Base damage range", min_value=min_damage, max_value=max_damage,
    value=(min_damage, max_damage)
)
min_upgrade = int(df["Upgrade_Level"].min())
max_upgrade = int(df["Upgrade_Level"].max())
upgrade_range = st.sidebar.slider(
    "Upgrade level", min_value=min_upgrade, max_value=max_upgrade,
    value=(min_upgrade, max_upgrade)
)

filtered = df.copy()
for column, selected in [
    ("Weapon_Type", weapon_types),
    ("Region_Found", regions),
    ("Affinity", affinities),
    ("Rarity", rarities),
    ("Primary_Damage_Type", damage_types),
    ("Is_Boss_Loot", boss_loot),
]:
    if selected:
        filtered = filtered[filtered[column].astype(str).isin(selected)]

filtered = filtered[
    filtered["Base_Damage"].between(damage_range[0], damage_range[1])
    & filtered["Upgrade_Level"].between(upgrade_range[0], upgrade_range[1])
]

# KPI row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Matching records", f"{len(filtered):,}")
c2.metric("Average base damage", f"{filtered['Base_Damage'].mean():,.1f}" if not filtered.empty else "—")
c3.metric("Average weight", f"{filtered['Weight_Kg'].mean():,.2f} kg" if not filtered.empty else "—")
c4.metric("Boss loot records", f"{(filtered['Is_Boss_Loot'].astype(str).str.lower() == 'yes').sum():,}")

if filtered.empty:
    st.warning("No records match these filters. Change or clear one or more filters.")
    st.stop()

tab_overview, tab_combat, tab_explore, tab_data = st.tabs(
    ["Overview", "Combat stats", "Explore items", "Data table"]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        type_counts = filtered["Weapon_Type"].value_counts().head(12).rename_axis("Weapon type").reset_index(name="Records")
        fig = px.bar(type_counts, x="Records", y="Weapon type", orientation="h",
                     title="Top weapon types by record count", template="plotly_dark")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        region_counts = filtered["Region_Found"].value_counts().head(12).rename_axis("Region").reset_index(name="Records")
        fig = px.bar(region_counts, x="Region", y="Records", title="Records by region (top 12)", template="plotly_dark")
        fig.update_layout(xaxis_tickangle=-35, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        rarity_counts = filtered["Rarity"].value_counts().rename_axis("Rarity").reset_index(name="Records")
        fig = px.pie(rarity_counts, names="Rarity", values="Records", hole=0.55,
                     title="Rarity distribution", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        affinity_counts = filtered["Affinity"].value_counts().head(12).rename_axis("Affinity").reset_index(name="Records")
        fig = px.bar(affinity_counts, x="Affinity", y="Records", title="Records by affinity", template="plotly_dark")
        fig.update_layout(xaxis_tickangle=-30, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)

with tab_combat:
    left, right = st.columns(2)
    with left:
        fig = px.histogram(filtered, x="Base_Damage", nbins=35, title="Base damage distribution",
                           labels={"Base_Damage": "Base damage"}, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.scatter(
            filtered.sample(min(5000, len(filtered)), random_state=7),
            x="Weight_Kg", y="Base_Damage", color="Primary_Damage_Type",
            hover_data=["Item_Name", "Weapon_Type", "Upgrade_Level"],
            title="Weight vs base damage (up to 5,000 points)", template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    damage_by_type = (filtered.groupby("Weapon_Type", dropna=False)
                      .agg(Records=("Record_ID", "count"), Avg_Damage=("Base_Damage", "mean"),
                           Max_Damage=("Base_Damage", "max"), Avg_Weight=("Weight_Kg", "mean"))
                      .reset_index().sort_values("Avg_Damage", ascending=False).head(15))
    st.subheader("Weapon type performance")
    st.dataframe(damage_by_type.round(2), use_container_width=True, hide_index=True)

with tab_explore:
    st.subheader("Find an item")
    search = st.text_input("Search item names", placeholder="Type a name or part of a name…")
    explore = filtered
    if search.strip():
        explore = explore[explore["Item_Name"].astype(str).str.contains(search.strip(), case=False, na=False)]
    st.caption(f"{len(explore):,} matching item(s)")
    show_cols = ["Item_Name", "Weapon_Type", "Weapon_Subtype", "Affinity", "Region_Found",
                 "Rarity", "Primary_Damage_Type", "Status_Effect", "Base_Damage",
                 "Upgrade_Level", "Weight_Kg", "Required_Strength", "Is_Boss_Loot"]
    st.dataframe(explore[show_cols].head(1000), use_container_width=True, hide_index=True)
    if len(explore) > 1000:
        st.info("Showing the first 1,000 matches here. Download the filtered data below to access all matching records.")

with tab_data:
    st.subheader("Filtered dataset")
    st.caption("The table is limited to the first 2,000 rows for browser performance; downloads include all filtered rows.")
    st.dataframe(filtered.head(2000), use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered records as CSV",
    data=csv,
    file_name="elden_ring_filtered_data.csv",
    mime="text/csv",
)
st.caption("Dashboard built with Streamlit and Plotly. Data source: supplied Excel workbook.")
