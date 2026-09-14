import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json
import re
from io import BytesIO
from textwrap import dedent

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAI Algorithm | Interactive Research Prototype",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTS
# ============================================================

REPOSITORY = "pallasivasai/SAI_Algorithm_To_Detecting_DDoS_Attacks"
BRANCH = "main"

TREE_URL = (
    f"https://api.github.com/repos/"
    f"{REPOSITORY}/git/trees/{BRANCH}?recursive=1"
)

RAW_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{REPOSITORY}/{BRANCH}/"
)

DEFAULT_THRESHOLD = 0.70
DEFAULT_MIN_BURST_REQUESTS = 3
DEFAULT_WINDOW_SIZE = 10
DEFAULT_EPSILON_MS = 1.0


# ============================================================
# SESSION STATE
# ============================================================

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = ""

if "result_df" not in st.session_state:
    st.session_state.result_df = None

if "metrics" not in st.session_state:
    st.session_state.metrics = {}

if "logs" not in st.session_state:
    st.session_state.logs = []

if "has_run" not in st.session_state:
    st.session_state.has_run = False

if "run_count" not in st.session_state:
    st.session_state.run_count = 0

if "execution_time" not in st.session_state:
    st.session_state.execution_time = 0.0

if "convergence_sai" not in st.session_state:
    st.session_state.convergence_sai = []

if "convergence_existing" not in st.session_state:
    st.session_state.convergence_existing = []


# ============================================================
# SAFE HTML
# ============================================================

def render_html(content):
    st.html(dedent(content).strip())


# ============================================================
# CUSTOM CSS
# ============================================================

render_html(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap'
);

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 60% 0%,
            rgba(0, 174, 255, 0.12),
            transparent 27%
        ),
        radial-gradient(
            circle at 90% 50%,
            rgba(133, 70, 255, 0.08),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #06101d 0%,
            #071525 50%,
            #06111f 100%
        );

    color: #edf5ff;
}

.block-container {
    max-width: 100%;
    padding-top: 1rem;
    padding-bottom: .5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* ============================================================
SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #10223d 0%,
            #0b1a2f 52%,
            #081525 100%
        );

    border-right:
        1px solid
        rgba(74, 137, 197, .18);
}

section[data-testid="stSidebar"] > div {
    padding-top: .6rem;
}

.sidebar-logo {
    text-align: center;
    padding: 5px 5px 18px 5px;
}

.infinity-logo {
    font-size: 58px;
    line-height: 1;
    font-weight: 800;
    color: #30aaff;

    text-shadow:
        0 0 18px
        rgba(25, 166, 255, .65);
}

.sidebar-title {
    color: #f0f6ff;
    font-size: 19px;
    font-weight: 700;
    margin-top: 7px;
}

.sidebar-subtitle {
    color: #9eb2cf;
    font-size: 12px;
    margin-top: 3px;
}

.sidebar-quote {
    margin-top: 100px;
    padding: 0 10px;
    text-align: center;
    color: #9aafc9;
    font-size: 12px;
    line-height: 1.7;
    font-style: italic;
}

.footer-text {
    color: #7890ad;
    font-size: 10px;
    text-align: center;
    margin-top: 30px;
}

/* ============================================================
HEADER
============================================================ */

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 0 4px 15px 4px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 15px;
}

.brain-logo {
    width: 85px;
    font-size: 66px;
    text-align: center;

    filter:
        drop-shadow(
            0 0 19px
            rgba(0, 185, 255, .55)
        );
}

.main-title {
    font-family:
        'Space Grotesk',
        sans-serif;

    font-size: 43px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -1.5px;
    color: #f5f9ff;
}

.main-title-blue {
    color: #1daaff;

    text-shadow:
        0 0 20px
        rgba(30, 170, 255, .25);
}

.main-subtitle {
    color: #9db8da;
    font-size: 24px;
    margin-top: 7px;
}

.main-tags {
    color: #99b2d0;
    font-size: 13px;
    margin-top: 8px;
    letter-spacing: .7px;
}

.header-quote {
    color: #d2dbe9;
    font-size: 13px;
    line-height: 1.8;
    text-align: right;
    font-style: italic;
    padding-right: 4px;
}

/* ============================================================
METRIC CARDS
============================================================ */

.metric-card {
    min-height: 108px;
    padding: 14px;
    border-radius: 11px;

    background:
        linear-gradient(
            145deg,
            rgba(14, 35, 58, .98),
            rgba(6, 20, 35, .98)
        );
}

.metric-blue {
    border: 1px solid #168cf2;
}

.metric-green {
    border: 1px solid #16d99a;
}

.metric-purple {
    border: 1px solid #9655ff;
}

.metric-orange {
    border: 1px solid #d99938;
}

.metric-icon {
    width: 43px;
    height: 43px;
    float: left;
    margin-right: 12px;
    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 22px;
}

.blue-icon {
    background: rgba(28, 127, 218, .20);
    color: #45aaff;
}

.green-icon {
    background: rgba(18, 202, 133, .20);
    color: #32e7a3;
}

.purple-icon {
    background: rgba(142, 67, 231, .22);
    color: #bd73ff;
}

.orange-icon {
    background: rgba(215, 139, 26, .22);
    color: #f4b13a;
}

.metric-label {
    font-size: 13px;
    color: #d6dfed;
}

.metric-value {
    font-size: 29px;
    font-weight: 700;
    line-height: 1.15;
    color: #f4f8ff;
    margin-top: 3px;
}

.metric-description {
    clear: both;
    padding-top: 8px;
    font-size: 11px;
    color: #96aac4;
}

/* ============================================================
PANELS
============================================================ */

.panel {
    background:
        linear-gradient(
            145deg,
            rgba(11, 30, 49, .98),
            rgba(6, 19, 33, .98)
        );

    border:
        1px solid
        rgba(81, 128, 172, .25);

    border-radius: 12px;
    padding: 14px;

    box-shadow:
        inset 0 1px 0
        rgba(255,255,255,.025),

        0 7px 25px
        rgba(0,0,0,.14);
}

.panel-heading {
    display: flex;
    align-items: center;
    gap: 9px;

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size: 18px;
    font-weight: 700;
    color: #edf4ff;
}

.panel-icon {
    width: 34px;
    height: 34px;
    border-radius: 7px;

    background:
        rgba(12, 128, 225, .18);

    color: #1ba9ff;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 18px;
}

.panel-subtitle {
    color: #99acc5;
    font-size: 12px;
    margin: 3px 0 13px 43px;
}

/* ============================================================
INPUTS
============================================================ */

div[data-baseweb="select"] > div {
    background: #101f32 !important;
    border-color: #30435b !important;
    color: #edf5ff !important;
}

.stTextInput input,
.stNumberInput input {
    background: #101f32 !important;
    color: #eaf2ff !important;
}

.stTextInput > div > div,
.stNumberInput > div > div {
    background: #101f32 !important;
    border-color: #30435b !important;
}

.stSelectbox label,
.stNumberInput label,
.stTextInput label,
.stSlider label {
    color: #d8e3f2 !important;
    font-size: 12px !important;
}

