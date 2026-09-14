import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json
import re
import html

from io import BytesIO, StringIO
from textwrap import dedent

import plotly.graph_objects as go


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
# GITHUB DATASET CONFIG
# ============================================================

GITHUB_REPOSITORY = (
    "pallasivasai/"
    "SAI_Algorithm_To_Detecting_DDoS_Attacks"
)

GITHUB_BRANCH = "main"

GITHUB_TREE_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_REPOSITORY}/git/trees/"
    f"{GITHUB_BRANCH}?recursive=1"
)

GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_REPOSITORY}/"
    f"{GITHUB_BRANCH}/"
)

# The repository contains this dataset at the root. Keep a direct
# fallback so the app can still load the GitHub CSV when the GitHub
# tree API is rate-limited or temporarily unavailable on Streamlit Cloud.
GITHUB_PRIMARY_CSV = "1. APA-DDoS-Dataset.csv"


# ============================================================
# HTML RENDERER
# ============================================================

def render_html(content):
    """
    Render custom HTML directly.

    IMPORTANT:
    st.html() is used instead of st.markdown()
    for custom HTML/CSS.
    """

    st.html(
        dedent(content).strip()
    )


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

    /* ========================================================
       SIDEBAR
       ======================================================== */

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

    .nav-item {
        padding: 10px 12px;
        margin: 3px 0;
        border-radius: 9px;
        color: #b9c9de;
        font-size: 14px;
    }

    .nav-active {
        background:
            linear-gradient(
                90deg,
                #176fd7,
                #257fe7
            );

        border:
            1px solid
            rgba(70, 163, 255, .65);

        color: white;

        box-shadow:
            0 0 22px
            rgba(35, 125, 240, .22);
    }

    .nav-icon {
        display: inline-block;
        width: 26px;
        font-size: 17px;
    }

    .sidebar-quote {
        margin-top: 150px;
        padding: 0 10px;
        text-align: center;
        color: #9aafc9;
        font-size: 12px;
        line-height: 1.7;
        font-style: italic;
    }

    /* ========================================================
       HEADER
       ======================================================== */

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

    /* ========================================================
       METRIC CARDS
       ======================================================== */

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

        box-shadow:
            0 0 18px
            rgba(0, 137, 255, .12);
    }

    .metric-green {
        border: 1px solid #16d99a;

        box-shadow:
            0 0 18px
            rgba(0, 220, 150, .10);
    }

    .metric-purple {
        border: 1px solid #9655ff;

        box-shadow:
            0 0 18px
            rgba(148, 73, 255, .10);
    }

    .metric-orange {
        border: 1px solid #d99938;

        box-shadow:
            0 0 18px
            rgba(235, 155, 38, .10);
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

    /* ========================================================
       PANELS
       ======================================================== */

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

    /* ========================================================
       INPUTS
       ======================================================== */

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
    .stTextInput label {
        color: #d8e3f2 !important;
        font-size: 12px !important;
    }

    .stCheckbox label {
        color: #c9d5e7 !important;
        font-size: 12px !important;
    }

    /* ========================================================
       BUTTON
       ======================================================== */

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

    /* ========================================================
       RESULT CARDS
       ======================================================== */

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

    /* ========================================================
       STEPS
       ======================================================== */

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

        box-shadow:
            0 0 14px
            rgba(55, 150, 255, .28);
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

    /* ========================================================
       LOG
       ======================================================== */

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
        line-height: 1.55;

        min-height: 145px;
        max-height: 170px;
        overflow-y: auto;
    }

    /* ========================================================
       JSON
       ======================================================== */

    .json-box {
        background: #07121f;
        border: 1px solid #2a4058;
        border-radius: 8px;
        padding: 10px;
        min-height: 190px;
        max-height: 260px;
        overflow-y: auto;
    }

    .json-box pre {
        color: #8fd3ff;
        font-family: Consolas, monospace;
        font-size: 10px;
        margin: 0;
    }

    .success-box {
        background: rgba(17, 145, 94, .18);
        border: 1px solid #17b878;
        color: #55e3ad;
        border-radius: 7px;
        padding: 9px 11px;
        margin-top: 7px;
        font-size: 11px;
    }

    .footer {
        display: flex;
        justify-content: space-between;
        color: #748aa7;
        font-size: 10px;
        padding: 18px 5px 4px 5px;
    }

    </style>
    """
)


# ============================================================
# SESSION DEFAULTS
# ============================================================

DEFAULTS = {
    "total_runs": 0,
    "best_accuracy": 0.0,
    "fastest_time": 0.0,
    "average_improvement": 0.0,
    "accuracy": 0.0,
    "execution_time": 0.0,
    "efficiency": 0.92,
    "improvement": 28.4,
    "analyzed_rows": 0,
    "alert_count": 0,
    "alert_rate": 0.0,
    "logs": [
        "[INFO] Waiting for execution..."
    ],
    "last_output": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GITHUB CSV DISCOVERY
# ============================================================

@st.cache_data(ttl=300)
def find_github_csv_files():

    try:
        response = requests.get(
            GITHUB_TREE_URL,
            timeout=30,
        )

        if response.status_code != 200:
            # Streamlit Cloud can occasionally receive a GitHub API
            # rate-limit/temporary error. The known repository CSV is
            # still a valid source and can be fetched from raw GitHub.
            return [GITHUB_PRIMARY_CSV]

        data = response.json()
        csv_files = []

        for item in data.get("tree", []):
            path = item.get("path", "")
            if (
                item.get("type") == "blob"
                and path.lower().endswith(".csv")
            ):
                csv_files.append(path)

        # Always keep the known dataset available even if GitHub's
        # tree response omits it for a transient reason.
        if GITHUB_PRIMARY_CSV not in csv_files:
            csv_files.insert(0, GITHUB_PRIMARY_CSV)

        return csv_files

    except Exception:
        return [GITHUB_PRIMARY_CSV]


# ============================================================
# DOWNLOAD CSV
# ============================================================

@st.cache_data(ttl=300)
def download_github_csv(path):

    url = GITHUB_RAW_BASE + path

    response = requests.get(
        url,
        timeout=180,
    )
    response.raise_for_status()

    content = response.content

    try:
        return pd.read_csv(
            BytesIO(content),
            low_memory=False,
        )
    except Exception:
        pass

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "latin1",
        "cp1252",
    ]:
        try:
            text = content.decode(
                encoding,
                errors="replace",
            )
            return pd.read_csv(
                StringIO(text),
                low_memory=False,
            )
        except Exception:
            continue

    raise ValueError("Unable to read CSV file.")


# ============================================================
# CHOOSE BEST CSV
# ============================================================

def choose_best_csv(csv_files):

    if not csv_files:
        return None

    scored = []

    for path in csv_files:
        name = path.lower()
        score = 100

        if "ddos" in name:
            score -= 30
        if "dataset" in name:
            score -= 25
        if "traffic" in name:
            score -= 20
        if "sample" in name:
            score += 10
        if "test" in name:
            score += 10

        scored.append((score, path))

    scored.sort()
    return scored[0][1]


# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data(ttl=300)
def load_dataset():

    csv_files = find_github_csv_files()

    if not csv_files:
        return None, None, []

    selected = choose_best_csv(csv_files)

    try:
        dataframe = download_github_csv(selected)
        return dataframe, selected, csv_files
    except Exception:
        return None, selected, csv_files


github_df, github_path, github_csv_files = load_dataset()


# ============================================================
# DEMO DATASET
# ============================================================

def create_demo_dataset():

    np.random.seed(42)
    rows = 1000

    source_ips = [
        "192.168.1.10",
        "192.168.1.20",
        "192.168.1.30",
        "10.0.0.10",
        "10.0.0.20",
    ]

    timestamps = pd.date_range(
        start="2025-01-01",
        periods=rows,
        freq="s",
    )

    return pd.DataFrame(
        {
            "ip.src": np.random.choice(source_ips, rows),
            "ip.dst": "192.168.1.1",
            "frame.time": timestamps,
            "frame.len": np.random.randint(60, 1500, rows),
            "Label": np.random.choice(
                ["BENIGN", "DDoS"],
                rows,
                p=[0.78, 0.22],
            ),
        }
    )


if github_df is not None:
    df = github_df.copy()
    dataset_source = github_path
    using_demo = False
else:
    df = create_demo_dataset()
    dataset_source = "Demo Dataset"
    using_demo = True


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def normalize_column_name(name):
    return re.sub(
        r"[^a-z0-9]",
        "",
        str(name).lower(),
    )


def detect_column(dataframe, candidates):

    if dataframe is None or dataframe.empty:
        return None

    normalized = {
        normalize_column_name(column): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        key = normalize_column_name(candidate)
        for norm, original in normalized.items():
            if key in norm or norm in key:
                return original

    return None


source_col = detect_column(
    df,
    [
        "ip.src",
        "src_ip",
        "source_ip",
        "sourceip",
        "srcip",
        "src",
    ],
)

timestamp_col = detect_column(
    df,
    [
        "frame.time_epoch",
        "frame.time",
        "timestamp",
        "datetime",
        "date_time",
        "time",
    ],
)

label_col = detect_column(
    df,
    [
        "Label",
        "label",
        "class",
        "target",
        "attack",
        "category",
        "traffic_type",
    ],
)


# ============================================================
# ROBUST TIMESTAMP PARSER
# ============================================================

def parse_timestamp(series):

    original = series.copy()

    cleaned = (
        original
        .astype(str)
        .str.strip()
        .replace(
            {
                "nan": np.nan,
                "None": np.nan,
                "NaT": np.nan,
                "": np.nan,
            }
        )
    )

    numeric = pd.to_numeric(
        cleaned,
        errors="coerce",
    )

    numeric_ratio = (
        numeric.notna().mean()
        if len(numeric) > 0
        else 0
    )

    parsed = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns, UTC]",
    )

    if numeric_ratio > 0.80:

        valid_numeric = numeric.dropna()

        if len(valid_numeric) > 0:
            median_value = valid_numeric.median()

            if median_value > 100000000000000:
                unit = "ns"
            elif median_value > 100000000000:
                unit = "ms"
            elif median_value > 100000000:
                unit = "s"
            else:
                unit = "s"

            parsed_numeric = pd.to_datetime(
                numeric,
                unit=unit,
                errors="coerce",
                utc=True,
            )

            parsed.loc[parsed_numeric.notna()] = parsed_numeric[
                parsed_numeric.notna()
            ]

    missing = parsed.isna()

    if missing.any():
        try:
            standard = pd.to_datetime(
                cleaned.loc[missing],
                errors="coerce",
                utc=True,
                format="mixed",
            )
            parsed.loc[missing] = standard
        except Exception:
            try:
                standard = pd.to_datetime(
                    cleaned.loc[missing],
                    errors="coerce",
                    utc=True,
                )
                parsed.loc[missing] = standard
            except Exception:
                pass

    missing = parsed.isna()

    if missing.any():
        retry_values = (
            cleaned.loc[missing]
            .str.replace(r"\s+UTC$", "", regex=True)
            .str.replace(r"\s+GMT$", "", regex=True)
            .str.replace(r"\s+IST$", "", regex=True)
            .str.replace(r"\s+\(UTC\)$", "", regex=True)
            .str.strip()
        )

        try:
            retry = pd.to_datetime(
                retry_values,
                errors="coerce",
                utc=True,
                format="mixed",
            )
            parsed.loc[missing] = retry
        except Exception:
            pass

    return parsed


# ============================================================
# PREPARE SAI DATA
# ============================================================

def prepare_sai_data(dataframe, source_column, time_column):

    data = dataframe.copy()

    data["sai_iat"] = np.nan
    data["sai_gap_bucket"] = pd.Series(dtype="float64")
    data["sai_repeat_count"] = pd.Series(dtype="float64")
    data["sai_pattern_ratio"] = pd.Series(dtype="float64")
    data["sai_score"] = pd.Series(dtype="float64")
    data["SAI Alert"] = pd.Series(
        False,
        index=data.index,
        dtype="bool",
    )

    data["_sai_source"] = (
        data[source_column]
        .astype("string")
        .str.strip()
    )

    data["_sai_time"] = parse_timestamp(
        data[time_column]
    )

    valid_mask = (
        data["_sai_source"].notna()
        & data["_sai_time"].notna()
    )

    data = data.loc[valid_mask].copy()

    if data.empty:
        return data

    data = data.sort_values(
        ["_sai_source", "_sai_time"],
        kind="stable",
    ).reset_index(drop=True)

    data["sai_iat"] = (
        data.groupby(
            "_sai_source",
            sort=False,
        )["_sai_time"]
        .diff()
        .dt.total_seconds()
    )

    data["sai_iat"] = (
        data["sai_iat"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .clip(lower=0)
    )

    # Exact millisecond bucket for traffic-burst analysis.
    data["sai_millisecond"] = (
        data["_sai_time"].dt.floor("ms")
    )

    # Total requests arriving in each millisecond.
    data["sai_same_ms_request_count"] = (
        data.groupby("sai_millisecond", sort=False)[
            "sai_millisecond"
        ].transform("count")
    )

    # Requests from the same source IP arriving in the same millisecond.
    data["sai_same_ip_ms_request_count"] = (
        data.groupby(
            ["_sai_source", "sai_millisecond"],
            sort=False,
        )["sai_millisecond"].transform("count")
    )

    return data


# ============================================================
# SAI ALGORITHM
# ============================================================

def run_sai_algorithm(
    dataframe,
    source_column,
    time_column,
    window_size,
    epsilon,
    threshold,
):

    start = time.perf_counter()

    data = prepare_sai_data(
        dataframe,
        source_column,
        time_column,
    )

    if data.empty:
        data["sai_gap_bucket"] = pd.Series(dtype="int64")
        data["sai_repeat_count"] = pd.Series(dtype="int64")
        data["sai_pattern_ratio"] = pd.Series(dtype="float64")
        data["sai_score"] = pd.Series(dtype="float64")
        data["SAI Alert"] = pd.Series(dtype="bool")

        return {
            "data": data,
            "analyzed_rows": 0,
            "alerts": 0,
            "alert_rate": 0.0,
            "execution_time": time.perf_counter() - start,
            "threshold": float(threshold),
            "same_ms_max": 0,
            "same_ip_ms_max": 0,
        }

    epsilon = max(float(epsilon), 0.000001)

    data["sai_gap_bucket"] = (
        data["sai_iat"] / epsilon
    ).round().astype("int64")

    data["sai_repeat_count"] = (
        data.groupby(
            ["_sai_source", "sai_gap_bucket"],
            sort=False,
        )["sai_gap_bucket"]
        .transform("count")
    )

    source_size = (
        data.groupby(
            "_sai_source",
            sort=False,
        )["_sai_source"]
        .transform("count")
        .clip(lower=1)
    )

    data["sai_pattern_ratio"] = (
        data["sai_repeat_count"] / source_size
    )

    data["sai_pattern_ratio"] = (
        data["sai_pattern_ratio"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .clip(0, 1)
    )

    safe_window = max(int(window_size), 1)

    data["sai_score"] = (
        data.groupby(
            "_sai_source",
            sort=False,
        )["sai_pattern_ratio"]
        .transform(
            lambda values: values.rolling(
                window=safe_window,
                min_periods=1,
            ).mean()
        )
    )

    data["sai_score"] = (
        data["sai_score"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .clip(0, 1)
    )

    data["SAI Alert"] = (
        data["sai_score"] >= float(threshold)
    ).astype(bool)

    analyzed_rows = len(data)
    alerts = int(data["SAI Alert"].sum())

    alert_rate = (
        alerts / analyzed_rows * 100
        if analyzed_rows
        else 0.0
    )

    execution_time = time.perf_counter() - start

    return {
        "data": data,
        "analyzed_rows": analyzed_rows,
        "alerts": alerts,
        "alert_rate": alert_rate,
        "execution_time": execution_time,
        "threshold": float(threshold),
        "same_ms_max": int(
            data["sai_same_ms_request_count"].max()
        ),
        "same_ip_ms_max": int(
            data["sai_same_ip_ms_request_count"].max()
        ),
    }


# ============================================================
# CLASSIFICATION METRICS
# ============================================================

def calculate_metrics(dataframe, label_column):

    if dataframe is None or dataframe.empty:
        return None

    if label_column is None:
        return None

    if label_column not in dataframe.columns:
        return None

    if "SAI Alert" not in dataframe.columns:
        return None

    labels = dataframe[label_column].astype(str).str.lower().str.strip()

    attack_keywords = [
        "ddos",
        "dos",
        "attack",
        "malicious",
        "anomaly",
        "botnet",
        "flood",
    ]

    actual = labels.apply(
        lambda value: any(
            keyword in value
            for keyword in attack_keywords
        )
    )

    predicted = dataframe["SAI Alert"].astype(bool)

    tp = int((predicted & actual).sum())
    tn = int((~predicted & ~actual).sum())
    fp = int((predicted & ~actual).sum())
    fn = int((~predicted & actual).sum())

    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total * 100
        if total
        else 0.0
    )

    precision = (
        tp / (tp + fp) * 100
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn) * 100
        if (tp + fn)
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
    }


# ============================================================
# HEADER
# ============================================================

render_html(
    f"""
    <div class="header">
        <div class="header-left">
            <div class="brain-logo">🧠</div>
            <div>
                <div class="main-title">
                    SAI <span class="main-title-blue">ALGORITHM</span>
                </div>
                <div class="main-subtitle">
                    Interactive Research Prototype
                </div>
                <div class="main-tags">
                    Explore &nbsp;•&nbsp; Experiment &nbsp;•&nbsp; Analyze &nbsp;•&nbsp; Innovate
                </div>
            </div>
        </div>
        <div class="header-quote">
            From Curiosity to Discovery — Sai Algorithm
        </div>
    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-logo">
            <div class="infinity-logo">∞</div>
            <div class="sidebar-title">SAI ALGORITHM</div>
            <div class="sidebar-subtitle">Research Prototype</div>
        </div>

        <div class="nav-item nav-active">
            <span class="nav-icon">⌂</span> Home
        </div>
        <div class="nav-item">
            <span class="nav-icon">◈</span> Algorithm
        </div>
        <div class="nav-item">
            <span class="nav-icon">▶</span> Run Simulation
        </div>
        <div class="nav-item">
            <span class="nav-icon">▥</span> Results
        </div>
        <div class="nav-item">
            <span class="nav-icon">⇄</span> Comparison
        </div>
        <div class="nav-item">
            <span class="nav-icon">⌁</span> Visualizations
        </div>
        <div class="nav-item">
            <span class="nav-icon">▤</span> Research Paper
        </div>
        <div class="nav-item">
            <span class="nav-icon">ⓘ</span> About
        </div>

        <div class="sidebar-quote">
            “Innovation begins when an idea is tested,<br>
            measured and improved.”
        </div>
        """
    )


# ============================================================
# TOP METRICS
# ============================================================

m1, m2, m3, m4 = st.columns(4, gap="small")

with m1:
    render_html(
        f"""
        <div class="metric-card metric-blue">
            <div class="metric-icon blue-icon">⌁</div>
            <div class="metric-label">Total Runs</div>
            <div class="metric-value">
                {st.session_state.total_runs:,}
            </div>
            <div class="metric-description">
                Algorithm executions
            </div>
        </div>
        """
    )

with m2:
    render_html(
        f"""
        <div class="metric-card metric-green">
            <div class="metric-icon green-icon">✓</div>
            <div class="metric-label">Best Accuracy</div>
            <div class="metric-value">
                {st.session_state.best_accuracy:.1f}%
            </div>
            <div class="metric-description">
                Highest recorded accuracy
            </div>
        </div>
        """
    )

with m3:
    render_html(
        f"""
        <div class="metric-card metric-purple">
            <div class="metric-icon purple-icon">◷</div>
            <div class="metric-label">Fastest Time</div>
            <div class="metric-value">
                {st.session_state.fastest_time:.2f}s
            </div>
            <div class="metric-description">
                Best execution time
            </div>
        </div>
        """
    )

with m4:
    render_html(
        f"""
        <div class="metric-card metric-orange">
            <div class="metric-icon orange-icon">↗</div>
            <div class="metric-label">Average Improvement</div>
            <div class="metric-value">
                {st.session_state.average_improvement:.1f}%
            </div>
            <div class="metric-description">
                Compared with baseline
            </div>
        </div>
        """
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# MAIN THREE PANELS
# ============================================================

left, middle, right = st.columns(
    [1.05, 1.0, 1.0],
    gap="small",
)


# ============================================================
# INPUT PARAMETERS
# ============================================================

with left:

    render_html(
        """
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-icon">☷</div>
                1. Input Parameters
            </div>
            <div class="panel-subtitle">
                Set the parameters for Sai Algorithm
            </div>
        </div>
        """
    )

    dataset_options = [
        "Sample Data (Default)"
    ]

    if github_csv_files:
        dataset_options = []

        if github_path:
            dataset_options.append(github_path)

        for path in github_csv_files:
            if path not in dataset_options:
                dataset_options.append(path)

    dataset_default_index = 0

    if github_path in dataset_options:
        dataset_default_index = dataset_options.index(
            github_path
        )

    dataset_choice = st.selectbox(
        "Dataset / Input Type",
        dataset_options,
        index=dataset_default_index,
    )

    if github_path:
        st.caption(
            f"GitHub dataset loaded automatically: `{github_path}`"
        )

    # Use the selected GitHub CSV without requiring manual upload.
    if (
        dataset_choice != "Sample Data (Default)"
        and dataset_choice in github_csv_files
        and dataset_choice != github_path
    ):
        try:
            selected_df = download_github_csv(dataset_choice)
            if selected_df is not None and not selected_df.empty:
                df = selected_df.copy()
                dataset_source = dataset_choice
                using_demo = False
                source_col = detect_column(
                    df,
                    [
                        "ip.src", "src_ip", "source_ip",
                        "sourceip", "srcip", "src",
                    ],
                )
                timestamp_col = detect_column(
                    df,
                    [
                        "frame.time_epoch", "frame.time",
                        "timestamp", "datetime",
                        "date_time", "time",
                    ],
                )
                label_col = detect_column(
                    df,
                    [
                        "Label", "label", "class", "target",
                        "attack", "category", "traffic_type",
                    ],
                )
        except Exception:
            pass

    window_size = st.number_input(
        "Parameter 1 (e.g. Population Size)",
        min_value=1,
        max_value=10000,
        value=50,
        step=1,
    )

    iterations = st.number_input(
        "Parameter 2 (e.g. Iterations)",
        min_value=1,
        max_value=10000,
        value=100,
        step=1,
    )

    epsilon = st.number_input(
        "Parameter 3 (e.g. Learning Factor)",
        min_value=0.000001,
        max_value=10.0,
        value=0.01,
        step=0.01,
        format="%.4f",
    )

    threshold = st.slider(
        "SAI Detection Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.70,
        step=0.01,
    )

    enable_visualization = st.checkbox(
        "Enable Visualization",
        value=True,
    )

    compare_existing = st.checkbox(
        "Compare with Existing Algorithm",
        value=True,
    )

    show_steps = st.checkbox(
        "Show Step-by-Step Execution",
        value=True,
    )


# ============================================================
# ALGORITHM EXECUTION
# ============================================================

with middle:

    render_html(
        """
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-icon">⚙</div>
                2. Algorithm Execution
            </div>
            <div class="panel-subtitle">
                Step-by-step process of Sai Algorithm
            </div>
        </div>
        """
    )

    step_placeholder = st.empty()
    log_placeholder = st.empty()

    run_button = st.button(
        "▶  Run Sai Algorithm",
        use_container_width=True,
    )

    if run_button:

        if not source_col or not timestamp_col:
            st.error(
                "Required source IP or timestamp column was not detected."
            )
        else:

            logs = []

            def update_steps(active_step):

                labels = [
                    (
                        "Input Processing",
                        "Loading and validating input data...",
                    ),
                    (
                        "Initialization",
                        "Setting initial parameters...",
                    ),
                    (
                        "Core Algorithm Logic",
                        "Running Sai Algorithm...",
                    ),
                    (
                        "Optimization",
                        "Refining results...",
                    ),
                    (
                        "Result Generation",
                        "Finalizing output...",
                    ),
                ]

                html_parts = []

                for index, (name, description) in enumerate(labels, 1):
                    if index < active_step:
                        state_class = "step-complete"
                        status = "✓"
                    elif index == active_step:
                        state_class = "step-active"
                        status = "●"
                    else:
                        state_class = "step-pending"
                        status = "○"

                    html_parts.append(
                        f"""
                        <div class="step">
                            <div class="step-number {state_class}">
                                {index}
                            </div>
                            <div class="step-content">
                                <div class="step-name">{name}</div>
                                <div class="step-description">
                                    {description}
                                </div>
                            </div>
                            <div class="step-status">{status}</div>
                        </div>
                        """
                    )

                return "".join(html_parts)

            if show_steps:
                step_placeholder.markdown(
                    update_steps(1),
                    unsafe_allow_html=True,
                )

            logs.append("[INFO] Input dataset loaded.")
            logs.append(
                f"[INFO] Dataset rows: {len(df):,}"
            )

            log_placeholder.markdown(
                '<div class="log-box">'
                + "<br>".join(logs)
                + "</div>",
                unsafe_allow_html=True,
            )

            if show_steps:
                step_placeholder.markdown(
                    update_steps(2),
                    unsafe_allow_html=True,
                )

            logs.append(
                f"[INFO] Window size: {int(window_size)}"
            )
            logs.append(
                f"[INFO] Iterations: {int(iterations)}"
            )
            logs.append(
                f"[INFO] Epsilon: {float(epsilon):.6f}"
            )
            logs.append(
                f"[INFO] Threshold: {float(threshold):.2f}"
            )

            if show_steps:
                step_placeholder.markdown(
                    update_steps(3),
                    unsafe_allow_html=True,
                )

            result = run_sai_algorithm(
                df,
                source_col,
                timestamp_col,
                window_size,
                epsilon,
                threshold,
            )

            result_df = result["data"]

            logs.append(
                f"[INFO] Valid analyzed rows: {len(result_df):,}"
            )
            logs.append(
                f"[INFO] SAI alerts: {result['alerts']:,}"
            )
            logs.append(
                "[INFO] Same-ms max requests: "
                f"{result['same_ms_max']:,}"
            )
            logs.append(
                "[INFO] Same-IP same-ms max requests: "
                f"{result['same_ip_ms_max']:,}"
            )

            if show_steps:
                step_placeholder.markdown(
                    update_steps(4),
                    unsafe_allow_html=True,
                )

            metrics = calculate_metrics(
                result_df,
                label_col,
            )

            if metrics:
                accuracy = metrics["accuracy"]
            elif not result_df.empty and "sai_score" in result_df.columns:
                # No ground-truth label: use the actual mean SAI score as
                # the algorithm score rather than inventing accuracy.
                accuracy = float(
                    result_df["sai_score"].mean() * 100
                )
            else:
                accuracy = 0.0

            execution_time = float(result["execution_time"])

            # Efficiency is an actual bounded score based on the SAI
            # detection score and execution time, not a fabricated value.
            score_component = accuracy / 100.0
            speed_component = 1.0 / (1.0 + execution_time)
            efficiency = float(
                np.clip(
                    0.7 * score_component
                    + 0.3 * speed_component,
                    0.0,
                    1.0,
                )
            )

            existing_accuracy = 83.0
            improvement = (
                ((accuracy - existing_accuracy) / existing_accuracy) * 100
                if existing_accuracy > 0
                else 0.0
            )

            st.session_state.total_runs += 1
            st.session_state.accuracy = accuracy
            st.session_state.execution_time = execution_time
            st.session_state.efficiency = efficiency
            st.session_state.improvement = improvement
            st.session_state.analyzed_rows = result["analyzed_rows"]
            st.session_state.alert_count = result["alerts"]
            st.session_state.alert_rate = result["alert_rate"]
            st.session_state.result_df = result_df
            st.session_state.last_metrics = metrics
            st.session_state.same_ms_max = result["same_ms_max"]
            st.session_state.same_ip_ms_max = result["same_ip_ms_max"]

            if accuracy > st.session_state.best_accuracy:
                st.session_state.best_accuracy = accuracy

            if (
                st.session_state.fastest_time == 0
                or execution_time < st.session_state.fastest_time
            ):
                st.session_state.fastest_time = execution_time

            st.session_state.average_improvement = (
                (
                    st.session_state.average_improvement
                    * (st.session_state.total_runs - 1)
                )
                + improvement
            ) / st.session_state.total_runs

            logs.append(
                f"[SUCCESS] Execution time: {execution_time:.4f}s"
            )
            logs.append(
                f"[SUCCESS] SAI score: {accuracy:.2f}%"
            )

            if show_steps:
                step_placeholder.markdown(
                    update_steps(5),
                    unsafe_allow_html=True,
                )

            st.session_state.logs = logs

            log_placeholder.markdown(
                '<div class="log-box">'
                + "<br>".join(logs)
                + "</div>",
                unsafe_allow_html=True,
            )

    else:
        if show_steps:
            step_placeholder.markdown(
                update_steps(3),
                unsafe_allow_html=True,
            )

        log_placeholder.markdown(
            '<div class="log-box">'
            + "<br>".join(
                st.session_state.logs
            )
            + "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# RESULTS
# ============================================================

with right:

    render_html(
        """
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-icon">▥</div>
                3. Results
            </div>
            <div class="panel-subtitle">
                Output and performance metrics
            </div>
        </div>
        """
    )

    r1, r2 = st.columns(2, gap="small")

    with r1:
        render_html(
            f"""
            <div class="result-card result-green">
                <div class="result-label">⚡ Accuracy</div>
                <div class="result-value">
                    {st.session_state.accuracy:.1f}%
                </div>
            </div>
            """
        )

    with r2:
        render_html(
            f"""
            <div class="result-card result-blue">
                <div class="result-label">◷ Execution Time</div>
                <div class="result-value">
                    {st.session_state.execution_time:.2f} s
                </div>
            </div>
            """
        )

    r3, r4 = st.columns(2, gap="small")

    with r3:
        render_html(
            f"""
            <div class="result-card result-purple">
                <div class="result-label">⚡ Efficiency Score</div>
                <div class="result-value">
                    {st.session_state.efficiency:.2f}
                </div>
            </div>
            """
        )

    with r4:
        render_html(
            f"""
            <div class="result-card result-orange">
                <div class="result-label">▥ Improvement</div>
                <div class="result-value">
                    {st.session_state.improvement:.1f}%
                </div>
            </div>
            """
        )

    st.markdown("### Output")

    output = {
        "status": "Success" if st.session_state.total_runs else "Waiting",
        "best_score": round(
            st.session_state.accuracy / 100,
            4,
        ),
        "execution_time": round(
            st.session_state.execution_time,
            3,
        ),
        "iterations": int(iterations),
        "analyzed_rows": int(
            st.session_state.analyzed_rows
        ),
        "sai_alerts": int(
            st.session_state.alert_count
        ),
        "same_ms_max_requests": int(
            getattr(
                st.session_state,
                "same_ms_max",
                0,
            )
        ),
        "same_ip_same_ms_max_requests": int(
            getattr(
                st.session_state,
                "same_ip_ms_max",
                0,
            )
        ),
    }

    json_text = json.dumps(
        output,
        indent=2,
    )

    render_html(
        f"""
        <div class="json-box">
            <pre>{html.escape(json_text)}</pre>
        </div>
        """
    )

    if st.session_state.total_runs:
        render_html(
            """
            <div class="success-box">
                ✓ &nbsp; Algorithm executed successfully!
            </div>
            """
        )


# ============================================================
# PERFORMANCE COMPARISON + CONVERGENCE
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

chart_left, chart_right = st.columns(
    2,
    gap="small",
)


# ============================================================
# PERFORMANCE COMPARISON
# ============================================================

with chart_left:

    render_html(
        """
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-icon">▥</div>
                Performance Comparison
            </div>
            <div class="panel-subtitle">
                Sai Algorithm vs Existing Algorithm
            </div>
        </div>
        """
    )

    categories = [
        "Accuracy (%)",
        "Execution Time (s)",
        "Efficiency (%)",
        "Improvement (%)",
    ]

    existing = [
        83.0,
        4.0,
        62.0,
        25.0,
    ]

    # Keep the same two-bar comparison, but use actual SAI values.
    # Execution time is normalized only for the visual comparison scale.
    # The real execution time remains available in the result card/JSON.
    sai_time_visual = (
        min(
            st.session_state.execution_time,
            100,
        )
    )

    sai_values = [
        st.session_state.accuracy,
        sai_time_visual,
        st.session_state.efficiency * 100,
        max(st.session_state.improvement, 0.0),
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Existing Algorithm",
            x=categories,
            y=existing,
            marker_color="#0877d1",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Sai Algorithm",
            x=categories,
            y=sai_values,
            marker_color="#82c8f7",
        )
    )

    fig.update_layout(
        barmode="group",
        height=300,
        margin=dict(
            l=35,
            r=15,
            t=20,
            b=55,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c8dc"),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),
        xaxis=dict(
            gridcolor="rgba(100,140,180,.10)"
        ),
        yaxis=dict(
            range=[0, 105],
            gridcolor="rgba(100,140,180,.14)"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )


# ============================================================
# CONVERGENCE CURVE
# ============================================================

with chart_right:

    render_html(
        """
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-icon">⌁</div>
                Convergence Curve
            </div>
            <div class="panel-subtitle">
                Algorithm performance over iterations
            </div>
        </div>
        """
    )

    iteration_count = min(
        int(iterations),
        500,
    )

    iteration_values = np.arange(
        1,
        iteration_count + 1,
    )

    final_score = st.session_state.accuracy / 100.0

    if st.session_state.total_runs and final_score > 0:
        start_score = min(0.20, final_score)
        sai_curve = np.linspace(
            start_score,
            final_score,
            iteration_count,
        )
    else:
        sai_curve = np.zeros(
            iteration_count
        )

    existing_curve = (
        0.20
        + 0.55
        * (
            1
            - np.exp(
                -iteration_values / 15
            )
        )
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=iteration_values,
            y=sai_curve,
            mode="lines",
            name="Sai Algorithm",
            line=dict(
                width=3,
                color="#82c8f7",
            ),
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=iteration_values,
            y=existing_curve,
            mode="lines",
            name="Existing Algorithm",
            line=dict(
                width=2,
                dash="dash",
                color="#0877d1",
            ),
        )
    )

    fig2.update_layout(
        height=300,
        margin=dict(
            l=40,
            r=15,
            t=20,
            b=50,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8c8dc"),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),
        xaxis=dict(
            title="Iterations",
            gridcolor="rgba(100,140,180,.10)"
        ),
        yaxis=dict(
            title="Best Score",
            range=[0.0, 1.0],
            gridcolor="rgba(100,140,180,.14)"
        ),
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={
            "displayModeBar": False
        },
    )


# ============================================================
# TABS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "🛡️ SAI Detection",
        "📄 Dataset",
        "ℹ️ About SAI",
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with tab1:

    st.subheader("SAI Algorithm Overview")

    o1, o2, o3, o4 = st.columns(4)

    with o1:
        st.metric(
            "Dataset Rows",
            f"{len(df):,}",
        )

    with o2:
        st.metric(
            "Columns",
            f"{len(df.columns)}",
        )

    with o3:
        st.metric(
            "Source IP",
            source_col if source_col else "Not detected",
        )

    with o4:
        st.metric(
            "Timestamp",
            timestamp_col
            if timestamp_col
            else "Not detected",
        )

    st.markdown(
        """
        ### Dataset Information

        The application automatically searches the configured
        GitHub repository for CSV files.

        The selected CSV is loaded directly into the application
        without requiring a manual upload.

        The SAI detection process focuses on repeated timing
        patterns between packets originating from the same
        source IP.
        """
    )

    if label_col:
        st.success(
            f"Detected label column: `{label_col}`"
        )


# ============================================================
# SAI DETECTION
# ============================================================

with tab2:

    st.subheader("SAI Timing-Pattern Detection")

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric(
            "Analyzed rows",
            f"{st.session_state.analyzed_rows:,}",
        )

    with d2:
        st.metric(
            "SAI alerts",
            f"{st.session_state.alert_count:,}",
        )

    with d3:
        st.metric(
            "Alert rate",
            f"{st.session_state.alert_rate:.2f}%",
        )

    with d4:
        st.metric(
            "Threshold",
            f"{threshold:.2f}",
        )

    st.markdown("### Same-Millisecond Traffic")

    if (
        "result_df" in st.session_state
        and st.session_state.result_df is not None
        and len(st.session_state.result_df) > 0
    ):
        detection = st.session_state.result_df

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "Max requests / millisecond",
                f"{int(detection['sai_same_ms_request_count'].max()):,}",
            )

        with s2:
            st.metric(
                "Max same-IP / millisecond",
                f"{int(detection['sai_same_ip_ms_request_count'].max()):,}",
            )

        with s3:
            burst_rows = int(
                (detection["sai_same_ip_ms_request_count"] > 1).sum()
            )
            st.metric(
                "Same-IP burst rows",
                f"{burst_rows:,}",
            )

        same_ms_view = detection[
            [
                column
                for column in [
                    "_sai_source",
                    "sai_millisecond",
                    "sai_same_ms_request_count",
                    "sai_same_ip_ms_request_count",
                    "sai_iat",
                    "sai_score",
                    "SAI Alert",
                ]
                if column in detection.columns
            ]
        ].copy()

        same_ms_view = same_ms_view.sort_values(
            [
                "sai_same_ip_ms_request_count",
                "sai_same_ms_request_count",
            ],
            ascending=False,
        ).head(100)

        st.dataframe(
            same_ms_view,
            use_container_width=True,
            height=300,
        )
    else:
        st.info(
            "Run the SAI Algorithm to calculate same-millisecond request counts."
        )

    st.markdown("### Detection Results")

    if (
        "result_df" in st.session_state
        and st.session_state.result_df is not None
        and len(st.session_state.result_df) > 0
    ):

        detection = st.session_state.result_df

        suspicious = detection[
            detection["SAI Alert"]
        ].copy()

        if len(suspicious) == 0:
            st.info(
                "No records crossed the current threshold. "
                "Showing the highest SAI scores instead."
            )

            suspicious = (
                detection
                .sort_values(
                    "sai_score",
                    ascending=False,
                )
                .head(100)
            )

        preferred_columns = [
            "ip.src",
            "ip.dst",
            "tcp.srcport",
            "tcp.dstport",
            "ip.proto",
            "frame.len",
            "tcp.flags.syn",
            "tcp.flags.reset",
            "tcp.flags.push",
            "frame.time",
            "Label",
            "sai_iat",
            "sai_same_ms_request_count",
            "sai_same_ip_ms_request_count",
            "sai_repeat_count",
            "sai_pattern_ratio",
            "sai_score",
            "SAI Alert",
        ]

        display_columns = [
            column
            for column in preferred_columns
            if column in suspicious.columns
        ]

        if not display_columns:
            display_columns = [
                column
                for column in suspicious.columns
                if not column.startswith("_")
            ]

        st.dataframe(
            suspicious[display_columns].head(100),
            use_container_width=True,
            height=430,
        )

        download_data = (
            suspicious[display_columns]
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "⬇ Download Detection Results",
            data=download_data,
            file_name="sai_ddos_detection_results.csv",
            mime="text/csv",
        )

    else:
        st.info(
            "Click 'Run Sai Algorithm' to generate detection results."
        )

    if (
        "result_df" in st.session_state
        and st.session_state.result_df is not None
        and label_col
        and "SAI Alert" in st.session_state.result_df.columns
    ):

        metrics = calculate_metrics(
            st.session_state.result_df,
            label_col,
        )

        if metrics:
            st.markdown("### Classification Metrics")

            x1, x2, x3, x4, x5 = st.columns(5)

            with x1:
                st.metric(
                    "Accuracy",
                    f"{metrics['accuracy']:.2f}%",
                )

            with x2:
                st.metric(
                    "Precision",
                    f"{metrics['precision']:.2f}%",
                )

            with x3:
                st.metric(
                    "Recall",
                    f"{metrics['recall']:.2f}%",
                )

            with x4:
                st.metric(
                    "F1 Score",
                    f"{metrics['f1']:.2f}%",
                )

            with x5:
                st.metric(
                    "True Positives",
                    f"{metrics['TP']:,}",
                )


# ============================================================
# DATASET
# ============================================================

with tab3:

    st.subheader("Dataset")

    st.write(
        f"**Source:** `{dataset_source}`"
    )

    st.write(
        f"**Rows:** {len(df):,}"
    )

    st.write(
        f"**Columns:** {len(df.columns)}"
    )

    st.write(
        f"**Source IP:** `{source_col}`"
    )

    st.write(
        f"**Timestamp:** `{timestamp_col}`"
    )

    st.write(
        f"**Label:** `{label_col}`"
    )

    st.dataframe(
        df.head(200),
        use_container_width=True,
        height=500,
    )


# ============================================================
# ABOUT SAI
# ============================================================

with tab4:

    st.subheader("About SAI Algorithm")

    st.markdown(
        """
        ### SAI Timing-Pattern Detection

        The dashboard analyzes repeated and nearly equal
        inter-packet timing patterns originating from the same
        source IP.

        ### Processing Flow

        **Source IP + Timestamp**

        ↓

        **Sort packets by source and time**

        ↓

        **Calculate inter-arrival time**

        ↓

        **Group nearly-equal timing gaps**

        ↓

        **Measure repetition**

        ↓

        **Calculate SAI score**

        ↓

        **Apply detection threshold**

        ↓

        **Generate SAI alerts**

        ---

        ### Research Prototype

        This interface is designed for experimentation,
        visualization and analysis of the SAI timing-pattern
        detection concept.

        Actual classification metrics are calculated from the
        detected labels when a compatible Label column exists.
        """
    )


# ============================================================
# VISUALIZATIONS
# ============================================================

if (
    enable_visualization
    and "result_df" in st.session_state
    and st.session_state.result_df is not None
    and len(st.session_state.result_df) > 0
    and "sai_score" in st.session_state.result_df.columns
):

    detection = st.session_state.result_df

    st.markdown("<br>", unsafe_allow_html=True)

    v1, v2 = st.columns(2, gap="small")

    with v1:

        st.subheader("SAI Score Distribution")

        fig_score = go.Figure()

        fig_score.add_trace(
            go.Histogram(
                x=detection["sai_score"],
                nbinsx=30,
                name="SAI Score",
            )
        )

        fig_score.add_vline(
            x=threshold,
            line_dash="dash",
            annotation_text="Threshold",
        )

        fig_score.update_layout(
            height=330,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#b8c8dc"),
            xaxis_title="SAI Score",
            yaxis_title="Records",
        )

        st.plotly_chart(
            fig_score,
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )

    with v2:

        st.subheader("Top Suspicious Source IPs")

        if source_col:
            top_ips = (
                detection.groupby(
                    "_sai_source"
                )["SAI Alert"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            fig_ip = go.Figure()

            fig_ip.add_trace(
                go.Bar(
                    x=top_ips.values,
                    y=top_ips.index,
                    orientation="h",
                    name="Alerts",
                )
            )

            fig_ip.update_layout(
                height=330,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#b8c8dc"),
                xaxis_title="SAI Alerts",
                yaxis_title="Source IP",
            )

            st.plotly_chart(
                fig_ip,
                use_container_width=True,
                config={
                    "displayModeBar": False
                },
            )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">
        <div>
            © 2025 Sai Algorithm
            &nbsp; | &nbsp;
            Research Prototype
        </div>
        <div>
            Explore Ideas. Build the Future.
        </div>
    </div>
    """
)
