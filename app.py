import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Witness Archive – ICE Raids in Chicago",
    layout="wide"
)

# -----------------------------
# Load data (very simple)
# -----------------------------
def load_data():
    # Make sure this EXACT file exists in the repo root
    df = pd.read_csv("corpus.csv.csv")

    # Normalize emotion labels just in case
    if "emotion_label" in df.columns:
        df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})
        df["emotion_label"] = df["emotion_label"].astype(str).str.strip()

    # Parse date_published if present
    if "date_published" in df.columns:
        df["date_published"] = pd.to_datetime(
            df["date_published"], errors="coerce"
        )

    return df


df = load_data()

# -----------------------------
# Title
# -----------------------------
st.title("📂 Witness Archive – ICE Raids in Chicago Dashboard")
st.markdown("---")

# -----------------------------
# Sidebar filters (simple)
# -----------------------------
st.sidebar.header("Filters")

# Emotion filter
if "emotion_label" in df.columns:
    emo_options = sorted(df["emotion_label"].dropna().unique())
    selected_emo = st.sidebar.multiselect(
        "Emotion",
        options=emo_options,
        default=emo_options,
    )
else:
    selected_emo = []

# Source filter
if "source" in df.columns:
    src_options = sorted(df["source"].dropna().unique())
    selected_src = st.sidebar.multiselect(
        "Source",
        options=src_options,
        default=src_options,
    )
else:
    selected_src = []

# Apply filters
filtered = df.copy()

if selected_emo and "emotion_label" in filtered.columns:
    filtered = filtered[filtered["emotion_label"].isin(selected_emo)]

if selected_src and "source" in filtered.columns:
    filtered = filtered[filtered["source"].isin(selected_src)]

# -----------------------------
# Summary
# -----------------------------
st.subheader("📊 Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total records (filtered)", len(filtered))

with col2:
    if "emotion_label" in filtered.columns and not filtered.empty:
        st.write("Emotion distribution:")
        st.bar_chart(filtered["emotion_label"].value_counts())
    else:
        st.write("No emotion data.")

st.markdown("---")

# -----------------------------
# Table
# -----------------------------
st.subheader("📑 Filtered data")

show_cols = [
    "id",
    "article_id",
    "title",
    "date_published",
    "source",
    "emotion_label",
    "theme_label",
    "narrative_type",
    "text_excerpt",
    "url",
]
show_cols = [c for c in show_cols if c in filtered.columns]

st.dataframe(filtered[show_cols], use_container_width=True)

st.caption("Dashboard: Witness Archive – ICE Raids in Chicago.")