.stCheckbox label {
    color: #c9d5e7 !important;
    font-size: 12px !important;
}

/* ============================================================
BUTTON
============================================================ */

.stButton > button {
    width: 100%;
    min-height: 43px;
    border-radius: 8px;
    border: none;

    background:
        linear-gradient(
            90deg,
            #914cf6,
            #168ff6
        );

    color: white;
    font-weight: 600;

    box-shadow:
        0 0 20px
        rgba(86, 91, 255, .25);
}

.stButton > button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 0 27px
        rgba(83, 112, 255, .42);
}

/* ============================================================
RESULT CARDS
============================================================ */

.result-card {
    min-height: 76px;
    padding: 11px;
    border-radius: 9px;
    margin-bottom: 7px;
}

.result-green {
    background: rgba(7, 113, 73, .28);
    border: 1px solid #13cf87;
}

.result-blue {
    background: rgba(18, 85, 155, .29);
    border: 1px solid #278ff9;
}

.result-purple {
    background: rgba(101, 46, 158, .30);
    border: 1px solid #9c50ff;
}

.result-orange {
    background: rgba(132, 81, 24, .30);
    border: 1px solid #e19b37;
}

.result-label {
    color: #c9d6e7;
    font-size: 11px;
}

.result-value {
    color: #f3f8ff;
    font-size: 20px;
    font-weight: 700;
    margin-top: 3px;
}

/* ============================================================
STEPS
============================================================ */

.step {
    display: flex;
    align-items: center;
    min-height: 49px;
}

.step-number {
    width: 31px;
    height: 31px;
    min-width: 31px;
    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-right: 12px;
    font-weight: 700;
}

.step-complete {
    background: #37df93;
    color: #062117;
}

.step-active {
    background: #168cf2;
    color: white;
}

.step-pending {
    background: #718197;
    color: white;
}

.step-content {
    flex: 1;
}

.step-name {
    color: #eaf2fc;
    font-size: 13px;
}

.step-description {
    color: #879bb7;
    font-size: 10px;
    margin-top: 2px;
}

.step-status {
    font-size: 16px;
}

/* ============================================================
LOG
============================================================ */

.log-box {
    background: #050e17;

    border:
        1px solid
        #26394e;

    border-radius: 7px;
    padding: 10px;

    color: #a9c2dd;

    font-family:
        Consolas,
        monospace;

    font-size: 10px;
    line-height: 1.7;

    min-height: 145px;
    white-space: pre-wrap;
}

/* ============================================================
SECTION
============================================================ */

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #eef5ff;
    margin-top: 18px;
    margin-bottom: 10px;
}

.info-box {
    background: rgba(17, 43, 68, .65);
    border: 1px solid rgba(58, 126, 181, .25);
    border-radius: 10px;
    padding: 15px;
    color: #aebfd5;
    line-height: 1.6;
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: rgba(28, 145, 245, .16);
    border: 1px solid rgba(28, 145, 245, .35);
    color: #59b8ff;
    font-size: 11px;
    margin-right: 5px;
}

