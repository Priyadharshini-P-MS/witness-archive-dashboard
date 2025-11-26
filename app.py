import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Witness Archive Dashboard", layout="wide")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("corpus_updated.csv")
    df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})
    return df

df = load_data()

# -----------------------------
# Header
# -----------------------------
st.title("📂 Witness Archive – ICE Raids in Chicago Dashboard")
st.markdown("Emotion Labels Dashboard: displaying emotional responses to ICE-related narratives.")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

emotion_options = sorted(df["emotion_label"].dropna().unique())
selected_emotions = st.sidebar.multiselect(
    "Select Emotion",
    emotion_options,
    default=emotion_options,
)

filtered_df = df[df["emotion_label"].isin(selected_emotions)] if selected_emotions else df

# -----------------------------
# Summary Stats
# -----------------------------
st.subheader("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", len(filtered_df))

with col2:
    unique_articles = filtered_df["article_id"].nunique()
    st.metric("Unique Articles", unique_articles)

with col3:
    emo_counts = filtered_df["emotion_label"].value_counts()
    st.write("Emotion Distribution:")
    st.bar_chart(emo_counts)

# -----------------------------
# Emotion Chart
# -----------------------------
st.subheader("📈 Emotion Trends")
emo_chart = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x=alt.X("emotion_label:N", title="Emotion"),
        y=alt.Y("count():Q", title="Number of Records"),
        color="emotion_label:N"
    )
    .properties(height=400)
)
st.altair_chart(emo_chart, use_container_width=True)

# -----------------------------
# Display Full Table
# -----------------------------
st.subheader("📑 Full Dataset")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.markdown("Dashboard filtered only by emotion labels. 'Joy' has been relabeled as 'Shock'.")
