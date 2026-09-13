import io
import json
import os
import urllib.parse
import urllib.request
from collections import Counter

import numpy as np
import pandas as pd
import requests
import streamlit as st


# ============================================================
# SAI DDoS Detection Dashboard
# Automatically finds CSV files in this GitHub repository.
# No manual CSV upload is required.
# ============================================================

REPOSITORY = "pallasivasai/SAI_Algorithm_To_Detecting_DDoS_Attacks"
BRANCH = "main"
GITHUB_API = "https://api.github.com"

WINDOW_SIZE_DEFAULT = 10
EPSILON_DEFAULT = 0.01
THRESHOLD_DEFAULT = 0.70

st.set_page_config(
    page_title="SAI DDoS Detection",
    page_icon="🛡️",
    layout="wide",
)


def github_headers():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "SAI-DDoS-App"}
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def find_csv_files():
    """Find CSV files anywhere in the configured GitHub repository."""
    url = f"{GITHUB_API}/repos/{REPOSITORY}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(url, headers=github_headers(), timeout=30)
    response.raise_for_status()

    tree = response.json().get("tree", [])
    return [
        item["path"]
        for item in tree
        if item.get("type") == "blob" and item.get("path", "").lower().endswith(".csv")
    ]


def load_github_csv(path):
    """Download a CSV directly from GitHub into memory."""
    encoded_path = urllib.parse.quote(path, safe="/")
    url = f"https://raw.githubusercontent.com/{REPOSITORY}/{BRANCH}/{encoded_path}"

    response = requests.get(
        url,
        headers=github_headers(),
        timeout=120,
    )
    response.raise_for_status()

    data = io.BytesIO(response.content)

    # Low-memory first attempt.
    try:
        return pd.read_csv(data, low_memory=False)
    except Exception:
        data.seek(0)
        return pd.read_csv(data, encoding_errors="ignore", low_memory=False)


def clean_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def find_column(columns, candidates):
    normalized = {str(c).strip().lower(): c for c in columns}

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    for column in columns:
        low = str(column).strip().lower()
        if any(candidate.lower() in low for candidate in candidates):
            return column

    return None


def detect_columns(df):
    source_col = find_column(
        df.columns,
        [
            "src_ip", "source_ip", "source ip", "src ip",
            "ip.src", "source address", "src_addr", "source"
        ],
    )

    timestamp_col = find_column(
        df.columns,
        [
            "timestamp", "time", "datetime", "date time",
            "frame.time", "flow start time", "start_time"
        ],
    )

    label_col = find_column(
        df.columns,
        [
            "label", "attack", "class", "target", "category"
        ],
    )

    return source_col, timestamp_col, label_col


def prepare_time_column(df, timestamp_col):
    result = df.copy()
    result["__sai_time"] = pd.to_datetime(
        result[timestamp_col],
        errors="coerce",
    )

    if result["__sai_time"].notna().sum() == 0:
        numeric = pd.to_numeric(result[timestamp_col], errors="coerce")
        result["__sai_time"] = pd.to_datetime(numeric, unit="s", errors="coerce")

    return result


def sai_detect(df, source_col, timestamp_col, window_size, epsilon, threshold):
    """
    Implements the high-level SAI idea described in this repository's README:
    repeated, nearly-equal inter-packet gaps from the same source IP are scored.

    This is a dashboard implementation of the documented approach; it does not
    claim to reproduce the notebook's exact train/test pipeline or reported score.
    """
    data = prepare_time_column(df, timestamp_col)
    data = data.dropna(subset=[source_col, "__sai_time"]).copy()
    data = data.sort_values([source_col, "__sai_time"])

    data["__sai_delta"] = (
        data.groupby(source_col)["__sai_time"]
        .diff()
        .dt.total_seconds()
    )

    scores = np.zeros(len(data), dtype=float)
    repeated = np.zeros(len(data), dtype=int)

    # Work with original integer positions after sorting.
    data = data.reset_index(drop=True)

    for source, group in data.groupby(source_col, sort=False):
        indices = group.index.to_numpy()
        deltas = group["__sai_delta"].to_numpy(dtype=float)

        for local_i, row_index in enumerate(indices):
            start = max(0, local_i - window_size + 1)
            window = deltas[start:local_i + 1]
            window = window[np.isfinite(window)]

            if len(window) < 2:
                continue

            counts = Counter()
            for value in window:
                bucket = round(float(value) / epsilon) * epsilon if epsilon > 0 else float(value)
                counts[bucket] += 1

            max_repeat = max(counts.values()) if counts else 0
            score = max_repeat / len(window)

            repeated[row_index] = max_repeat
            scores[row_index] = score

    data["SAI_Repeated_Gaps"] = repeated
    data["SAI_Score"] = scores
    data["SAI_Detected"] = data["SAI_Score"] >= threshold

    return data


def safe_label_summary(df, label_col):
    if not label_col or label_col not in df.columns:
        return None

    values = df[label_col].astype(str).str.strip()
    return values.value_counts().head(15)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ SAI Algorithm — DDoS Detection")
st.caption(
    "Automatic GitHub CSV loading • Inter-packet timing analysis • Interactive detection dashboard"
)

with st.sidebar:
    st.header("⚙️ SAI Settings")

    window_size = st.slider(
        "Sliding window",
        min_value=3,
        max_value=50,
        value=WINDOW_SIZE_DEFAULT,
    )

    epsilon = st.number_input(
        "Gap tolerance (seconds)",
        min_value=0.000001,
        max_value=10.0,
        value=EPSILON_DEFAULT,
        step=0.001,
        format="%.6f",
    )

    threshold = st.slider(
        "Detection threshold",
        min_value=0.10,
        max_value=1.00,
        value=THRESHOLD_DEFAULT,
        step=0.05,
    )

    st.divider()
    st.write("**Repository**")
    st.code(REPOSITORY)
    st.write("**CSV source**")
    st.write("Automatically discovered from GitHub")