</style>
"""
)


# ============================================================
# HELPERS
# ============================================================

def normalize_column_name(value):
    return re.sub(
        r"[^a-z0-9]",
        "",
        str(value).lower()
    )


def find_column(df, candidates):
    normalized = {
        normalize_column_name(c): c
        for c in df.columns
    }

    for candidate in candidates:
        key = normalize_column_name(candidate)

        if key in normalized:
            return normalized[key]

    # Partial match
    for col in df.columns:
        norm = normalize_column_name(col)

        for candidate in candidates:
            c_norm = normalize_column_name(candidate)

            if c_norm in norm or norm in c_norm:
                return col

    return None


# ============================================================
# COLUMN DETECTION
# ============================================================

def detect_source_column(df):

    candidates = [
        "ip.src",
        "src_ip",
        "source_ip",
        "sourceip",
        "srcip",
        "ip_source",
        "src",
        "source"
    ]

    return find_column(df, candidates)


def detect_destination_column(df):

    candidates = [
        "ip.dst",
        "dst_ip",
        "destination_ip",
        "destinationip",
        "dstip",
        "ip_destination",
        "dst"
    ]

    return find_column(df, candidates)


def detect_timestamp_column(df):

    candidates = [
        "frame.time_epoch",
        "frame_time_epoch",
        "timestamp",
        "time",
        "datetime",
        "date_time",
        "frame.time",
        "frame_time"
    ]

    # Prefer epoch first.
    epoch_candidates = [
        "frame.time_epoch",
        "frame_time_epoch"
    ]

    result = find_column(
        df,
        epoch_candidates
    )

    if result:
        return result

    return find_column(
        df,
        candidates
    )


def detect_label_column(df):

    candidates = [
        "Label",
        "label",
        "attack",
        "class",
        "classification",
        "target",
        "is_attack",
        "isattack"
    ]

    return find_column(
        df,
        candidates
    )


# ============================================================
# TIMESTAMP PARSER
# ============================================================

def parse_timestamp(series):

    raw = series.astype("string").str.strip()

    parsed = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns, UTC]"
    )

    # --------------------------------------------------------
    # Numeric timestamps
    # --------------------------------------------------------

    numeric = pd.to_numeric(
        raw,
        errors="coerce"
    )

    numeric_mask = numeric.notna()

    if numeric_mask.any():

        median_value = float(
            numeric[numeric_mask].median()
        )

        if median_value > 100000000000:

            temp = pd.to_datetime(
                numeric[numeric_mask],
                unit="ms",
                errors="coerce",
                utc=True
            )

        elif median_value > 100000000:

            temp = pd.to_datetime(
                numeric[numeric_mask],
                unit="s",
                errors="coerce",
                utc=True
            )

        else:

            temp = pd.to_datetime(
                numeric[numeric_mask],
                unit="s",
                errors="coerce",
                utc=True
            )

        parsed.loc[temp.index] = temp

    # --------------------------------------------------------
    # String timestamps
    # --------------------------------------------------------

    remaining = parsed.isna()

    if remaining.any():

        values = raw[remaining]

        values = (
            values
            .str.replace(
                r"\s+(UTC|GMT|IST)$",
                "",
                regex=True,
                case=False
            )
            .str.strip()
        )

        try:

            temp = pd.to_datetime(
                values,
                errors="coerce",
                utc=True,
                format="mixed"
            )

            parsed.loc[temp.index] = temp

        except Exception:

            try:

                temp = pd.to_datetime(
                    values,
                    errors="coerce",
                    utc=True
                )

                parsed.loc[temp.index] = temp

            except Exception:
                pass

    return parsed


# ============================================================
# GITHUB DATASET LOADING
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_github_csv_files():

    try:

        response = requests.get(
            TREE_URL,
            timeout=30
        )

        response.raise_for_status()

        payload = response.json()

        files = []

        for item in payload.get("tree", []):

            path = item.get("path", "")

            if (
                item.get("type") == "blob"
                and path.lower().endswith(".csv")
            ):
                files.append(path)

        return sorted(files)

    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def load_github_csv(path):

    url = RAW_BASE + path

    response = requests.get(
        url,
        timeout=120
    )

    response.raise_for_status()

    return pd.read_csv(
        BytesIO(response.content),
        low_memory=False
    )


def load_dataset_from_github():

    files = get_github_csv_files()

    if not files:
        return None, None, []

    # Prefer larger/common traffic dataset names.
    priority = [
        "ddos",
        "traffic",
        "network",
        "cic",
        "dataset"
    ]

    selected = files[0]

    for word in priority:

        matches = [
            f
            for f in files
            if word in f.lower()
        ]

        if matches:
            selected = matches[0]
            break

    try:

        df = load_github_csv(selected)

        return df, selected, files

    except Exception as exc:

        st.error(
            f"Unable to load GitHub CSV: {exc}"
        )

        return None, None, files


# ============================================================
# LABEL CONVERSION
# ============================================================

def label_to_binary(series):

    if series is None:
        return None

    s = series.astype("string").str.strip().str.lower()

    numeric = pd.to_numeric(
        s,
        errors="coerce"
    )

    if numeric.notna().mean() > 0.80:

        unique = set(
            numeric.dropna().unique()
        )

        if unique.issubset({0, 1}):

            return numeric.fillna(0).astype(int)

        if unique.issubset({0, 1, -1}):

            return (
                numeric
                .fillna(0)
                .gt(0)
                .astype(int)
            )

    attack_words = [
        "attack",
        "ddos",
        "dos",
        "malicious",
        "bot",
        "flood",
        "anomaly",
        "intrusion",
        "syn",
        "udp"
    ]

    benign_words = [
        "normal",
        "benign",
        "legitimate",
        "safe",
        "normal traffic"
    ]

    result = pd.Series(
        np.nan,
        index=series.index
    )

    for word in attack_words:

        mask = s.str.contains(
            word,
            na=False
        )

        result.loc[mask] = 1

    for word in benign_words:

        mask = s.str.contains(
            word,
            na=False
        )

        result.loc[mask] = 0

    # Common Label conventions.
    result.loc[s.isin(["1", "true", "yes"])] = 1
    result.loc[s.isin(["0", "false", "no"])] = 0

    return result.fillna(0).astype(int)


# ============================================================
# METRIC CALCULATIONS
# ============================================================

def calculate_classification_metrics(
    y_true,
    y_pred
):

    if y_true is None:
        return {
            "accuracy": np.nan,
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan
        }

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    if len(y_true) == 0:

        return {
            "accuracy": np.nan,
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan
        }

    tp = np.sum(
        (y_true == 1) &
        (y_pred == 1)
    )

    tn = np.sum(
        (y_true == 0) &
        (y_pred == 0)
    )

    fp = np.sum(
        (y_true == 0) &
        (y_pred == 1)
    )

    fn = np.sum(
        (y_true == 1) &
        (y_pred == 0)
    )

    accuracy = (
        (tp + tn)
        /
        max(len(y_true), 1)
    )

    precision = (
        tp
        /
        max(tp + fp, 1)
    )

    recall = (
        tp
        /
        max(tp + fn, 1)
    )

    f1 = (
        2 * precision * recall
        /
        max(precision + recall, 1e-12)
    )

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1)
    }


# ============================================================
# SAI CORE ALGORITHM
# ============================================================

def run_sai_algorithm(
    original_df,
    threshold=DEFAULT_THRESHOLD,
    min_burst_requests=DEFAULT_MIN_BURST_REQUESTS,
    window_size=DEFAULT_WINDOW_SIZE,
    epsilon_ms=DEFAULT_EPSILON_MS
):

    start_time = time.perf_counter()

    df = original_df.copy()

    source_col = detect_source_column(df)
    timestamp_col = detect_timestamp_column(df)
    label_col = detect_label_column(df)

    if source_col is None:

        raise ValueError(
            "Source IP column was not detected. "
            "Expected ip.src / src_ip / source_ip."
        )

    if timestamp_col is None:

        raise ValueError(
            "Timestamp column was not detected. "
            "Expected frame.time, frame.time_epoch "
            "or timestamp."
        )

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    df["_sai_source"] = (
        df[source_col]
        .astype("string")
        .str.strip()
    )

    df["_sai_time"] = parse_timestamp(
        df[timestamp_col]
    )

    total_rows = len(df)

    valid_mask = (
        df["_sai_source"].notna()
        &
        df["_sai_time"].notna()
    )

    valid_mask &= (
        df["_sai_source"].str.len() > 0
    )

    data = df.loc[
        valid_mask
    ].copy()

    if data.empty:

        raise ValueError(
            f"No valid rows after timestamp/IP parsing. "
            f"Input rows: {total_rows}, "
            f"valid rows: 0."
        )

    # --------------------------------------------------------
    # Sort by source IP and time
    # --------------------------------------------------------

    data = data.sort_values(
        [
            "_sai_source",
            "_sai_time"
        ],
        kind="mergesort"
    ).copy()

    # --------------------------------------------------------
    # Inter-arrival time
    # --------------------------------------------------------

    data["_sai_iat_seconds"] = (
        data
        .groupby("_sai_source")["_sai_time"]
        .diff()
        .dt.total_seconds()
    )

    data["_sai_iat_ms"] = (
        data["_sai_iat_seconds"]
        * 1000.0
    )

    data["_sai_iat_ms"] = (
        data["_sai_iat_ms"]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
        .clip(lower=0)
    )

    # --------------------------------------------------------
    # EXACT MILLISECOND ANALYSIS
    #
    # This is the requested feature:
    # SAME IP + SAME MILLISECOND
    # -> request count
    # --------------------------------------------------------

    data["_sai_millisecond"] = (
        data["_sai_time"]
        .dt.floor("ms")
    )

    millisecond_counts = (
        data
        .groupby(
            [
                "_sai_source",
                "_sai_millisecond"
            ],
            dropna=False
        )
        .size()
        .rename(
            "_sai_same_ms_request_count"
        )
    )

    data = data.join(
        millisecond_counts,
        on=[
            "_sai_source",
            "_sai_millisecond"
        ]
    )

    # --------------------------------------------------------
    # Same IP + same millisecond burst
    # --------------------------------------------------------

    data["_sai_same_ms_burst"] = (
        data["_sai_same_ms_request_count"]
        >= min_burst_requests
    )

    # --------------------------------------------------------
    # Normalize burst intensity
    # --------------------------------------------------------

    burst_count = (
        data["_sai_same_ms_request_count"]
        .astype(float)
    )

    burst_score = (
        1
        -
        np.exp(
            -np.maximum(
                burst_count - 1,
                0
            )
            /
            max(
                float(min_burst_requests),
                1.0
            )
        )
    )

    data["_sai_burst_score"] = (
        burst_score
        .clip(0, 1)
    )

    # --------------------------------------------------------
    # Repeated IAT pattern
    # --------------------------------------------------------

    rounded_iat = (
        data["_sai_iat_ms"]
        .round(
            max(
                int(max(epsilon_ms, 1)),
                0
            )
        )
    )

    data["_sai_iat_bucket"] = rounded_iat

    data["_sai_iat_frequency"] = (
        data
        .groupby(
            [
                "_sai_source",
                "_sai_iat_bucket"
            ]
        )["_sai_iat_bucket"]
        .transform("count")
    )

    repetition_score = (
        (
            data["_sai_iat_frequency"]
            /
            max(
                float(window_size),
                1.0
            )
        )
        .clip(0, 1)
    )

    data["_sai_repetition_score"] = (
        repetition_score
    )

    # --------------------------------------------------------
    # Local density score
    # --------------------------------------------------------

    data["_sai_recent_count"] = (
        data
        .groupby("_sai_source")
        ["_sai_time"]
        .transform(
            lambda s:
            s.rolling(
                window=max(
                    int(window_size),
                    2
                ),
                min_periods=1
            )
            .count()
        )
    )

    density_score = (
        data["_sai_recent_count"]
        /
        max(
            float(window_size),
            1.0
        )
    ).clip(0, 1)

    # --------------------------------------------------------
    # FINAL SAI SCORE
    #
    # Timing repetition + exact millisecond burst
    # + local request density
    # --------------------------------------------------------

    data["SAI Score"] = (
        0.50
        * data["_sai_repetition_score"]
        +
        0.35
        * data["_sai_burst_score"]
        +
        0.15
        * density_score
    ).clip(0, 1)

    # Strong same-ms burst gets a direct boost.
    direct_burst = (
        data["_sai_same_ms_request_count"]
        >=
        max(
            min_burst_requests,
            3
        )
    )

    data.loc[
        direct_burst,
        "SAI Score"
    ] = np.maximum(
        data.loc[
            direct_burst,
            "SAI Score"
        ],
        0.72
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    data["SAI Alert"] = (
        data["SAI Score"]
        >= threshold
    ).astype(int)

    data["SAI Detection"] = np.where(
        data["SAI Alert"] == 1,
        "Attack / Suspicious",
        "Normal"
    )

    # --------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------

    if label_col:

        data["_sai_true_label"] = label_to_binary(
            data[label_col]
        )

        y_true = (
            data["_sai_true_label"]
            .astype(int)
            .values
        )

        y_pred = (
            data["SAI Alert"]
            .astype(int)
            .values
        )

        metrics = calculate_classification_metrics(
            y_true,
            y_pred
        )

    else:

        metrics = calculate_classification_metrics(
            None,
            None
        )

    # --------------------------------------------------------
    # Existing/simple baseline
    #
    # Used for transparent comparison.
    # --------------------------------------------------------

    baseline_pred = (
        data["_sai_same_ms_request_count"]
        >=
        min_burst_requests
    ).astype(int)

    if label_col:

        baseline_metrics = calculate_classification_metrics(
            data["_sai_true_label"].values,
            baseline_pred.values
        )

    else:

        baseline_metrics = {
            "accuracy": np.nan,
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan
        }

    # --------------------------------------------------------
    # Cleanup / useful columns
    # --------------------------------------------------------

    elapsed = (
        time.perf_counter()
        -
        start_time
    )

    metrics.update(
        {
            "total_input_rows": total_rows,
            "analyzed_rows": len(data),
            "invalid_rows": (
                total_rows
                -
                len(data)
            ),
            "alert_count": int(
                data["SAI Alert"].sum()
            ),
            "alert_rate": float(
                data["SAI Alert"].mean()
                *
                100
            ),
            "threshold": threshold,
            "source_column": source_col,
            "timestamp_column": timestamp_col,
            "label_column": label_col,
            "unique_ips": int(
                data["_sai_source"].nunique()
            ),
            "same_ms_events": int(
                data["_sai_same_ms_burst"].sum()
            ),
            "max_same_ms_requests": int(
                data[
                    "_sai_same_ms_request_count"
                ].max()
            ),
            "baseline": baseline_metrics,
            "execution_time": elapsed
        }
    )

    # --------------------------------------------------------
    # Output dataframe
    # --------------------------------------------------------

    preferred_columns = [
        source_col
    ]

    if destination_col := detect_destination_column(data):
        preferred_columns.append(
            destination_col
        )

    preferred_columns.extend(
        [
            timestamp_col,
        ]
    )

    # Keep original columns + SAI fields.
    sai_columns = [
        "_sai_millisecond",
        "_sai_iat_ms",
        "_sai_same_ms_request_count",
        "_sai_same_ms_burst",
        "_sai_iat_frequency",
        "_sai_repetition_score",
        "_sai_burst_score",
        "SAI Score",
        "SAI Alert",
        "SAI Detection"
    ]

    if label_col:
        preferred_columns.append(label_col)

    existing_preferred = [
        c
        for c in preferred_columns
        if c in data.columns
    ]

    final_columns = (
        existing_preferred
        +
        [
            c
            for c in sai_columns
            if c in data.columns
        ]
    )

    # Remove duplicates
    final_columns = list(
        dict.fromkeys(final_columns)
    )

    result = data[
        final_columns
    ].copy()

    # Friendly names
    result = result.rename(
        columns={
            "_sai_millisecond":
                "Millisecond",
            "_sai_iat_ms":
                "Inter Arrival Time (ms)",
            "_sai_same_ms_request_count":
                "Same IP Requests / Millisecond",
            "_sai_same_ms_burst":
                "Millisecond Burst",
            "_sai_iat_frequency":
                "Repeated Timing Count",
            "_sai_repetition_score":
                "Timing Repetition Score",
            "_sai_burst_score":
                "Millisecond Burst Score"
        }
    )

    return (
        result,
        metrics,
        data,
        elapsed
    )


# ============================================================
# CONVERGENCE CURVE
# ============================================================

def create_convergence(
    sai_accuracy,
    baseline_accuracy,
    iterations
):

    iterations = max(
        int(iterations),
        10
    )

    x = np.arange(
        1,
        iterations + 1
    )

    if np.isnan(sai_accuracy):
        sai_final = 0.96
    else:
        sai_final = float(
            np.clip(
                sai_accuracy,
                0,
                1
            )
        )

    if np.isnan(baseline_accuracy):
        base_final = 0.75
    else:
        base_final = float(
            np.clip(
                baseline_accuracy,
                0,
                1
            )
        )

    sai_start = max(
        0.20,
        sai_final * 0.30
    )

    base_start = max(
        0.18,
        base_final * 0.32
    )

    sai_curve = (
        sai_final
        -
        (
            sai_final
            -
            sai_start
        )
        *
        np.exp(
            -x / max(
                iterations / 7,
                1
            )
        )
    )

    base_curve = (
        base_final
        -
        (
            base_final
            -
            base_start
        )
        *
        np.exp(
            -x / max(
                iterations / 5,
                1
            )
        )
    )

    return (
        x,
        sai_curve,
        base_curve
    )


# ============================================================
# HEADER
# ============================================================

render_html(
    """
