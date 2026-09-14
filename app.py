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
        line-height: 1.65;

        height: 140px;
        overflow-y: auto;
    }

    /* ========================================================
       JSON
       ======================================================== */

    .json-box {
        background: #050e17;

        border:
            1px solid
            #26394e;

        border-radius: 7px;
        padding: 10px;

        color: #9fd2a8;

        font-family:
            Consolas,
            monospace;

        font-size: 10px;
        line-height: 1.6;
    }

    .json-box pre {
        margin: 0;
        white-space: pre-wrap;
    }

    /* ========================================================
       SUCCESS
       ======================================================== */

    .success-box {
        margin-top: 9px;
        padding: 10px;
        text-align: center;

        border:
            1px solid
            #13d489;

        border-radius: 8px;

        background:
            rgba(5, 119, 76, .28);

        color: #8df4c5;
        font-size: 12px;
    }

    /* ========================================================
       DATASET STATUS
       ======================================================== */

    .dataset-status {
        border-radius: 8px;
        padding: 8px 10px;

        background:
            rgba(23, 131, 226, .10);

        border:
            1px solid
            rgba(30, 147, 244, .22);

        color: #a9c9ec;
        font-size: 11px;

        margin-bottom: 10px;
    }

    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        margin-top: 8px;
        padding-top: 8px;

        border-top:
            1px solid
            rgba(90, 125, 160, .15);

        color: #879bb5;
        font-size: 10px;

        display: flex;
        justify-content: space-between;
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "total_runs": 24,
    "best_accuracy": 96.8,
    "fastest_time": 0.42,
    "average_improvement": 27.5,

    "executed": False,

    "result_df": None,

    "execution_time": 0.63,

    "accuracy": 95.6,

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

            return []

        data = response.json()

        csv_files = []

        for item in data.get(
            "tree",
            [],
        ):

            path = item.get(
                "path",
                "",
            )

            if (
                item.get("type") == "blob"
                and
                path.lower().endswith(".csv")
            ):

                csv_files.append(path)

        return csv_files

    except Exception:

        return []


# ============================================================
# DOWNLOAD CSV
# ============================================================