# ============================================================
# LOAD CSV FROM GITHUB AUTOMATICALLY
# ============================================================

try:
    csv_files = find_csv_files()
except Exception as exc:
    st.error(f"Could not inspect the GitHub repository: {exc}")
    st.stop()

if not csv_files:
    st.warning(
        "No CSV file is currently present in this GitHub repository. "
        "Once a CSV is added to the repository, this app will discover and load it automatically."
    )
    st.info(
        "The repository currently contains the project notebook and README, but no CSV was found."
    )
    st.stop()

selected_csv = st.selectbox(
    "GitHub dataset",
    csv_files,
)

try:
    with st.spinner(f"Loading {selected_csv} from GitHub..."):
        df = load_github_csv(selected_csv)
except Exception as exc:
    st.error(f"Could not load the GitHub CSV: {exc}")
    st.stop()

df = clean_columns(df)

source_col, timestamp_col, label_col = detect_columns(df)

# ============================================================
# DATA SUMMARY
# ============================================================

st.success(
    f"Dataset loaded automatically from GitHub: {selected_csv}"
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", f"{len(df.columns):,}")
m3.metric("Source IP column", source_col or "Not detected")
m4.metric("Timestamp column", timestamp_col or "Not detected")

if label_col:
    st.caption(f"Detected label column: `{label_col}`")

# ============================================================
# TABS
# ============================================================

tab_overview, tab_detection, tab_data, tab_about = st.tabs(
    ["📊 Overview", "🛡️ SAI Detection", "📄 Dataset", "ℹ️ About SAI"]
)

with tab_overview:
    st.subheader("Dataset Overview")

    c1, c2 = st.columns(2)

    with c1:
        st.write("**First rows**")
        st.dataframe(df.head(20), use_container_width=True)

    with c2:
        st.write("**Missing values**")
        missing = (
            df.isna()
            .sum()
            .sort_values(ascending=False)
            .head(20)
            .rename("missing")
            .to_frame()
        )
        st.dataframe(missing, use_container_width=True)

    if label_col:
        st.subheader("Label Distribution")
        summary = safe_label_summary(df, label_col)
        st.bar_chart(summary)

with tab_detection:
    st.subheader("SAI Timing-Pattern Detection")

    if not source_col or not timestamp_col:
        st.error(
            "SAI detection needs a source-IP column and a timestamp column. "
            "The app could not automatically identify both in this CSV."
        )
        st.write("Available columns:")
        st.write(list(df.columns))
    else:
        with st.spinner("Running SAI detection..."):
            detected = sai_detect(
                df,
                source_col,
                timestamp_col,
                window_size,
                epsilon,
                threshold,
            )

        total = len(detected)
        alerts = int(detected["SAI_Detected"].sum())
        alert_rate = (alerts / total * 100) if total else 0

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Analyzed rows", f"{total:,}")
        a2.metric("SAI alerts", f"{alerts:,}")
        a3.metric("Alert rate", f"{alert_rate:.2f}%")
        a4.metric("Threshold", f"{threshold:.2f}")

        st.subheader("Detection Results")

        show_cols = list(df.columns[: min(12, len(df.columns))])
        extra = ["SAI_Repeated_Gaps", "SAI_Score", "SAI_Detected"]
        show_cols = [c for c in show_cols if c not in extra] + extra

        st.dataframe(
            detected[show_cols].head(500),
            use_container_width=True,
        )

        st.subheader("SAI Score Distribution")
        st.bar_chart(
            detected["SAI_Detected"].value_counts().rename(
                {False: "Normal", True: "Detected"}
            )
        )

        suspicious = detected[detected["SAI_Detected"]].copy()

        st.subheader("Top Suspicious Source IPs")
        if len(suspicious):
            top_ips = (
                suspicious[source_col]
                .astype(str)
                .value_counts()
                .head(15)
                .rename("alerts")
                .to_frame()
            )
            st.bar_chart(top_ips)
        else:
            st.info("No rows crossed the current SAI threshold.")

        csv_bytes = detected.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Detection Results",
            data=csv_bytes,
            file_name="sai_ddos_detection_results.csv",
            mime="text/csv",
        )

with tab_data:
    st.subheader("Dataset Columns")
    st.write(list(df.columns))

    st.subheader("Dataset Statistics")
    st.dataframe(
        df.describe(include="all").transpose().head(50),
        use_container_width=True,
    )

with tab_about:
    st.subheader("SAI Algorithm")
    st.write(
        "The repository describes SAI as a lightweight DDoS detection approach "
        "based on repeated, nearly equal inter-packet time gaps from the same "
        "source IP. Low timing variation and high repetition are treated as "
        "suspicious patterns."
    )

    st.markdown(
        """
        **Pipeline**

        1. Load the CSV automatically from GitHub.
        2. Detect source-IP and timestamp columns.
        3. Sort packets by source IP and time.
        4. Calculate inter-arrival time (Δt).
        5. Examine repeated Δt values inside a sliding window.
        6. Calculate an SAI repetition score.
        7. Flag rows above the configured threshold.
        """
    )

    st.warning(
        "The dashboard implements the high-level SAI method documented in the repository. "
        "It does not claim to reproduce the exact notebook's reported 99.89% result "
        "unless the same dataset, preprocessing, split, tolerance and parameters are used."
    )