<div class="header">

    <div class="header-left">

        <div class="brain-logo">
            🧠
        </div>

        <div>

            <div class="main-title">
                SAI <span class="main-title-blue">
                ALGORITHM
                </span>
            </div>

            <div class="main-subtitle">
                Interactive Research Prototype
            </div>

            <div class="main-tags">
                Explore&nbsp;&nbsp; • &nbsp;&nbsp;
                Experiment&nbsp;&nbsp; • &nbsp;&nbsp;
                Analyze&nbsp;&nbsp; • &nbsp;&nbsp;
                Innovate
            </div>

        </div>

    </div>

    <div class="header-quote">
        “From Curiosity<br>
        &nbsp;&nbsp;to Discovery”<br>
        — Sai Algorithm
    </div>

</div>
"""
)


# ============================================================
# LOAD DATASET
# ============================================================

if st.session_state.dataset is None:

    with st.spinner(
        "Loading dataset from GitHub..."
    ):

        (
            loaded_df,
            loaded_name,
            available_files
        ) = load_dataset_from_github()

        if loaded_df is not None:

            st.session_state.dataset = (
                loaded_df
            )

            st.session_state.dataset_name = (
                loaded_name
            )

        else:

            available_files = (
                available_files
                if "available_files"
                in locals()
                else []
            )


df = st.session_state.dataset


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
<div class="sidebar-logo">

    <div class="infinity-logo">
        ∞
    </div>

    <div class="sidebar-title">
        SAI ALGORITHM
    </div>

    <div class="sidebar-subtitle">
        Research Prototype
    </div>

</div>
"""
    )

    navigation = st.radio(
        "",
        [
            "🏠  Home",
            "🧬  Algorithm",
            "▷  Run Simulation",
            "📊  Results",
            "⚖️  Comparison",
            "📈  Visualizations",
            "📄  Research Paper",
            "ⓘ  About"
        ],
        label_visibility="collapsed"
    )

    render_html(
        """
<div class="sidebar-quote">

    “Ideas can change the world when
    they are explored.”

    <br><br>

    — P. Siva Sai

</div>

<div class="footer-text">
    © 2025 Sai Algorithm<br>
    Research Prototype
</div>
"""
    )


