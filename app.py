import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Witness Archive Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("corpus.csv.csv")

    if "emotion_label" in df.columns:
        df["emotion_label"] = df["emotion_label"].astype(str).str.strip()
        df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})

    if "date_published" in df.columns:
        df["date_published"] = pd.to_datetime(df["date_published"], errors="coerce")

    return df

df = load_data()

st.title("📂 Witness Archive – ICE Raids in Chicago Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

emotions = sorted(df["emotion_label"].dropna().unique()) if "emotion_label" in df else []
sources = sorted(df["source"].dropna().unique()) if "source" in df else []

selected_emotions = st.sidebar.multiselect("Emotion", emotions, default=emotions)
selected_sources = st.sidebar.multiselect("Source", sources, default=sources)

filtered = df.copy()

if selected_emotions:
    filtered = filtered[filtered["emotion_label"].isin(selected_emotions)]
if selected_sources:
    filtered = filtered[filtered["source"].isin(selected_sources)]

# Summary section
st.subheader("📊 Summary")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total records", len(filtered))

with col2:
    st.write("Emotion distribution (horizontal chart)")

    emo_counts = (
        filtered["emotion_label"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "emotion", "emotion_label": "count"})
    )

    fig = px.bar(
        emo_counts,
        x="count",
        y="emotion",
        orientation="h",
        title="Emotion distribution",
        color="emotion",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    st.plotly_chart(fig, use_container_width_