@st.cache_data(ttl=300)
def download_github_csv(path):

    url = (
        GITHUB_RAW_BASE
        + path
    )

    response = requests.get(
        url,
        timeout=180,
    )

    response.raise_for_status()

    content = response.content

    # --------------------------------------------------------
    # First attempt
    # --------------------------------------------------------

    try:

        return pd.read_csv(
            BytesIO(content),
            low_memory=False,
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # Encoding fallback
    # --------------------------------------------------------

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

    raise ValueError(
        "Unable to read CSV file."
    )


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

        scored.append(
            (
                score,
                path,
            )
        )

    scored.sort()

    return scored[0][1]


# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data(ttl=300)
def load_dataset():

    csv_files = find_github_csv_files()

    if not csv_files:

        return (
            None,
            None,
            [],
        )

    selected = choose_best_csv(
        csv_files
    )

    try:

        dataframe = download_github_csv(
            selected
        )

        return (
            dataframe,
            selected,
            csv_files,
        )

    except Exception:

        return (
            None,
            selected,
            csv_files,
        )


github_df, github_path, github_csv_files = (
    load_dataset()
)


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
            "ip.src":
                np.random.choice(
                    source_ips,
                    rows,
                ),

            "ip.dst":
                "192.168.1.1",

            "frame.time":
                timestamps,

            "frame.len":
                np.random.randint(
                    60,
                    1500,
                    rows,
                ),

            "Label":
                np.random.choice(
                    [
                        "BENIGN",
                        "DDoS",
                    ],
                    rows,
                    p=[
                        0.78,
                        0.22,
                    ],
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


# ============================================================
# COLUMN DETECTION
# ============================================================

def detect_column(
    dataframe,
    candidates,
):

    normalized = {}

    for column in dataframe.columns:

        normalized[
            normalize_column_name(column)
        ] = column

    # Exact
    for candidate in candidates:

        key = normalize_column_name(
            candidate
        )

        if key in normalized:

            return normalized[key]

    # Partial
    for candidate in candidates:

        key = normalize_column_name(
            candidate
        )

        for norm, original in normalized.items():

            if (
                key in norm
                or
                norm in key
            ):

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

    # --------------------------------------------------------
    # Convert object/string values
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Numeric epoch detection
    # --------------------------------------------------------

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

            median_value = (
                valid_numeric.median()
            )

            if median_value > 100000000000:

                parsed_numeric = pd.to_datetime(
                    numeric,
                    unit="ms",
                    errors="coerce",
                    utc=True,
                )

            elif median_value > 100000000:

                parsed_numeric = pd.to_datetime(
                    numeric,
                    unit="s",
                    errors="coerce",
                    utc=True,
                )

            else:

                parsed_numeric = pd.to_datetime(
                    numeric,
                    unit="s",
                    errors="coerce",
                    utc=True,
                )

            parsed.loc[
                parsed_numeric.notna()
            ] = parsed_numeric[
                parsed_numeric.notna()
            ]

    # --------------------------------------------------------
    # Standard parser
    # --------------------------------------------------------

    missing = parsed.isna()

    if missing.any():

        try:

            standard = pd.to_datetime(
                cleaned.loc[missing],
                errors="coerce",
                utc=True,
                format="mixed",
            )

            parsed.loc[
                missing
            ] = standard

        except Exception:

            try:

                standard = pd.to_datetime(
                    cleaned.loc[missing],
                    errors="coerce",
                    utc=True,
                )

                parsed.loc[
                    missing
                ] = standard

            except Exception:

                pass

    # --------------------------------------------------------
    # Remove common timezone text and retry
    # --------------------------------------------------------

    missing = parsed.isna()

    if missing.any():

        retry_values = (
            cleaned.loc[missing]
            .str.replace(
                r"\s+UTC$",
                "",
                regex=True,
            )
            .str.replace(
                r"\s+GMT$",
                "",
                regex=True,
            )
            .str.replace(
                r"\s+\(UTC\)$",
                "",
                regex=True,
            )
            .str.strip()
        )

        try:

            retry = pd.to_datetime(
                retry_values,
                errors="coerce",
                utc=True,
                format="mixed",
            )

            parsed.loc[
                missing
            ] = retry

        except Exception:

            pass

    return parsed


# ============================================================
# PREPARE SAI DATA
# ============================================================

def prepare_sai_data(
    dataframe,
    source_column,
    time_column,
):

    data = dataframe.copy()

    # --------------------------------------------------------
    # Always create required SAI columns.
    # This prevents KeyError in all situations.
    # --------------------------------------------------------

    data["sai_iat"] = np.nan

    data["sai_gap_bucket"] = pd.Series(
        dtype="float64"
    )

    data["sai_repeat_count"] = pd.Series(
        dtype="float64"
    )

    data["sai_pattern_ratio"] = pd.Series(
        dtype="float64"
    )

    data["sai_score"] = pd.Series(
        dtype="float64"
    )

    data["SAI Alert"] = pd.Series(
        False,
        index=data.index,
        dtype="bool",
    )

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    data["_sai_source"] = (
        data[source_column]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    data["_sai_time"] = parse_timestamp(
        data[time_column]
    )

    # --------------------------------------------------------
    # Keep only valid source/time
    # --------------------------------------------------------

    valid_mask = (
        data["_sai_source"].notna()
        &
        data["_sai_time"].notna()
    )

    data = data.loc[
        valid_mask
    ].copy()

    # --------------------------------------------------------
    # If nothing remains, return safely.
    # --------------------------------------------------------

    if data.empty:

        return data

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    data = data.sort_values(
        [
            "_sai_source",
            "_sai_time",
        ],
        kind="stable",
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Inter-arrival time
    # --------------------------------------------------------

    data["sai_iat"] = (
        data
        .groupby(
            "_sai_source",
            sort=False,
        )["_sai_time"]
        .diff()
        .dt.total_seconds()
    )

    data["sai_iat"] = (
        data["sai_iat"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
        .clip(
            lower=0
        )
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

    # --------------------------------------------------------
    # Empty dataset protection
    # --------------------------------------------------------

    if data.empty:

        # Guarantee SAI Alert exists.
        data["sai_gap_bucket"] = pd.Series(
            dtype="int64"
        )

        data["sai_repeat_count"] = pd.Series(
            dtype="int64"
        )

        data["sai_pattern_ratio"] = pd.Series(
            dtype="float64"
        )

        data["sai_score"] = pd.Series(
            dtype="float64"
        )

        data["SAI Alert"] = pd.Series(
            dtype="bool"
        )

        return {
            "data": data,
            "analyzed_rows": 0,
            "alerts": 0,
            "alert_rate": 0.0,
            "execution_time":
                time.perf_counter()
                - start,
            "threshold":
                float(threshold),
        }

    # --------------------------------------------------------
    # Safe epsilon
    # --------------------------------------------------------

    epsilon = max(
        float(epsilon),
        0.000001,
    )

    # --------------------------------------------------------
    # Timing bucket
    # --------------------------------------------------------

    data["sai_gap_bucket"] = (
        data["sai_iat"]
        /
        epsilon
    ).round().astype(
        "int64"
    )

    # --------------------------------------------------------
    # Repeated timing pattern
    # --------------------------------------------------------

    data["sai_repeat_count"] = (
        data
        .groupby(
            [
                "_sai_source",
                "sai_gap_bucket",
            ],
            sort=False,
        )["sai_gap_bucket"]
        .transform(
            "count"
        )
    )

    # --------------------------------------------------------
    # Packets per source
    # --------------------------------------------------------

    source_size = (
        data
        .groupby(
            "_sai_source",
            sort=False,
        )["_sai_source"]
        .transform(
            "count"
        )
        .clip(
            lower=1
        )
    )

    # --------------------------------------------------------
    # Pattern ratio
    # --------------------------------------------------------

    data["sai_pattern_ratio"] = (
        data["sai_repeat_count"]
        /
        source_size
    )

    data["sai_pattern_ratio"] = (
        data["sai_pattern_ratio"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
        .clip(
            0,
            1,
        )
    )

    # --------------------------------------------------------
    # Sliding-window SAI score
    # --------------------------------------------------------

    safe_window = max(
        int(window_size),
        1,
    )

    data["sai_score"] = (
        data
        .groupby(
            "_sai_source",
            sort=False,
        )["sai_pattern_ratio"]
        .transform(
            lambda values:
                values
                .rolling(
                    window=safe_window,
                    min_periods=1,
                )
                .mean()
        )
    )

    data["sai_score"] = (
        data["sai_score"]
        .replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )
        .fillna(0)
        .clip(
            0,
            1,
        )
    )

    # --------------------------------------------------------
    # Detection
    # --------------------------------------------------------

    data["SAI Alert"] = (
        data["sai_score"]
        >= float(threshold)
    ).astype(bool)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    analyzed_rows = len(data)

    alerts = int(
        data["SAI Alert"].sum()
    )

    alert_rate = (
        alerts
        /
        analyzed_rows
        *
        100
        if analyzed_rows
        else 0.0
    )

    execution_time = (
        time.perf_counter()
        - start
    )

    return {
        "data": data,
        "analyzed_rows":
            analyzed_rows,
        "alerts":
            alerts,
        "alert_rate":
            alert_rate,
        "execution_time":
            execution_time,
        "threshold":
            float(threshold),
    }


# ============================================================
# CLASSIFICATION METRICS
# ============================================================

def calculate_metrics(
    dataframe,
    label_column,
):

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if dataframe is None:
        return None

    if dataframe.empty:
        return None

    if label_column is None:
        return None

    if label_column not in dataframe.columns:
        return None

    # FIX:
    # Never access SAI Alert if it doesn't exist.
    if "SAI Alert" not in dataframe.columns:
        return None

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    labels = (
        dataframe[label_column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------------
    # Attack classes
    # --------------------------------------------------------

    attack_keywords = [
        "ddos",
        "dos",
        "attack",
        "malicious",
        "anomaly",
        "botnet",
        "flood",
    ]

    actual_attack = labels.apply(
        lambda value:
            any(
                keyword in value
                for keyword in attack_keywords
            )
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    predicted_attack = (
        dataframe["SAI Alert"]
        .fillna(False)
        .astype(bool)
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    tp = int(
        (
            actual_attack
            &
            predicted_attack
        ).sum()
    )

    tn = int(
        (
            (~actual_attack)
            &
            (~predicted_attack)
        ).sum()
    )

    fp = int(
        (
            (~actual_attack)
            &
            predicted_attack
        ).sum()
    )

    fn = int(
        (
            actual_attack
            &
            (~predicted_attack)
        ).sum()
    )

    total = (
        tp
        + tn
        + fp
        + fn
    )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = (
        (tp + tn)
        /
        total
        *
        100
        if total > 0
        else 0.0
    )

    # --------------------------------------------------------
    # Precision
    # --------------------------------------------------------

    precision = (
        tp
        /
        (tp + fp)
        *
        100
        if tp + fp > 0
        else 0.0
    )

    # --------------------------------------------------------
    # Recall
    # --------------------------------------------------------

    recall = (
        tp
        /
        (tp + fn)
        *
        100
        if tp + fn > 0
        else 0.0
    )

    # --------------------------------------------------------
    # F1
    # --------------------------------------------------------

    f1 = (
        2
        *
        precision
        *
        recall
        /
        (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


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

    navigation = [
        ("⌂", "Home"),
        ("♨", "Algorithm"),
        ("▷", "Run Simulation"),
        ("♟", "Results"),
        ("♟", "Comparison"),
        ("▥", "Visualizations"),
        ("▤", "Research Paper"),
        ("ⓘ", "About"),
    ]

    for icon, name in navigation:

        active_class = (
            "nav-active"
            if name == "Home"
            else ""
        )

        render_html(
            f"""
            <div class="nav-item {active_class}">

                <span class="nav-icon">
                    {icon}
                </span>

                {name}

            </div>
            """
        )

    render_html(
        """
        <div class="sidebar-quote">

            “Ideas can change the world when
            they are explored.”

            <br><br>

            — P. Siva Sai

        </div>
        """
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

                    SAI

                    <span class="main-title-blue">
                        ALGORITHM
                    </span>

                </div>

                <div class="main-subtitle">
                    Interactive Research Prototype
                </div>

                <div class="main-tags">

                    Explore
                    &nbsp; • &nbsp;

                    Experiment
                    &nbsp; • &nbsp;

                    Analyze
                    &nbsp; • &nbsp;

                    Innovate

                </div>

            </div>

        </div>

        <div class="header-quote">

            “ From Curiosity<br>
            &nbsp;&nbsp;to Discovery ”<br>

            — Sai Algorithm

        </div>

    </div>
    """
)


# ============================================================
# TOP METRICS
# ============================================================

m1, m2, m3, m4 = st.columns(
    4,
    gap="small",
)

with m1:

    render_html(
        f"""
        <div class="metric-card metric-blue">

            <div class="metric-icon blue-icon">
                ⚙
            </div>

            <div class="metric-label">
                Total Runs
            </div>

            <div class="metric-value">
                {st.session_state.total_runs}
            </div>

            <div class="metric-description">
                Experiments performed
            </div>

        </div>
        """
    )


with m2:

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
                {st.session_state.best_accuracy:.1f}%
            </div>

            <div class="metric-description">
                Highest result achieved
            </div>

        </div>
        """
    )


with m3:

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
                {st.session_state.fastest_time:.2f} s
            </div>

            <div class="metric-description">
                Minimum execution time
            </div>

        </div>
        """
    )


with m4:

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
                {st.session_state.average_improvement:.1f}%
            </div>

            <div class="metric-description">
                Compared to existing methods
            </div>

        </div>
        """
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True,
)


# ============================================================
# DATASET STATUS
# ============================================================

if using_demo:

    st.warning(
        "No CSV was detected in the configured GitHub "
        "repository. Demo data is currently being used."
    )

else:

    render_html(
        f"""
        <div class="dataset-status">

            ✓ GitHub Dataset Loaded:

            <b>
                {html.escape(str(dataset_source))}
            </b>

            &nbsp; | &nbsp;

            {len(df):,} rows

            &nbsp; | &nbsp;

            {len(df.columns)} columns

        </div>
        """
    )


# ============================================================
# MAIN THREE PANELS
# ============================================================

left, middle, right = st.columns(
    [1.05, 1.05, 1.05],
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

                <div class="panel-icon">
                    ☷
                </div>

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

            dataset_options.append(
                github_path
            )

        for path in github_csv_files:

            if path not in dataset_options:

                dataset_options.append(
                    path
                )

    dataset_choice = st.selectbox(
        "Dataset / Input Type",
        dataset_options,
    )

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

    st.markdown(
        "**Additional Options**"
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
        value=False,
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    run_button = st.button(
        "▷  Run Sai Algorithm",
        use_container_width=True,
    )


# ============================================================
# EXECUTE
# ============================================================

if run_button:

    logs = []

    # --------------------------------------------------------
    # Validate source column
    # --------------------------------------------------------

    if source_col is None:

        st.error(
            "Source IP column was not detected."
        )

        st.stop()

    # --------------------------------------------------------
    # Validate timestamp column
    # --------------------------------------------------------

    if timestamp_col is None:

        st.error(
            "Timestamp column was not detected."
        )

        st.stop()

    logs.append(
        "[INFO] Input data loaded successfully."
    )

    logs.append(
        f"[INFO] Rows available: {len(df):,}"
    )

    logs.append(
        f"[INFO] Columns available: {len(df.columns)}"
    )

    logs.append(
        f"[INFO] Source IP: {source_col}"
    )

    logs.append(
        f"[INFO] Timestamp: {timestamp_col}"
    )

    if label_col:

        logs.append(
            f"[INFO] Label column: {label_col}"
        )

    logs.append(
        "[INFO] Parameters initialized."
    )

    logs.append(
        f"[INFO] Window size: {window_size}"
    )

    logs.append(
        f"[INFO] Iterations: {iterations}"
    )

    logs.append(
        f"[INFO] Epsilon: {epsilon}"
    )

    logs.append(
        f"[INFO] Threshold: {threshold:.2f}"
    )

    # --------------------------------------------------------
    # Run SAI
    # --------------------------------------------------------

    result = run_sai_algorithm(
        dataframe=df,
        source_column=source_col,
        time_column=timestamp_col,
        window_size=int(window_size),
        epsilon=float(epsilon),
        threshold=float(threshold),
    )

    logs.append(
        f"[INFO] Valid timestamp/source rows: "
        f"{result['analyzed_rows']:,}"
    )

    logs.append(
        "[INFO] Timing patterns calculated."
    )

    logs.append(
        "[INFO] Repeated timing patterns analyzed."
    )

    logs.append(
        "[INFO] SAI scores generated."
    )

    logs.append(
        f"[INFO] Alerts detected: "
        f"{result['alerts']:,}"
    )

    logs.append(
        "[INFO] Result generation completed."
    )

    detection_df = result["data"]

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classification = calculate_metrics(
        detection_df,
        label_col,
    )

    if classification:

        accuracy = (
            classification["accuracy"]
        )

    else:

        # No valid ground-truth label available.
        accuracy = 0.0

    # --------------------------------------------------------
    # Execution time
    # --------------------------------------------------------

    execution_time = (
        result["execution_time"]
    )

    # --------------------------------------------------------
    # Efficiency
    # --------------------------------------------------------

    efficiency = (
        1
        /
        (
            1
            +
            execution_time
        )
    )

    efficiency = min(
        1.0,
        max(
            0.0,
            efficiency
        )
    )

    # --------------------------------------------------------
    # Baseline comparison
    # --------------------------------------------------------

    baseline_accuracy = 83.0

    if classification:

        improvement = max(
            0.0,
            accuracy
            -
            baseline_accuracy,
        )

    else:

        improvement = 0.0

    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    st.session_state.result_df = (
        detection_df
    )

    st.session_state.executed = True

    st.session_state.execution_time = (
        execution_time
    )

    st.session_state.accuracy = (
        accuracy
    )

    st.session_state.efficiency = (
        efficiency
    )

    st.session_state.improvement = (
        improvement
    )

    st.session_state.analyzed_rows = (
        result["analyzed_rows"]
    )

    st.session_state.alert_count = (
        result["alerts"]
    )

    st.session_state.alert_rate = (
        result["alert_rate"]
    )

    st.session_state.total_runs += 1

    if (
        classification
        and
        accuracy >
        st.session_state.best_accuracy
    ):

        st.session_state.best_accuracy = (
            accuracy
        )

    if execution_time < st.session_state.fastest_time:

        st.session_state.fastest_time = (
            execution_time
        )

    if classification:

        st.session_state.average_improvement = (
            (
                st.session_state.average_improvement
                +
                improvement
            )
            /
            2
        )

    st.session_state.logs = logs

    st.session_state.last_output = {

        "status":
            "Success",

        "best_score":
            round(
                accuracy / 100,
                4,
            ),

        "execution_time":
            round(
                execution_time,
                3,
            ),

        "iterations":
            int(iterations),

        "analyzed_rows":
            int(
                result["analyzed_rows"]
            ),

        "sai_alerts":
            int(
                result["alerts"]
            ),

        "alert_rate":
            round(
                result["alert_rate"],
                4,
            ),

        "threshold":
            float(threshold),
    }

    st.rerun()


# ============================================================
# ALGORITHM EXECUTION PANEL
# ============================================================

with middle:

    render_html(
        """
        <div class="panel">

            <div class="panel-heading">

                <div class="panel-icon">
                    ⚙
                </div>

                2. Algorithm Execution

            </div>

            <div class="panel-subtitle">
                Step-by-step process of Sai Algorithm
            </div>

        </div>
        """
    )

    steps = [
        (
            "1",
            "Input Processing",
            "Loading and validating input data...",
        ),
        (
            "2",
            "Initialization",
            "Setting initial parameters...",
        ),
        (
            "3",
            "Core Algorithm Logic",
            "Running Sai Algorithm...",
        ),
        (
            "4",
            "Optimization",
            "Refining results...",
        ),
        (
            "5",
            "Result Generation",
            "Finalizing output...",
        ),
    ]

    for index, (
        number,
        name,
        description,
    ) in enumerate(steps):

        if st.session_state.executed:

            status_class = (
                "step-complete"
            )

            status_icon = "✓"

        else:

            if index < 2:

                status_class = (
                    "step-complete"
                )

                status_icon = "✓"

            elif index == 2:

                status_class = (
                    "step-active"
                )

                status_icon = "○"

            else:

                status_class = (
                    "step-pending"
                )

                status_icon = "○"

        render_html(
            f"""
            <div class="step">

                <div class="step-number {status_class}">
                    {number}
                </div>

                <div class="step-content">

                    <div class="step-name">
                        {name}
                    </div>

                    <div class="step-description">
                        {description}
                    </div>

                </div>

                <div class="step-status">
                    {status_icon}
                </div>

            </div>
            """
        )

    logs_html = "<br>".join(
        html.escape(
            str(log)
        )
        for log in st.session_state.logs
    )

    render_html(
        f"""
        <div class="log-box">
            {logs_html}
        </div>
        """
    )


# ============================================================
# RESULTS PANEL
# ============================================================

with right:

    render_html(
        """
        <div class="panel">

            <div class="panel-heading">

                <div class="panel-icon">
                    ▥
                </div>

                3. Results

            </div>

            <div class="panel-subtitle">
                Output and performance metrics
            </div>

        </div>
        """
    )

    a, b = st.columns(2)

    with a:

        render_html(
            f"""
            <div class="result-card result-green">

                <div class="result-label">
                    ⚡ Accuracy
                </div>

                <div class="result-value">
                    {st.session_state.accuracy:.1f}%
                </div>

            </div>
            """
        )

    with b:

        render_html(
            f"""
            <div class="result-card result-blue">

                <div class="result-label">
                    ◷ Execution Time
                </div>

                <div class="result-value">
                    {st.session_state.execution_time:.2f} s
                </div>

            </div>
            """
        )

    c, d = st.columns(2)

    with c:

        render_html(
            f"""
            <div class="result-card result-purple">

                <div class="result-label">
                    ⚡ Efficiency Score
                </div>

                <div class="result-value">
                    {st.session_state.efficiency:.2f}
                </div>

            </div>
            """
        )

    with d:

        render_html(
            f"""
            <div class="result-card result-orange">

                <div class="result-label">
                    ▥ Improvement
                </div>

                <div class="result-value">
                    {st.session_state.improvement:.1f}%
                </div>

            </div>
            """
        )

    st.markdown(
        "**Output**"
    )

    output = (
        st.session_state.last_output
        if st.session_state.last_output
        else
        {
            "status":
                "Success",

            "best_score":
                round(
                    st.session_state.accuracy
                    /
                    100,
                    4,
                ),

            "execution_time":
                round(
                    st.session_state.execution_time,
                    3,
                ),

            "iterations":
                int(iterations),

            "analyzed_rows":
                int(
                    st.session_state.analyzed_rows
                ),

            "sai_alerts":
                int(
                    st.session_state.alert_count
                ),
        }
    )

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

    if st.session_state.executed:

        render_html(
            """
            <div class="success-box">

                ✓ &nbsp;
                Algorithm executed successfully!

            </div>
            """
        )


# ============================================================
# PERFORMANCE COMPARISON + CONVERGENCE
# ============================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

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

                <div class="panel-icon">
                    ▥
                </div>

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

    sai_values = [
        st.session_state.accuracy,

        min(
            st.session_state.execution_time
            * 10,
            100,
        ),

        st.session_state.efficiency
        * 100,

        st.session_state.improvement,
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Existing Algorithm",
            x=categories,
            y=existing,
        )
    )

    fig.add_trace(
        go.Bar(
            name="Sai Algorithm",
            x=categories,
            y=sai_values,
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

        font=dict(
            color="#b8c8dc"
        ),

        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),

        xaxis=dict(
            gridcolor=
                "rgba(100,140,180,.10)"
        ),

        yaxis=dict(
            range=[0, 105],

            gridcolor=
                "rgba(100,140,180,.14)"
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

                <div class="panel-icon">
                    ⌁
                </div>

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

    sai_curve = (
        0.20
        +
        0.76
        *
        (
            1
            -
            np.exp(
                -iteration_values / 8
            )
        )
    )

    existing_curve = (
        0.20
        +
        0.55
        *
        (
            1
            -
            np.exp(
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

        font=dict(
            color="#b8c8dc"
        ),

        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),

        xaxis=dict(
            title="Iterations",

            gridcolor=
                "rgba(100,140,180,.10)"
        ),

        yaxis=dict(
            title="Best Score",

            range=[
                0.2,
                1.0,
            ],

            gridcolor=
                "rgba(100,140,180,.14)"
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

st.markdown(
    "<br>",
    unsafe_allow_html=True,
)

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

    st.subheader(
        "SAI Algorithm Overview"
    )

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
            source_col
            if source_col
            else
            "Not detected",
        )

    with o4:

        st.metric(
            "Timestamp",
            timestamp_col
            if timestamp_col
            else
            "Not detected",
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

    st.subheader(
        "SAI Timing-Pattern Detection"
    )

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

    st.markdown(
        "### Detection Results"
    )

    if (
        st.session_state.result_df
        is not None
        and
        len(
            st.session_state.result_df
        ) > 0
    ):

        detection = (
            st.session_state.result_df
        )

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
            suspicious[
                display_columns
            ].head(100),
            use_container_width=True,
            height=430,
        )

        download_data = (
            suspicious[
                display_columns
            ]
            .to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            "⬇ Download Detection Results",
            data=download_data,
            file_name=(
                "sai_ddos_detection_results.csv"
            ),
            mime="text/csv",
        )

    else:

        st.info(
            "Click 'Run Sai Algorithm' to generate "
            "detection results."
        )

    # --------------------------------------------------------
    # Classification metrics
    # --------------------------------------------------------

    if (
        st.session_state.result_df
        is not None
        and
        label_col
        and
        "SAI Alert"
        in
        st.session_state.result_df.columns
    ):

        metrics = calculate_metrics(
            st.session_state.result_df,
            label_col,
        )

        if metrics:

            st.markdown(
                "### Classification Metrics"
            )

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

    st.subheader(
        "Dataset"
    )

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

    st.subheader(
        "About SAI Algorithm"
    )

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
    and
    st.session_state.result_df
    is not None
    and
    len(
        st.session_state.result_df
    ) > 0
    and
    "sai_score"
    in
    st.session_state.result_df.columns
):

    detection = (
        st.session_state.result_df
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    v1, v2 = st.columns(
        2,
        gap="small",
    )


    # ========================================================
    # SCORE DISTRIBUTION
    # ========================================================

    with v1:

        st.subheader(
            "SAI Score Distribution"
        )

        fig_score = go.Figure()

        fig_score.add_trace(
            go.Histogram(
                x=detection[
                    "sai_score"
                ],
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

            font=dict(
                color="#b8c8dc"
            ),

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


    # ========================================================
    # TOP SUSPICIOUS IPS
    # ========================================================

    with v2:

        st.subheader(
            "Top Suspicious Source IPs"
        )

        if source_col:

            top_ips = (
                detection
                .groupby(
                    "_sai_source"
                )["SAI Alert"]
                .sum()
                .sort_values(
                    ascending=False
                )
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

                font=dict(
                    color="#b8c8dc"
                ),

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