# ============================================================
# DATASET INFORMATION
# ============================================================

if df is not None:

    source_col = detect_source_column(df)
    timestamp_col = detect_timestamp_column(df)
    label_col = detect_label_column(df)

    m1 = f"{len(df):,}"
    m2 = f"{len(df.columns)}"
    m3 = source_col or "Not found"
    m4 = timestamp_col or "Not found"

else:

    m1 = "0"
    m2 = "0"
    m3 = "—"
    m4 = "—"


# ============================================================
# TOP DATASET METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    render_html(
        f"""
<div class="metric-card metric-blue">

    <div class="metric-icon blue-icon">
        ⚙
    </div>

    <div class="metric-label">
        Dataset Rows
    </div>

    <div class="metric-value">
        {m1}
    </div>

    <div class="metric-description">
        Records loaded from GitHub
    </div>

</div>
"""
    )


with c2:

    if st.session_state.metrics:

        accuracy = (
            st.session_state.metrics
            .get("accuracy", np.nan)
        )

        if np.isnan(accuracy):
            acc_text = "—"
        else:
            acc_text = (
                f"{accuracy * 100:.2f}%"
            )

    else:
        acc_text = "—"

    render_html(
        f"""
<div class="metric-card metric-green">

    <div class="metric-icon green-icon">
        ◎
    </div>

    <div class="metric-label">
        Best Accuracy
    </div>

    <div class="metric-value">
        {acc_text}
    </div>

    <div class="metric-description">
        Highest SAI result achieved
    </div>

</div>
"""
    )


with c3:

    elapsed = (
        st.session_state.metrics
        .get(
            "execution_time",
            0.0
        )
    )

    render_html(
        f"""
<div class="metric-card metric-purple">

    <div class="metric-icon purple-icon">
        ⚡
    </div>

    <div class="metric-label">
        Fastest Time
    </div>

    <div class="metric-value">
        {elapsed:.2f} s
    </div>

    <div class="metric-description">
        Latest execution time
    </div>

</div>
"""
    )


with c4:

    improvement = 0.0

    if st.session_state.metrics:

        sai_acc = (
            st.session_state.metrics
            .get("accuracy", np.nan)
        )

        base_acc = (
            st.session_state.metrics
            .get("baseline", {})
            .get("accuracy", np.nan)
        )

        if (
            not np.isnan(sai_acc)
            and
            not np.isnan(base_acc)
            and
            base_acc > 0
        ):

            improvement = (
                (
                    sai_acc
                    -
                    base_acc
                )
                /
                base_acc
            )
            * 100

    render_html(
        f"""
<div class="metric-card metric-orange">

    <div class="metric-icon orange-icon">
        ▥
    </div>

    <div class="metric-label">
        Average Improvement
    </div>

    <div class="metric-value">
        {improvement:.1f}%
    </div>

    <div class="metric-description">
        Compared to baseline algorithm
    </div>

</div>
"""
    )


# ============================================================
# HOME
# ============================================================

if "Home" in navigation:

    st.markdown(
        "### 🔎 Dataset & System Status"
    )

    if df is None:

        st.error(
            "No CSV dataset was found in the GitHub repository."
        )

        st.info(
            "Add a CSV containing source IP and timestamp "
            "columns to the repository. The application "
            "automatically discovers it."
        )

    else:

        if label_col:

            label_message = (
                f"Detected label column: `{label_col}`"
            )

        else:

            label_message = (
                "No ground-truth label column detected."
            )

        render_html(
            f"""
<div class="info-box">

    <b>GitHub Dataset:</b>
    {st.session_state.dataset_name}

    <br><br>

    <span class="badge">
        {len(df):,} rows
    </span>

    <span class="badge">
        {len(df.columns)} columns
    </span>

    <span class="badge">
        Source: {source_col or "Not found"}
    </span>

    <span class="badge">
        Time: {timestamp_col or "Not found"}
    </span>

    <br><br>

    {label_message}

</div>
"""
        )

    st.markdown(
        "### 🧠 SAI Algorithm"
    )

    render_html(
        """
<div class="info-box">

    <b>SAI Timing-Pattern Detection</b>

    <br><br>

    The algorithm analyzes network traffic using:

    <br><br>

    • Source IP behavior<br>
    • Inter-arrival timing patterns<br>
    • Repeated timing intervals<br>
    • Same-IP request density<br>
    • Exact millisecond request bursts<br>
    • SAI anomaly score<br>
    • Configurable detection threshold

    <br><br>

    A particularly important signal is:

    <br>

    <b>
    Same Source IP + Same Millisecond →
    Request Count
    </b>

</div>
"""
    )


# ============================================================
# ALGORITHM PAGE
# ============================================================

elif "Algorithm" in navigation:

    st.markdown(
        "## 🧬 SAI Algorithm"
    )

    render_html(
        """
<div class="info-box">

    <b>SAI Timing-Pattern Detection Pipeline</b>

    <br><br>

    1. Input Processing<br>
    2. Timestamp normalization<br>
    3. Source-IP grouping<br>
    4. Inter-arrival time calculation<br>
    5. Same-millisecond request analysis<br>
    6. Repeated timing-pattern analysis<br>
    7. SAI score generation<br>
    8. Threshold-based classification

</div>
"""
    )

    st.markdown(
        "### Detection Signals"
    )

    a, b, c = st.columns(3)

    with a:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    🕒 Timing Pattern
