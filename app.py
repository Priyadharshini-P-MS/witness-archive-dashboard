import streamlit as st
import pandas as pd

st.set_page_config(page_title="Witness Archive Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("corpus.csv.csv")

    # Replace joy -> shock
    if "emotion_label" in df.columns:
        df["emotion_label"] = df["emotion_label"].astype(str).str.strip()
        df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})

    # Convert date
    if "date_published" in df.columns:
        df["date_published"] = pd.to_datetime(df["date_published"], errors="coerce")

    return df

df = load_data()

# ---------- UI ----------
st.title("📂 Witness Archive – ICE Raids in Chicago Dashboard")
st.markdown("---")

# ---------- Sidebar Filters ----------
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

# ---------- Summary ----------
st.subheader("📊 Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total records", len(filtered))

with col2:
    st.write("Emotion distribution (vertical)")
    emo_counts = filtered["emotion_label"].value_counts().sort_index()
    st.bar_chart(emo_counts)

st.markdown("---")

# ---------- Data ----------
st.subheader("📑 Filtered Data")

cols = [
    "id", "article_id", "title", "date_published", "source",
    "emotion_label", "theme_label", "narrative_type",
    "text_excerpt", "url"
]
cols = [c for c in cols if c in filtered.columns]

st.dataframe(filtered[cols], use_container_width=True)

st.markdown("---")
st.caption("Dashboard: Witness Archive – ICE Raids in Chicago.")
