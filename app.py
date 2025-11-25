import streamlit as st
import pandas as pd

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
    # IMPORTANT: filename must match your GitHub file
    df = pd.read_csv("corpus.csv.csv")

    # Normalize emotion labels: joy -> shock
    if "emotion_label" in df.columns:
        df["emotion_label"] = df["emotion_label"].astype(str).str.strip()
        df["emotion_label"] = df["emotion_label"].replace({"joy": "shock"})

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

# Optional: focus only fear & shock
focus_fs = st.sidebar.checkbox("Focus only on fear & shock", value=False)

working_df = df.copy()
if focus_fs and "emotion_label" in working_df.columns:
    working_df = working_df[working_df["emotion_label"].isin(["fear", "shock"])]

def multiselect_if(colname: str, label: str):
    """Create a multiselect only if the column exists."""
    if colname in working_df.columns:
        options = sorted(working_df[colname].dropna().unique())
        return st.sidebar.multiselect(label, options, default=options)
    return []

selected_emotions   = multiselect_if("emotion_label", "Emotion")
selected_narratives = multiselect_if("narrative_type", "Narrative type")
selected_themes     = multiselect_if("theme_label", "Theme")
selected_sources    = multiselect_if("source", "Source")

# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered = working_df.copy()

if selected_emotions and "emotion_label" in filtered.columns:
    filtered = filtered[filtered["emotion_label"].isin(selected_emotions)]

if selected_narratives and "narrative_type" in filtered.columns:
    filtered = filtered[filtered["narrative_type"].isin(selected_narratives)]

if selected_themes and "theme_label" in filtered.columns:
    filtered = filtered[filtered["theme_label"].isin(selected_themes)]

if selected_sources and "source" in filtered.columns:
    filtered = filtered[filtered["source"].isin(selected_sources)]

# --------------------------------------------------
# Summary metrics
# --------------------------------------------------
st.subheader("📊 Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total records (filtered)", len(filtered))

with col2:
    article_count = (
        filtered["article_id"].nunique()
        if "article_id" in filtered.columns
        else 0
    )
    st.metric("Unique articles", article_count)

with col3:
    if "date_published" in filtered.columns and not filtered["date_published"].isna().all():
        min_date = filtered["date_published"].min().date()
        max_date = filtered["date_published"].max().date()
        st.metric("Date range", f"{min_date} → {max_date}")
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

    if "emotion_label" in filtered.columns and not filtered.empty:
        emo_counts = filtered["emotion_label"].value_counts().sort_index()
        st.bar_chart(emo_counts)
    else:
        st.info("No emotion data for current filters.")

    st.markdown("### Top themes")
    if "theme_label" in filtered.columns and not filtered.empty:
        theme_counts = filtered["theme_label"].value_counts().head(10)
        st.bar_chart(theme_counts)
    else:
        st.info("No theme data for current filters.")

# ----------------- Timeline tab -------------------
with tab_timeline:
    st.markdown("### Narratives over time")

    if "date_published" in filtered.columns:
        time_df = filtered.dropna(subset=["date_published"]).copy()
        if not time_df.empty:
            # Group by month and emotion
            time_df["month"] = time_df["date_published"].dt.to_period("M").dt.to_timestamp()
            timeline = (
                time_df
                .groupby(["month", "emotion_label"])
                .size()
                .reset_index(name="count")
            )

            # Pivot so each emotion is a separate line
            pivot = timeline.pivot(
                index="month",
                columns="emotion_label",
                values="count"
            ).fillna(0).sort_index()

            st.line_chart(pivot)
        else:
            st.info("No valid dates after filtering.")
    else:
        st.info("Column `date_published` not found in data.")

# ----------------- Data tab -----------------------
with tab_data:
    st.markdown("### Filtered records")

    columns_to_show = [
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
    columns_to_show = [c for c in columns_to_show if c in filtered.columns]

    st.dataframe(filtered[columns_to_show], use_container_width=True)

st.markdown("---")
st.caption("Dashboard: Witness Archive – ICE Raids in Chicago.")