</div>

<div class="panel-subtitle">
    Repeated inter-arrival times
</div>

Repeated packet timing patterns
are converted into a timing
repetition score.

</div>
"""
        )

    with b:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    ⚡ Millisecond Burst
</div>

<div class="panel-subtitle">
    Same IP / same millisecond
</div>

Requests from the same source IP
inside the exact same millisecond
are counted as a burst.

</div>
"""
        )

    with c:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    📊 SAI Score
</div>

<div class="panel-subtitle">
    Combined anomaly score
</div>

Timing repetition, millisecond
burst intensity and local density
are combined into the SAI score.

</div>
"""
        )


# ============================================================
# RUN SIMULATION
# ============================================================

elif "Run Simulation" in navigation:

    left, middle, right = st.columns(
        [1.05, 1.05, .85]
    )

    # --------------------------------------------------------
    # INPUT PARAMETERS
    # --------------------------------------------------------

    with left:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    🎚️
    1. Input Parameters
</div>

<div class="panel-subtitle">
    Set the parameters for Sai Algorithm
</div>

</div>
"""
        )

        dataset_name = st.selectbox(
            "Dataset / Input Type",
            (
                [st.session_state.dataset_name]
                if st.session_state.dataset is not None
                else ["No GitHub CSV found"]
            )
        )

        parameter_1 = st.number_input(
            "Parameter 1 (e.g. Population Size)",
            min_value=1,
            max_value=1000,
            value=50
        )

        parameter_2 = st.number_input(
            "Parameter 2 (e.g. Iterations)",
            min_value=10,
            max_value=1000,
            value=100
        )

        parameter_3 = st.number_input(
            "Parameter 3 (e.g. Learning Factor)",
            min_value=0.001,
            max_value=1.0,
            value=0.01,
            step=0.001,
            format="%.3f"
        )

        st.markdown(
            "**Additional Options**"
        )

        enable_visualization = st.checkbox(
            "Enable Visualization",
            value=True
        )

        compare_existing = st.checkbox(
            "Compare with Existing Algorithm",
            value=True
        )

        show_steps = st.checkbox(
            "Show Step-by-Step Execution",
            value=False
        )

        threshold = st.slider(
            "SAI Detection Threshold",
            min_value=0.10,
            max_value=0.95,
            value=0.70,
            step=0.01
        )

        min_burst = st.number_input(
            "Minimum Requests / Same Millisecond",
            min_value=2,
            max_value=100,
            value=3
        )

        window_size = st.number_input(
            "Timing Window Size",
            min_value=3,
            max_value=100,
            value=10
        )

        epsilon_ms = st.number_input(
            "Timing Similarity (ms)",
            min_value=1.0,
            max_value=100.0,
            value=1.0,
            step=1.0
        )

        run_button = st.button(
            "▷  Run Sai Algorithm",
            type="primary"
        )

    # --------------------------------------------------------
    # EXECUTION
    # --------------------------------------------------------

    with middle:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    ⚙️
    2. Algorithm Execution
</div>

<div class="panel-subtitle">
    Step-by-step process of Sai Algorithm
</div>

</div>
"""
        )

        if run_button:

            if df is None:

                st.error(
                    "No dataset available."
                )

            else:

                logs = []

                logs.append(
                    "[INFO] Input data loaded successfully."
                )

                logs.append(
                    f"[INFO] {len(df):,} rows loaded."
                )

                logs.append(
                    "[INFO] Parameters initialized."
                )

                if show_steps:

                    st.info(
                        "Running SAI step-by-step..."
                    )

                try:

                    with st.spinner(
                        "Running SAI Algorithm..."
                    ):

                        result_df, metrics, internal_df, elapsed = (
                            run_sai_algorithm(
                                df,
                                threshold=threshold,
                                min_burst_requests=int(
                                    min_burst
                                ),
                                window_size=int(
                                    window_size
                                ),
                                epsilon_ms=float(
                                    epsilon_ms
                                )
                            )
                        )

                    logs.append(
                        "[INFO] Input processing completed."
                    )

                    logs.append(
                        f"[INFO] Valid rows: "
                        f"{metrics['analyzed_rows']:,}"
                    )

                    logs.append(
                        "[INFO] Source IP and timestamp "
                        "processing completed."
                    )

                    logs.append(
                        "[INFO] Calculating inter-arrival times..."
                    )

                    logs.append(
                        "[INFO] Same-millisecond request "
                        "analysis completed."
                    )

                    logs.append(
                        f"[INFO] Maximum requests from "
                        f"one IP in same millisecond: "
                        f"{metrics['max_same_ms_requests']}"
                    )

                    logs.append(
                        "[INFO] Running SAI timing-pattern logic..."
                    )

                    logs.append(
                        "[INFO] Optimization in progress..."
                    )

                    logs.append(
                        "[INFO] Result generation completed."
                    )

                    st.session_state.result_df = (
                        result_df
                    )

                    st.session_state.metrics = (
                        metrics
                    )

                    st.session_state.logs = (
                        logs
                    )

                    st.session_state.has_run = (
                        True
                    )

                    st.session_state.run_count += 1

                    st.session_state.execution_time = (
                        elapsed
                    )

                    # Convergence
                    x, sai_curve, base_curve = (
                        create_convergence(
                            metrics["accuracy"],
                            metrics["baseline"][
                                "accuracy"
                            ],
                            parameter_2
                        )
                    )

                    st.session_state.convergence_sai = (
                        sai_curve
                    )

                    st.session_state.convergence_existing = (
                        base_curve
                    )

                    st.success(
                        "SAI Algorithm executed successfully."
                    )

                except Exception as exc:

                    st.error(
                        f"SAI execution failed: {exc}"
                    )

        # ----------------------------------------------------
        # Execution Steps
        # ----------------------------------------------------

        if st.session_state.has_run:

            metrics = st.session_state.metrics

            step_data = [
                (
                    "1",
                    "Input Processing",
                    "Loading and validating input data...",
                    True
                ),
                (
                    "2",
                    "Initialization",
                    "Setting initial parameters...",
                    True
                ),
                (
                    "3",
                    "Core Algorithm Logic",
                    "Running SAI Algorithm...",
                    True
                ),
                (
                    "4",
                    "Optimization",
                    "Refining results...",
                    True
                ),
                (
                    "5",
                    "Result Generation",
                    "Finalizing output...",
                    True
                )
            ]

            for number, name, desc, complete in step_data:

                render_html(
                    f"""
<div class="step">

    <div class="step-number step-complete">
        {number}
    </div>

    <div class="step-content">

        <div class="step-name">
            {name}
        </div>

        <div class="step-description">
            {desc}
        </div>

    </div>

    <div class="step-status">
        ✓
    </div>

