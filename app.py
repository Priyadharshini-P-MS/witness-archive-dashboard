import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Witness Archive – ICE Raids in Chicago",
    layout="wide"
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("corpus.csv.csv")

    # Normalize emotion labels: convert any 'joy' to 'shock'
    if "emotion_label" in df.columns:
        df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})
        df["emotion_label"] = df["emotion_label"].str.strip()

    # Parse date_published as datetime if present
    if "date_published" in df.columns:
        df["date_published"] = pd.to_datetime(
            df["date_published"], errors="coerce"
        )

    return df


df = load_data()

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("📂 Witness Archive – ICE Raids in Chicago Dashboard")

st.markdown("---")

# --------------------------------------------------
# Sidebar – filters
# --------------------------------------------------
st.sidebar.title("Filters")

# Optional focus on only fear & shock
focus_fs = st.sidebar.checkbox(
    "Focus only on fear & shock", value=False
)

working_df = df.copy()

if focus_fs and "emotion_label" in working_df.columns:
    working_df = working_df[working_df["emotion_label"].isin(["fear", "shock"])]

# Emotion filter
if "emotion_label" in working_df.columns:
    emotion_options = sorted(working_df["emotion_label"].dropna().unique())
else:
    emotion_options = []

selected_emotions = st.sidebar.multiselect(
    "Emotion",
    options=emotion_options,
    default=emotion_options,
)

# Narrative type filter
if "narrative_type" in working_df.columns:
    narrative_options = sorted(working_df["narrative_type"].dropna().unique())
else:
    narrative_options = []

selected_narratives = st.sidebar.multiselect(
    "Narrative type",
    options=narrative_options,
    default=narrative_options,
)

# Theme filter
if "theme_label" in working_df.columns:
    theme_options = sorted(working_df["theme_label"].dropna().unique())
else:
    theme_options = []

selected_themes = st.sidebar.multiselect(
    "Theme",
    options=theme_options,
    default=theme_options,
)

# Source filter
if "source" in working_df.columns:
    source_options = sorted(working_df["source"].dropna().unique())
else:
    source_options = []

selected_sources = st.sidebar.multiselect(
    "Source",
    options=source_options,
    default=source_options,
)

# --------------------------------------------------
# Apply filters to working_df
# --------------------------------------------------
filtered_df = working_df.copy()

if selected_emotions and "emotion_label" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["emotion_label"].isin(selected_emotions)]

if selected_narratives and "narrative_type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["narrative_type"].isin(selected_narratives)]

if selected_themes and "theme_label" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["theme_label"].isin(selected_themes)]

if selected_sources and "source" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]

# --------------------------------------------------
# Top summary – simple, clean metrics
# --------------------------------------------------
st.subheader("📊 Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total records (filtered)", len(filtered_df))

with c2:
    unique_articles = (
        filtered_df["article_id"].nunique()
        if "article_id" in filtered_df.columns
        else 0
    )
    st.metric("Unique articles", unique_articles)

with c3:
    if "date_published" in filtered_df.columns and not filtered_df["date_published"].isna().all():
        min_date = filtered_df["date_published"].min()
        max_date = filtered_df["date_published"].max()
        st.metric("Date range",
                  f"{min_date.date()} → {max_date.date()}")
    else:
        st.metric("Date range", "N/A")

st.markdown("---")

# --------------------------------------------------
# Tabs: Overview | Timeline | Data
# --------------------------------------------------
tab_overview, tab_timeline, tab_data = st.tabs(
    ["📈 Overview", "📅 Timeline", "📑 Data table"]
)

# ----------------- Overview tab --------------------
with tab_overview:
    st.markdown("### Emotion distribution")

    if "emotion_label" in filtered_df.columns and not filtered_df.empty:
        emo_counts = (
            filtered_df["emotion_label"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "emotion_label", "emotion_label": "count"})
        )

        emo_chart = (
            alt.Chart(emo_counts)
            .mark_bar()
            .encode(
                x=alt.X("emotion_label:N", title="Emotion"),
                y=alt.Y("count:Q", title="Count"),
                tooltip=["emotion_label", "count"],
            )
            .properties(height=300)
        )
        st.altair_chart(emo_chart, use_container_width=True)
    else:
        st.info("No emotion data available for the current filters.")

    # Optional: top themes
    if "theme_label" in filtered_df.columns and not filtered_df.empty:
        st.markdown("### Top themes")
        theme_counts = (
            filtered_df["theme_label"]
            .value_counts()
            .head(10)
            .reset_index()
            .rename(columns={"index": "theme_label", "theme_label": "count"})
        )

        theme_chart = (
            alt.Chart(theme_counts)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Count"),
                y=alt.Y("theme_label:N", title="Theme", sort="-x"),
                tooltip=["theme_label", "count"],
            )
            .properties(height=300)
        )
        st.altair_chart(theme_chart, use_container_width=True)

# ----------------- Timeline tab --------------------
with tab_timeline:
    st.markdown("### Narratives over time")

    if "date_published" in filtered_df.columns:
        time_df = filtered_df.dropna(subset=["date_published"]).copy()
        if not time_df.empty:
            time_group = (
                time_df
                .groupby(
                    [pd.Grouper(key="date_published", freq="M"), "emotion_label"],
                    dropna=True,
                )
                .size()
                .reset_index(name="count")
            )

            time_chart = (
                alt.Chart(time_group)
                .mark_line(point=True)
                .encode(
                    x=alt.X("date_published:T", title="Month"),
                    y=alt.Y("count:Q", title="Number of records"),
                    color=alt.Color("emotion_label:N", title="Emotion"),
                    tooltip=["date_published:T", "emotion_label:N", "count:Q"],
                )
                .properties(height=350)
            )

            st.altair_chart(time_chart, use_container_width=True)
        else:
            st.info("No valid dates available after filters.")
    else:
        st.info("Column `date_published` not found in the data.")

# ----------------- Data tab ------------------------
with tab_data:
    st.markdown("### Filtered records")

    show_cols = [
        col
        for col in [
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
        if col in filtered_df.columns
    ]

    st.dataframe(filtered_df[show_cols], use_container_width=True)

st.markdown("---")
st.caption(
    "Dashboard: Witness Archive – ICE Raids in Chicago."
)