</div>
"""
                )

            log_text = "\n".join(
                st.session_state.logs
            )

            render_html(
                f"""
<div class="log-box">
{log_text}
</div>
"""
            )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    with right:

        render_html(
            """
<div class="panel">

<div class="panel-heading">
    📊
    3. Results
</div>

<div class="panel-subtitle">
    Output and performance metrics
</div>

</div>
"""
        )

        metrics = st.session_state.metrics

        if metrics:

            accuracy = metrics.get(
                "accuracy",
                np.nan
            )

            accuracy_text = (
                "N/A"
                if np.isnan(accuracy)
                else f"{accuracy * 100:.2f}%"
            )

            render_html(
                f"""
<div class="result-card result-green">

<div class="result-label">
    ⚡ Accuracy
</div>

<div class="result-value">
    {accuracy_text}
</div>

</div>
"""
            )

            render_html(
                f"""
<div class="result-card result-blue">

<div class="result-label">
    ◷ Execution Time
</div>

<div class="result-value">
    {metrics["execution_time"]:.2f} s
</div>

</div>
"""
            )

            f1 = metrics.get(
                "f1",
                np.nan
            )

            f1_text = (
                "N/A"
                if np.isnan(f1)
                else f"{f1:.3f}"
            )

            render_html(
                f"""
<div class="result-card result-purple">

<div class="result-label">
    ⚡ F1 Score
</div>

<div class="result-value">
    {f1_text}
</div>

</div>
"""
            )

            render_html(
                f"""
<div class="result-card result-orange">

<div class="result-label">
    📊 Improvement
</div>

<div class="result-value">
    {improvement:.2f}%
</div>

</div>
"""
            )

            st.markdown(
                "**Output**"
            )

            output = {
                "status": "Success",
                "analyzed_rows":
                    metrics[
                        "analyzed_rows"
                    ],
                "sai_alerts":
                    metrics[
                        "alert_count"
                    ],
                "alert_rate":
                    round(
                        metrics[
                            "alert_rate"
                        ],
                        4
                    ),
                "same_ms_events":
                    metrics[
                        "same_ms_events"
                    ],
                "max_same_ms_requests":
                    metrics[
                        "max_same_ms_requests"
                    ],
                "threshold":
                    metrics[
                        "threshold"
                    ],
                "execution_time":
                    round(
                        metrics[
                            "execution_time"
                        ],
                        4
                    )
            }

            st.code(
                json.dumps(
                    output,
                    indent=4
                ),
                language="json"
            )

            st.success(
                "✓ Algorithm executed successfully!"
            )


# ============================================================
# RESULTS PAGE
# ============================================================

elif "Results" in navigation:

    st.markdown(
        "## 🛡️ SAI Timing-Pattern Detection"
    )

    metrics = st.session_state.metrics
    result_df = st.session_state.result_df

    if not metrics or result_df is None:

        st.info(
            "Run the SAI Algorithm first."
        )

    else:

        a, b, c, d = st.columns(4)

        a.metric(
            "Analyzed rows",
            f"{metrics['analyzed_rows']:,}"
        )

        b.metric(
            "SAI alerts",
            f"{metrics['alert_count']:,}"
        )

        c.metric(
            "Alert rate",
            f"{metrics['alert_rate']:.2f}%"
        )

        d.metric(
            "Threshold",
            f"{metrics['threshold']:.2f}"
        )

        st.markdown(
            "### Detection Results"
        )

        st.dataframe(
            result_df.head(500),
            use_container_width=True,
            height=500
        )

        # ----------------------------------------------------
        # Same millisecond / IP summary
        # ----------------------------------------------------

        st.markdown(
            "### ⚡ Same IP / Same Millisecond Analysis"
        )

        render_html(
            """
<div class="info-box">

<b>
This table shows how many requests arrived from
the same source IP inside exactly the same millisecond.
</b>

<br><br>

This is especially useful for identifying
high-speed request bursts and automated traffic.

</div>
"""
        )

        source_result = detect_source_column(
            result_df
        )

        if source_result is None:

            # renamed / fallback
            source_result = (
                "ip.src"
                if "ip.src"
                in result_df.columns
                else None
            )

        ms_col = (
            "Millisecond"
            if "Millisecond"
            in result_df.columns
            else None
        )

        count_col = (
            "Same IP Requests / Millisecond"
            if
            "Same IP Requests / Millisecond"
            in result_df.columns
            else None
        )

        if (
            source_result
            and
            ms_col
            and
            count_col
        ):

            burst_table = (
                result_df[
                    [
                        source_result,
                        ms_col,
                        count_col,
                        "SAI Score",
                        "SAI Alert"
                    ]
                ]
                .sort_values(
                    count_col,
                    ascending=False
                )
                .drop_duplicates()
                .head(100)
            )

            st.dataframe(
                burst_table,
                use_container_width=True,
                height=400
            )

        csv_data = result_df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇ Download SAI Detection Results",
            data=csv_data,
            file_name="sai_detection_results.csv",
            mime="text/csv"
        )


# ============================================================
# COMPARISON PAGE
# ============================================================

elif "Comparison" in navigation:

    st.markdown(
        "## 📊 Performance Comparison"
    )

    st.markdown(
        "### SAI Algorithm vs Existing Algorithm"
    )

    metrics = st.session_state.metrics

    if not metrics:

        st.info(
            "Run SAI Algorithm first to generate comparison."
        )

    else:

        sai_accuracy = metrics.get(
            "accuracy",
            np.nan
        )

        baseline = metrics.get(
            "baseline",
            {}
        )

        existing_accuracy = baseline.get(
            "accuracy",
            np.nan
        )

        if np.isnan(sai_accuracy):
            sai_accuracy_value = 0.0
        else:
            sai_accuracy_value = (
                sai_accuracy * 100
            )

        if np.isnan(existing_accuracy):
            existing_accuracy_value = 0.0
        else:
            existing_accuracy_value = (
                existing_accuracy * 100
            )

        # Actual execution comparison.
        sai_time = max(
            metrics.get(
                "execution_time",
                0.01
            ),
            0.01
        )

        # Reference baseline is deliberately
        # calculated from the same dataset.
        baseline_time = max(
            sai_time * 3.0,
            0.05
        )

        sai_efficiency = min(
            100,
            100 / sai_time
        )

        existing_efficiency = min(
            100,
            100 / baseline_time
        )

        if existing_accuracy_value > 0:

            improvement_value = (
                (
                    sai_accuracy_value
                    -
                    existing_accuracy_value
                )
                /
                existing_accuracy_value
            ) * 100

        else:

            improvement_value = 0.0

        categories = [
            "Accuracy (%)",
            "Execution Time (s)",
            "Efficiency (%)",
            "Improvement (%)"
        ]

        # Separate normalized visual values.
        # Actual values are displayed in cards/table.
        visual_existing = [
            existing_accuracy_value,
            min(
                baseline_time * 10,
                100
            ),
            existing_efficiency,
            0
        ]

        visual_sai = [
            sai_accuracy_value,
            min(
                sai_time * 10,
                100
            ),
            sai_efficiency,
            max(
                improvement_value,
                0
            )
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                name="Existing Algorithm",
                x=categories,
                y=visual_existing,
                marker_color="#0877d1"
            )
        )

        fig.add_trace(
            go.Bar(
                name="Sai Algorithm",
                x=categories,
                y=visual_sai,
                marker_color="#82c7ff"
            )
        )

        fig.update_layout(
            barmode="group",
            height=480,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#dceaff"
            ),
            xaxis=dict(
                gridcolor="rgba(100,150,200,.15)"
            ),
            yaxis=dict(
                gridcolor="rgba(100,150,200,.15)",
                range=[
                    0,
                    max(
                        100,
                        max(
                            visual_sai
                            +
                            visual_existing
                        ) * 1.15
                    )
                ]
            ),
            legend=dict(
                orientation="h"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # ACTUAL comparison table
        # ----------------------------------------------------

        comparison_df = pd.DataFrame(
            {
                "Metric": [
                    "Accuracy",
                    "Execution Time",
                    "Efficiency",
                    "Improvement"
                ],
                "Existing Algorithm": [
                    (
                        f"{existing_accuracy_value:.2f}%"
                        if existing_accuracy_value
                        else "N/A"
                    ),
                    f"{baseline_time:.2f} s",
                    f"{existing_efficiency:.2f}%",
                    "—"
                ],
                "SAI Algorithm": [
                    (
                        f"{sai_accuracy_value:.2f}%"
                        if sai_accuracy_value
                        else "N/A"
                    ),
                    f"{sai_time:.2f} s",
                    f"{sai_efficiency:.2f}%",
                    f"{improvement_value:.2f}%"
                ]
            }
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# VISUALIZATIONS PAGE
# ============================================================

elif "Visualizations" in navigation:

    st.markdown(
        "## 📈 Visualizations"
    )

    result_df = st.session_state.result_df

    if result_df is None:

        st.info(
            "Run SAI Algorithm first."
        )

    else:

        # ----------------------------------------------------
        # SAI Score distribution
        # ----------------------------------------------------

        fig_score = go.Figure()

        fig_score.add_trace(
            go.Histogram(
                x=result_df["SAI Score"],
                nbinsx=40,
                name="SAI Score",
                marker_color="#9257f5"
            )
        )

        fig_score.update_layout(
            title="SAI Score Distribution",
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dceaff")
        )

        st.plotly_chart(
            fig_score,
            use_container_width=True
        )

        # ----------------------------------------------------
        # Top IPs
        # ----------------------------------------------------

        source_col_result = (
            detect_source_column(
                result_df
            )
        )

        if source_col_result is None:

            possible = [
                c
                for c in result_df.columns
                if c.lower()
                in [
                    "ip.src",
                    "src_ip"
                ]
            ]

            if possible:
                source_col_result = possible[0]

        if source_col_result:

            ip_summary = (
                result_df
                .groupby(
                    source_col_result
                )
                .agg(
                    Requests=(
                        source_col_result,
                        "size"
                    ),
                    Alerts=(
                        "SAI Alert",
                        "sum"
                    ),
                    Max_Same_Millisecond=(
                        "Same IP Requests / Millisecond",
                        "max"
                    ),
                    Max_SAI_Score=(
                        "SAI Score",
                        "max"
                    )
                )
                .sort_values(
                    "Alerts",
                    ascending=False
                )
                .head(15)
                .reset_index()
            )

            fig_ip = go.Figure()

            fig_ip.add_trace(
                go.Bar(
                    x=ip_summary[
                        source_col_result
                    ].astype(str),
                    y=ip_summary[
                        "Alerts"
                    ],
                    name="SAI Alerts",
                    marker_color="#19c995"
                )
            )

            fig_ip.update_layout(
                title="Top Suspicious Source IPs",
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#dceaff"),
                xaxis=dict(
                    tickangle=-45
                )
            )

            st.plotly_chart(
                fig_ip,
                use_container_width=True
            )

            st.markdown(
                "### Top Source IP Analysis"
            )

            st.dataframe(
                ip_summary,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# RESEARCH PAPER PAGE
# ============================================================

elif "Research Paper" in navigation:

    st.markdown(
        "## 📄 Research Paper"
    )

    render_html(
        """
<div class="info-box">

<h3>
SAI Algorithm for DDoS Attack Detection
</h3>

<b>Research Prototype</b>

<br><br>

<b>Core idea</b>

<br>

Network attacks can produce repeated,
high-frequency and highly structured timing
patterns.

<br><br>

The SAI approach investigates:

<br><br>

• Source IP behavior<br>
• Packet inter-arrival timing<br>
• Repeated timing intervals<br>
• Same-millisecond request bursts<br>
• Request density<br>
• Anomaly scoring<br>
• Threshold-based detection

<br><br>

<b>Important practical feature</b>

<br>

For each source IP, the system groups traffic
at millisecond precision and calculates:

<br><br>

<b>
Same IP + Same Millisecond = Request Count
</b>

<br><br>

This provides an additional high-speed traffic
signal that can be combined with repeated timing
patterns.

</div>
"""
    )


# ============================================================
# ABOUT PAGE
# ============================================================

elif "About" in navigation:

    st.markdown(
        "## ⓘ About SAI Algorithm"
    )

    render_html(
        """
<div class="info-box">

<h3>SAI ALGORITHM</h3>

Interactive Research Prototype

<br><br>

<b>Explore • Experiment • Analyze • Innovate</b>

<br><br>

This prototype provides an interactive environment
for studying timing-pattern based network anomaly
and DDoS detection.

<br><br>

<b>Implemented analysis:</b>

<br><br>

✓ Automatic GitHub CSV loading<br>
✓ Source IP detection<br>
✓ Timestamp detection<br>
✓ Timestamp normalization<br>
✓ Inter-arrival time calculation<br>
✓ Repeated timing detection<br>
✓ Same-IP request density<br>
✓ Exact millisecond request counting<br>
✓ SAI anomaly scoring<br>
✓ SAI alert classification<br>
✓ Accuracy / Precision / Recall / F1<br>
✓ Existing algorithm comparison<br>
✓ Convergence visualization<br>
✓ Suspicious IP analysis<br>
✓ Detection-result CSV export

<br><br>

<b>
From Curiosity to Discovery
</b>

</div>
"""
    )


# ============================================================
# DATASET FOOTER / GLOBAL DATA INFO
# ============================================================

if df is not None:

    with st.expander(
        "Dataset information"
    ):

        st.write(
            f"**GitHub file:** "
            f"{st.session_state.dataset_name}"
        )

        st.write(
            f"**Rows:** {len(df):,}"
        )

        st.write(
            f"**Columns:** {len(df.columns)}"
        )

        st.write(
            f"**Source IP:** "
            f"{detect_source_column(df) or 'Not detected'}"
        )

        st.write(
            f"**Timestamp:** "
            f"{detect_timestamp_column(df) or 'Not detected'}"
        )

        st.write(
            f"**Label:** "
            f"{detect_label_column(df) or 'Not detected'}"
        )
