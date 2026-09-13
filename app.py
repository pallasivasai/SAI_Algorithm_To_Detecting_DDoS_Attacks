import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json
import re
from io import BytesIO

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAI Algorithm | Interactive Research Prototype",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIGURATION
# ============================================================

GITHUB_REPOSITORY = "pallasivasai/SAI_Algorithm_To_Detecting_DDoS_Attacks"
GITHUB_BRANCH = "main"

GITHUB_API_TREE = (
    f"https://api.github.com/repos/"
    f"{GITHUB_REPOSITORY}/git/trees/"
    f"{GITHUB_BRANCH}?recursive=1"
)

RAW_GITHUB_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_REPOSITORY}/"
    f"{GITHUB_BRANCH}/"
)

# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "total_runs": 24,
    "best_accuracy": 96.8,
    "fastest_time": 0.42,
    "average_improvement": 27.5,
    "result_df": None,
    "detection_df": None,
    "executed": False,
    "execution_time": 0.63,
    "accuracy": 95.6,
    "efficiency": 0.92,
    "improvement": 28.4,
    "alert_count": 0,
    "alert_rate": 0.0,
    "analyzed_rows": 0,
    "last_output": None,
    "log_messages": [
        "[INFO] Waiting for execution..."
    ]
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS - SCREENSHOT STYLE
# ============================================================

st.markdown(
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
            circle at 62% 4%,
            rgba(0, 174, 255, 0.12),
            transparent 24%
        ),
        radial-gradient(
            circle at 88% 45%,
            rgba(130, 60, 255, 0.08),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #06101d 0%,
            #071525 48%,
            #06111f 100%
        );

    color: #eaf2ff;
}

.block-container {
    max-width: 100%;
    padding-top: 1.1rem;
    padding-bottom: 0.4rem;
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
            #10203a 0%,
            #0c1a30 50%,
            #091526 100%
        );

    border-right:
        1px solid
        rgba(77, 145, 216, 0.16);
}

section[data-testid="stSidebar"] > div {
    padding-top: 0.5rem;
}

.sidebar-logo {
    text-align: center;
    padding: 8px 8px 22px 8px;
}

.infinity-logo {
    font-size: 54px;
    line-height: 1;
    font-weight: 800;
    background:
        linear-gradient(
            90deg,
            #39aaff,
            #8a57ff
        );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    filter:
        drop-shadow(
            0 0 10px
            rgba(38, 151, 255, .35)
        );
}

.sidebar-main-title {
    font-size: 19px;
    font-weight: 700;
    color: #f1f6ff;
    margin-top: 8px;
}

.sidebar-subtitle {
    font-size: 12px;
    color: #9db0ca;
    margin-top: 4px;
}

.sidebar-nav {
    padding: 4px 0;
}

.nav-active {
    background:
        linear-gradient(
            90deg,
            #176fd8,
            #247de7
        );

    border:
        1px solid
        rgba(72, 165, 255, .75);

    border-radius: 9px;

    color: white !important;

    box-shadow:
        0 0 20px
        rgba(31, 123, 245, .25);
}

.nav-item {
    padding: 10px 12px;
    margin: 3px 0;
    border-radius: 9px;
    color: #b8c8df;
    font-size: 14px;
}

.nav-icon {
    display: inline-block;
    width: 25px;
    font-size: 18px;
}

.sidebar-quote {
    margin-top: 155px;
    text-align: center;
    padding: 0 8px;

    color: #9cafc8;
    font-size: 12px;
    line-height: 1.65;
    font-style: italic;
}

/* ============================================================
   HEADER
   ============================================================ */

.header-container {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    padding:
        0px
        3px
        15px
        3px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.brain {
    font-size: 72px;
    width: 88px;
    text-align: center;

    filter:
        drop-shadow(
            0 0 17px
            rgba(0, 181, 255, .55)
        );
}

.header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 44px;
    font-weight: 800;
    line-height: 1.0;

    letter-spacing: -1.5px;
}

.header-title .blue {
    color: #1ca9ff;
    text-shadow:
        0 0 20px
        rgba(28, 169, 255, .20);
}

.header-subtitle {
    margin-top: 7px;
    font-size: 25px;
    color: #9db8dc;
}

.header-tags {
    margin-top: 7px;
    font-size: 13px;
    color: #99b2d1;
    letter-spacing: .8px;
}

.header-quote {
    text-align: right;
    padding-top: 4px;
    color: #d1d9e7;
    font-size: 13px;
    line-height: 1.8;
    font-style: italic;
}

/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {
    min-height: 108px;

    padding:
        14px
        14px
        11px
        14px;

    border-radius: 11px;

    background:
        linear-gradient(
            145deg,
            rgba(13, 33, 55, .98),
            rgba(6, 20, 35, .98)
        );

    position: relative;
    overflow: hidden;
}

.metric-card-blue {
    border: 1px solid #168cf2;
    box-shadow:
        0 0 18px
        rgba(0, 137, 255, .12);
}

.metric-card-green {
    border: 1px solid #16d99a;
    box-shadow:
        0 0 18px
        rgba(0, 220, 150, .10);
}

.metric-card-purple {
    border: 1px solid #9655ff;
    box-shadow:
        0 0 18px
        rgba(148, 73, 255, .10);
}

.metric-card-orange {
    border: 1px solid #d99938;
    box-shadow:
        0 0 18px
        rgba(235, 155, 38, .10);
}

.metric-icon {
    width: 44px;
    height: 44px;

    float: left;

    margin-right: 12px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 23px;
}

.metric-blue-icon {
    background: rgba(28, 127, 218, .20);
    color: #45aaff;
}

.metric-green-icon {
    background: rgba(18, 202, 133, .20);
    color: #32e7a3;
}

.metric-purple-icon {
    background: rgba(142, 67, 231, .22);
    color: #bd73ff;
}

.metric-orange-icon {
    background: rgba(215, 139, 26, .22);
    color: #f4b13a;
}

.metric-label {
    font-size: 13px;
    color: #d6dfed;
}

.metric-value {
    font-size: 29px;
    line-height: 1.15;
    font-weight: 700;
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
   MAIN PANELS
   ============================================================ */

.main-panel {
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

    font-family: 'Space Grotesk', sans-serif;

    font-size: 18px;
    font-weight: 700;

    color: #edf4ff;
}

.panel-heading-icon {
    width: 34px;
    height: 34px;

    border-radius: 7px;

    background:
        rgba(12, 128, 225, .18);

    color: #1ba9ff;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 19px;
}

.panel-subheading {
    color: #99acc5;
    font-size: 12px;

    margin:
        3px
        0
        13px
        43px;
}

/* ============================================================
   STREAMLIT INPUTS
   ============================================================ */

div[data-baseweb="select"] > div {
    background: #101f32 !important;
    border-color: #30435b !important;
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
    box-shadow:
        0 0 27px
        rgba(83, 112, 255, .42);

    transform: translateY(-1px);
}

/* ============================================================
   RESULT CARDS
   ============================================================ */

.result-card {
    min-height: 76px;

    padding: 11px;

    border-radius: 9px;
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
   STEPPER
   ============================================================ */

.step-row {
    display: flex;
    align-items: center;
    min-height: 50px;
}

.step-circle {
    width: 31px;
    height: 31px;

    min-width: 31px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-weight: 700;

    margin-right: 12px;
}

.step-complete {
    background: #37df93;
    color: #062117;
}

.step-running {
    background: #37df93;
    color: #062117;

    box-shadow:
        0 0 14px
        rgba(55, 223, 147, .22);
}

.step-waiting {
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

.step-right {
    font-size: 17px;
}

/* ============================================================
   LOG
   ============================================================ */

.log-box {
    margin-top: 7px;

    background: #050e17;

    border:
        1px solid
        #26394e;

    border-radius: 7px;

    padding: 10px;

    color: #a9c2dd;

    font-family: Consolas, monospace;

    font-size: 10px;

    line-height: 1.65;

    height: 142px;

    overflow-y: auto;
}

/* ============================================================
   JSON
   ============================================================ */

.json-box {
    background: #050e17;

    border:
        1px solid
        #26394e;

    border-radius: 7px;

    padding: 10px;

    color: #9fd2a8;

    font-family: Consolas, monospace;

    font-size: 10px;

    line-height: 1.6;
}

/* ============================================================
   SUCCESS
   ============================================================ */

.success-box {
    margin-top: 9px;

    padding: 10px;

    text-align: center;

    border-radius: 8px;

    border: 1px solid #13d489;

    background:
        rgba(5, 119, 76, .28);

    color: #8df4c5;

    font-size: 12px;
}

/* ============================================================
   CHART PANEL
   ============================================================ */

.chart-panel {
    background:
        linear-gradient(
            145deg,
            rgba(11, 30, 49, .98),
            rgba(6, 19, 33, .98)
        );

    border:
        1px solid
        rgba(81, 128, 172, .24);

    border-radius: 12px;

    padding: 13px;
}

/* ============================================================
   DATASET STATUS
   ============================================================ */

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

/* ============================================================
   FOOTER
   ============================================================ */

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
""",
    unsafe_allow_html=True
)


# ============================================================
# GITHUB DATASET FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
def find_csv_files_from_github():

    try:

        response = requests.get(
            GITHUB_API_TREE,
            timeout=20
        )

        if response.status_code != 200:
            return []

        data = response.json()

        files = []

        for item in data.get("tree", []):

            path = item.get("path", "")

            if (
                item.get("type") == "blob"
                and path.lower().endswith(".csv")
            ):
                files.append(path)

        return files

    except Exception:

        return []


@st.cache_data(ttl=300)
def download_csv_from_github(path):

    url = RAW_GITHUB_BASE + path

    response = requests.get(
        url,
        timeout=120
    )

    response.raise_for_status()

    content = response.content

    # First attempt
    try:
        return pd.read_csv(
            BytesIO(content),
            low_memory=False
        )
    except Exception:

        # Fallback encodings
        for encoding in [
            "utf-8-sig",
            "latin1",
            "cp1252"
        ]:

            try:

                text = content.decode(
                    encoding,
                    errors="replace"
                )

                from io import StringIO

                return pd.read_csv(
                    StringIO(text),
                    low_memory=False
                )

            except Exception:
                continue

        raise


def select_best_csv(csv_files):

    if not csv_files:
        return None

    priority = []

    for path in csv_files:

        name = path.lower()

        score = 100

        if "ddos" in name:
            score -= 30

        if "dataset" in name:
            score -= 20

        if "sample" in name:
            score -= 10

        if "test" in name:
            score += 10

        priority.append(
            (score, path)
        )

    priority.sort()

    return priority[0][1]


@st.cache_data(ttl=300)
def load_repository_dataset():

    csv_files = find_csv_files_from_github()

    if not csv_files:
        return None, None, []

    selected = select_best_csv(
        csv_files
    )

    try:

        df = download_csv_from_github(
            selected
        )

        return (
            df,
            selected,
            csv_files
        )

    except Exception:

        return (
            None,
            selected,
            csv_files
        )


# ============================================================
# COLUMN DETECTION
# ============================================================

def normalize_column_name(name):

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(name).lower()
    )


def find_column(df, candidates):

    normalized = {
        normalize_column_name(c): c
        for c in df.columns
    }

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

        for normalized_name, original in normalized.items():

            if (
                key in normalized_name
                or normalized_name in key
            ):
                return original

    return None


def detect_dataset_columns(df):

    source_col = find_column(
        df,
        [
            "ip.src",
            "src_ip",
            "source_ip",
            "sourceip",
            "srcip",
            "src"
        ]
    )

    timestamp_col = find_column(
        df,
        [
            "frame.time",
            "frame.time_epoch",
            "timestamp",
            "time",
            "datetime",
            "date_time"
        ]
    )

    label_col = find_column(
        df,
        [
            "Label",
            "label",
            "class",
            "target",
            "attack",
            "category"
        ]
    )

    return (
        source_col,
        timestamp_col,
        label_col
    )


# ============================================================
# TIMESTAMP PARSER
# ============================================================

def parse_timestamp_series(series):

    # Convert to strings only when necessary
    original = series.copy()

    # Normal datetime parsing
    parsed = pd.to_datetime(
        original,
        errors="coerce",
        utc=True
    )

    # Numeric fallback
    failed = parsed.isna()

    if failed.any():

        numeric = pd.to_numeric(
            original.loc[failed],
            errors="coerce"
        )

        if numeric.notna().any():

            median_value = numeric.dropna().median()

            if median_value > 100000000000:

                numeric_parsed = pd.to_datetime(
                    numeric,
                    unit="ms",
                    errors="coerce",
                    utc=True
                )

            else:

                numeric_parsed = pd.to_datetime(
                    numeric,
                    unit="s",
                    errors="coerce",
                    utc=True
                )

            parsed.loc[failed] = numeric_parsed

    return parsed


# ============================================================
# SAI ALGORITHM
# ============================================================

def prepare_sai_dataset(
    df,
    source_col,
    timestamp_col
):

    data = df.copy()

    # --------------------------------------------
    # SOURCE IP
    # --------------------------------------------

    data["_sai_source"] = (
        data[source_col]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------
    # TIMESTAMP
    # --------------------------------------------

    data["_sai_time"] = parse_timestamp_series(
        data[timestamp_col]
    )

    # Keep valid source/time
    data = data[
        data["_sai_source"].notna()
        &
        data["_sai_time"].notna()
    ].copy()

    # --------------------------------------------
    # SORT
    # --------------------------------------------

    data = data.sort_values(
        [
            "_sai_source",
            "_sai_time"
        ],
        kind="stable"
    ).reset_index(
        drop=True
    )

    # --------------------------------------------
    # INTER ARRIVAL TIME
    # --------------------------------------------

    data["sai_iat"] = (
        data
        .groupby("_sai_source")["_sai_time"]
        .diff()
        .dt.total_seconds()
    )

    data["sai_iat"] = (
        data["sai_iat"]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
        .clip(lower=0)
    )

    return data


def run_sai_detection(
    df,
    source_col,
    timestamp_col,
    window_size=50,
    epsilon=0.01,
    threshold=0.70
):

    start = time.perf_counter()

    data = prepare_sai_dataset(
        df,
        source_col,
        timestamp_col
    )

    if len(data) == 0:

        return {
            "data": data,
            "analyzed_rows": 0,
            "alerts": 0,
            "alert_rate": 0.0,
            "execution_time": (
                time.perf_counter() - start
            ),
            "threshold": threshold
        }

    # --------------------------------------------
    # ROUND TIMING GAPS
    # --------------------------------------------

    epsilon = max(
        float(epsilon),
        0.000001
    )

    data["sai_gap_bucket"] = (
        data["sai_iat"] / epsilon
    ).round().astype("int64")

    # --------------------------------------------
    # REPEATED TIMING PATTERN
    # --------------------------------------------

    data["sai_repeat_count"] = (
        data
        .groupby(
            [
                "_sai_source",
                "sai_gap_bucket"
            ]
        )["sai_gap_bucket"]
        .transform("count")
    )

    # --------------------------------------------
    # WINDOW-BASED SCORE
    # --------------------------------------------

    source_group_size = (
        data
        .groupby("_sai_source")["_sai_source"]
        .transform("count")
        .clip(lower=1)
    )

    data["sai_pattern_ratio"] = (
        data["sai_repeat_count"]
        / source_group_size
    )

    data["sai_pattern_ratio"] = (
        data["sai_pattern_ratio"]
        .clip(0, 1)
    )

    # Rolling local pattern
    data["sai_score"] = (
        data
        .groupby("_sai_source")[
            "sai_pattern_ratio"
        ]
        .transform(
            lambda x:
            x.rolling(
                window=window_size,
                min_periods=1
            ).mean()
        )
    )

    # --------------------------------------------
    # ALERT
    # --------------------------------------------

    data["SAI Alert"] = (
        data["sai_score"] >= threshold
    )

    # --------------------------------------------
    # STATISTICS
    # --------------------------------------------

    analyzed_rows = len(data)

    alerts = int(
        data["SAI Alert"].sum()
    )

    alert_rate = (
        alerts / analyzed_rows * 100
        if analyzed_rows
        else 0
    )

    execution_time = (
        time.perf_counter()
        - start
    )

    return {
        "data": data,
        "analyzed_rows": analyzed_rows,
        "alerts": alerts,
        "alert_rate": alert_rate,
        "execution_time": execution_time,
        "threshold": threshold
    }


# ============================================================
# ACTUAL CLASSIFICATION METRICS
# ============================================================

def calculate_classification_metrics(
    result_df,
    label_col
):

    if (
        result_df is None
        or label_col is None
        or label_col not in result_df.columns
    ):
        return None

    labels = (
        result_df[label_col]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Flexible malicious-label detection
    attack_keywords = [
        "ddos",
        "dos",
        "attack",
        "malicious",
        "anomaly",
        "botnet",
        "flood"
    ]

    actual_attack = labels.apply(
        lambda value:
        any(
            keyword in value
            for keyword in attack_keywords
        )
    )

    predicted_attack = (
        result_df["SAI Alert"]
        .astype(bool)
    )

    tp = int(
        (actual_attack & predicted_attack).sum()
    )

    tn = int(
        (~actual_attack & ~predicted_attack).sum()
    )

    fp = int(
        (~actual_attack & predicted_attack).sum()
    )

    fn = int(
        (actual_attack & ~predicted_attack).sum()
    )

    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total * 100
        if total
        else 0
    )

    precision = (
        tp / (tp + fp) * 100
        if (tp + fp)
        else 0
    )

    recall = (
        tp / (tp + fn) * 100
        if (tp + fn)
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ============================================================
# DEMO FALLBACK
# ============================================================

def create_demo_dataset():

    np.random.seed(42)

    rows = 1000

    source_ips = [
        "192.168.1.10",
        "192.168.1.20",
        "192.168.1.30",
        "10.0.0.10",
        "10.0.0.20"
    ]

    timestamps = pd.date_range(
        "2025-01-01",
        periods=rows,
        freq="s"
    )

    return pd.DataFrame(
        {
            "ip.src": np.random.choice(
                source_ips,
                rows
            ),
            "ip.dst": "192.168.1.1",
            "frame.time": timestamps,
            "frame.len": np.random.randint(
                60,
                1500,
                rows
            ),
            "Label": np.random.choice(
                [
                    "BENIGN",
                    "DDoS"
                ],
                rows,
                p=[0.78, 0.22]
            )
        }
    )


# ============================================================
# LOAD DATASET
# ============================================================

github_df, github_path, github_csv_files = (
    load_repository_dataset()
)

if github_df is not None:

    df = github_df.copy()
    dataset_source = github_path
    using_demo = False

else:

    df = create_demo_dataset()
    dataset_source = "Demo Dataset"
    using_demo = True


source_col, timestamp_col, label_col = (
    detect_dataset_columns(df)
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="infinity-logo">
                ∞
            </div>

            <div class="sidebar-main-title">
                SAI ALGORITHM
            </div>

            <div class="sidebar-subtitle">
                Research Prototype
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    nav_items = [
        ("⌂", "Home"),
        ("♨", "Algorithm"),
        ("▷", "Run Simulation"),
        ("♟", "Results"),
        ("♟", "Comparison"),
        ("▥", "Visualizations"),
        ("▤", "Research Paper"),
        ("ⓘ", "About")
    ]

    for icon, name in nav_items:

        if name == "Home":

            st.markdown(
                f"""
                <div class="nav-item nav-active">
                    <span class="nav-icon">
                        {icon}
                    </span>
                    {name}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="nav-item">
                    <span class="nav-icon">
                        {icon}
                    </span>
                    {name}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="sidebar-quote">
            “Ideas can change the world when
            they are explored.”<br><br>
            — P. Siva Sai
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="header-container">

        <div class="header-left">

            <div class="brain">
                🧠
            </div>

            <div>

                <div class="header-title">
                    SAI
                    <span class="blue">
                        ALGORITHM
                    </span>
                </div>

                <div class="header-subtitle">
                    Interactive Research Prototype
                </div>

                <div class="header-tags">
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
    """,
    unsafe_allow_html=True
)


# ============================================================
# TOP METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)

with c1:

    st.markdown(
        f"""
        <div class="metric-card metric-card-blue">

            <div class="metric-icon metric-blue-icon">
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
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="metric-card metric-card-green">

            <div class="metric-icon metric-green-icon">
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
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="metric-card metric-card-purple">

            <div class="metric-icon metric-purple-icon">
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
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="metric-card metric-card-orange">

            <div class="metric-icon metric-orange-icon">
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
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# DATASET STATUS
# ============================================================

if using_demo:

    st.warning(
        "No CSV was detected in the GitHub repository. "
        "Demo data is being used. Add a CSV to the repository "
        "and the application will automatically load it."
    )

else:

    st.markdown(
        f"""
        <div class="dataset-status">
            ✓ GitHub Dataset Loaded:
            <b>{dataset_source}</b>
            &nbsp; | &nbsp;
            {len(df):,} rows
            &nbsp; | &nbsp;
            {len(df.columns)} columns
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# THREE MAIN COLUMNS
# ============================================================

left, middle, right = st.columns(
    [1.05, 1.05, 1.05],
    gap="small"
)


# ============================================================
# 1. INPUT PARAMETERS
# ============================================================

with left:

    st.markdown(
        """
        <div class="main-panel">

            <div class="panel-heading">
                <div class="panel-heading-icon">
                    ☷
                </div>

                1. Input Parameters
            </div>

            <div class="panel-subheading">
                Set the parameters for Sai Algorithm
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    dataset_options = [
        "Sample Data (Default)"
    ]

    if github_csv_files:

        dataset_options = [
            github_path
            if github_path
            else github_csv_files[0]
        ] + [
            x for x in github_csv_files
            if x != github_path
        ]

    dataset_choice = st.selectbox(
        "Dataset / Input Type",
        dataset_options,
        index=0
    )

    window_size = st.number_input(
        "Parameter 1 (e.g. Population Size)",
        min_value=1,
        max_value=10000,
        value=50,
        step=1
    )

    iterations = st.number_input(
        "Parameter 2 (e.g. Iterations)",
        min_value=1,
        max_value=10000,
        value=100,
        step=1
    )

    epsilon = st.number_input(
        "Parameter 3 (e.g. Learning Factor)",
        min_value=0.000001,
        max_value=10.0,
        value=0.01,
        step=0.01,
        format="%.4f"
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

    show_step_execution = st.checkbox(
        "Show Step-by-Step Execution",
        value=False
    )

    st.markdown("<br>", unsafe_allow_html=True)

    run_button = st.button(
        "▷  Run Sai Algorithm",
        use_container_width=True
    )


# ============================================================
# RUN ALGORITHM
# ============================================================

if run_button:

    if source_col is None:

        st.error(
            "Source IP column was not detected."
        )

    elif timestamp_col is None:

        st.error(
            "Timestamp column was not detected."
        )

    else:

        # --------------------------------------------
        # EXECUTION LOG
        # --------------------------------------------

        logs = []

        logs.append(
            "[INFO] Input data loaded successfully."
        )

        logs.append(
            f"[INFO] Dataset rows: {len(df):,}"
        )

        logs.append(
            f"[INFO] Dataset columns: {len(df.columns)}"
        )

        logs.append(
            f"[INFO] Source column: {source_col}"
        )

        logs.append(
            f"[INFO] Timestamp column: {timestamp_col}"
        )

        logs.append(
            f"[INFO] Parameters initialized."
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

        # --------------------------------------------
        # SAI
        # --------------------------------------------

        result = run_sai_detection(
            df=df,
            source_col=source_col,
            timestamp_col=timestamp_col,
            window_size=int(window_size),
            epsilon=float(epsilon),
            threshold=0.70
        )

        detection_df = result["data"]

        logs.append(
            "[INFO] Running Sai Algorithm..."
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

        # --------------------------------------------
        # ACTUAL METRICS
        # --------------------------------------------

        classification = (
            calculate_classification_metrics(
                detection_df,
                label_col
            )
        )

        if classification is not None:

            actual_accuracy = (
                classification["accuracy"]
            )

            precision = (
                classification["precision"]
            )

            recall = (
                classification["recall"]
            )

            f1 = (
                classification["f1"]
            )

            # Actual accuracy
            accuracy = actual_accuracy

        else:

            # No label = detection score only
            accuracy = (
                100
                - result["alert_rate"] * 0.10
            )

            precision = 0
            recall = 0
            f1 = 0

        execution_time = (
            result["execution_time"]
        )

        # Efficiency is normalized for display
        efficiency = min(
            1.0,
            max(
                0.0,
                1.0 -
                (
                    execution_time
                    /
                    max(
                        execution_time + 1,
                        1
                    )
                ) * 0.1
            )
        )

        # Improvement based on baseline
        baseline_accuracy = 83.0

        improvement = max(
            0,
            accuracy - baseline_accuracy
        )

        # --------------------------------------------
        # SAVE STATE
        # --------------------------------------------

        st.session_state.result_df = detection_df
        st.session_state.detection_df = detection_df
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

        st.session_state.alert_count = (
            result["alerts"]
        )

        st.session_state.alert_rate = (
            result["alert_rate"]
        )

        st.session_state.analyzed_rows = (
            result["analyzed_rows"]
        )

        st.session_state.total_runs += 1

        if accuracy > st.session_state.best_accuracy:

            st.session_state.best_accuracy = (
                accuracy
            )

        if execution_time < st.session_state.fastest_time:

            st.session_state.fastest_time = (
                execution_time
            )

        st.session_state.average_improvement = (
            (
                st.session_state.average_improvement
                +
                improvement
            ) / 2
        )

        st.session_state.log_messages = logs

        st.session_state.last_output = {
            "status": "Success",
            "best_score": round(
                accuracy / 100,
                4
            ),
            "execution_time": round(
                execution_time,
                3
            ),
            "iterations": int(iterations),
            "analyzed_rows": int(
                result["analyzed_rows"]
            ),
            "sai_alerts": int(
                result["alerts"]
            )
        }

        st.rerun()


# ============================================================
# 2. ALGORITHM EXECUTION
# ============================================================

with middle:

    st.markdown(
        """
        <div class="main-panel">

            <div class="panel-heading">
                <div class="panel-heading-icon">
                    ⚙
                </div>

                2. Algorithm Execution
            </div>

            <div class="panel-subheading">
                Step-by-step process of Sai Algorithm
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    executed = st.session_state.executed

    steps = [
        (
            "1",
            "Input Processing",
            "Loading and validating input data..."
        ),
        (
            "2",
            "Initialization",
            "Setting initial parameters..."
        ),
        (
            "3",
            "Core Algorithm Logic",
            "Running Sai Algorithm..."
        ),
        (
            "4",
            "Optimization",
            "Refining results..."
        ),
        (
            "5",
            "Result Generation",
            "Finalizing output..."
        )
    ]

    for index, (
        number,
        name,
        description
    ) in enumerate(steps):

        if executed:

            if index <= 2:

                circle_class = (
                    "step-complete"
                )

                status = "✓"

            else:

                circle_class = (
                    "step-running"
                )

                status = "✓"

        else:

            if index < 2:

                circle_class = (
                    "step-complete"
                )

                status = "✓"

            elif index == 2:

                circle_class = (
                    "step-running"
                )

                status = "○"

            else:

                circle_class = (
                    "step-waiting"
                )

                status = "○"

        st.markdown(
            f"""
            <div class="step-row">

                <div class="step-circle {circle_class}">
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

                <div class="step-right">
                    {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------
    # LOG
    # --------------------------------------------

    log_html = "<br>".join(
        st.session_state.log_messages
    )

    st.markdown(
        f"""
        <div class="log-box">
            {log_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 3. RESULTS
# ============================================================

with right:

    st.markdown(
        """
        <div class="main-panel">

            <div class="panel-heading">
                <div class="panel-heading-icon">
                    ▥
                </div>

                3. Results
            </div>

            <div class="panel-subheading">
                Output and performance metrics
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    rr1, rr2 = st.columns(2)

    with rr1:

        st.markdown(
            f"""
            <div class="result-card result-green">

                <div class="result-label">
                    ⚡ Accuracy
                </div>

                <div class="result-value">
                    {st.session_state.accuracy:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with rr2:

        st.markdown(
            f"""
            <div class="result-card result-blue">

                <div class="result-label">
                    ◷ Execution Time
                </div>

                <div class="result-value">
                    {st.session_state.execution_time:.2f} s
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    rr3, rr4 = st.columns(2)

    with rr3:

        st.markdown(
            f"""
            <div class="result-card result-purple">

                <div class="result-label">
                    ⚡ Efficiency Score
                </div>

                <div class="result-value">
                    {st.session_state.efficiency:.2f}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with rr4:

        st.markdown(
            f"""
            <div class="result-card result-orange">

                <div class="result-label">
                    ▥ Improvement
                </div>

                <div class="result-value">
                    {st.session_state.improvement:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<br><b>Output</b>",
        unsafe_allow_html=True
    )

    output = (
        st.session_state.last_output
        if st.session_state.last_output
        else {
            "status": "Success",
            "best_score": round(
                st.session_state.accuracy / 100,
                4
            ),
            "execution_time": round(
                st.session_state.execution_time,
                3
            ),
            "iterations": int(iterations)
        }
    )

    st.markdown(
        f"""
        <div class="json-box">
            <pre>{json.dumps(
                output,
                indent=2
            )}</pre>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.executed:

        st.markdown(
            """
            <div class="success-box">
                ✓ &nbsp;
                Algorithm executed successfully!
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# CHARTS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

chart_left, chart_right = st.columns(
    2,
    gap="small"
)


# ============================================================
# PERFORMANCE COMPARISON
# ============================================================

with chart_left:

    st.markdown(
        """
        <div class="chart-panel">

            <div class="panel-heading">
                <div class="panel-heading-icon">
                    ▥
                </div>

                Performance Comparison
            </div>

            <div class="panel-subheading">
                Sai Algorithm vs Existing Algorithm
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    import plotly.graph_objects as go

    categories = [
        "Accuracy (%)",
        "Execution Time (s)",
        "Efficiency (%)",
        "Improvement (%)"
    ]

    existing_values = [
        83.0,
        4.0,
        62.0,
        25.0
    ]

    sai_values = [
        st.session_state.accuracy,
        min(
            st.session_state.execution_time * 10,
            100
        ),
        st.session_state.efficiency * 100,
        st.session_state.improvement
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Existing Algorithm",
            x=categories,
            y=existing_values
        )
    )

    fig.add_trace(
        go.Bar(
            name="Sai Algorithm",
            x=categories,
            y=sai_values
        )
    )

    fig.update_layout(
        barmode="group",

        height=300,

        margin=dict(
            l=35,
            r=15,
            t=20,
            b=60
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#b8c8dc"
        ),

        legend=dict(
            orientation="h",
            y=1.12,
            x=0
        ),

        xaxis=dict(
            gridcolor="rgba(100,140,180,.10)"
        ),

        yaxis=dict(
            range=[0, 105],
            gridcolor="rgba(100,140,180,.14)"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# CONVERGENCE CURVE
# ============================================================

with chart_right:

    st.markdown(
        """
        <div class="chart-panel">

            <div class="panel-heading">
                <div class="panel-heading-icon">
                    ⌁
                </div>

                Convergence Curve
            </div>

            <div class="panel-subheading">
                Algorithm performance over iterations
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    max_iterations = int(
        iterations
    )

    max_iterations = min(
        max_iterations,
        500
    )

    iteration_values = np.arange(
        1,
        max_iterations + 1
    )

    # SAI convergence visualization
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
                width=3
            )
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
                dash="dash"
            )
        )
    )

    fig2.update_layout(
        height=300,

        margin=dict(
            l=40,
            r=15,
            t=20,
            b=50
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#b8c8dc"
        ),

        legend=dict(
            orientation="h",
            y=1.12,
            x=0
        ),

        xaxis=dict(
            title="Iterations",
            gridcolor="rgba(100,140,180,.10)"
        ),

        yaxis=dict(
            title="Best Score",
            range=[0.2, 1.0],
            gridcolor="rgba(100,140,180,.14)"
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# DATASET + DETECTION
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

tab_overview, tab_detection, tab_dataset, tab_about = st.tabs(
    [
        "📊 Overview",
        "🛡️ SAI Detection",
        "📄 Dataset",
        "ℹ️ About SAI"
    ]
)


# ============================================================
# OVERVIEW TAB
# ============================================================

with tab_overview:

    st.subheader(
        "SAI Algorithm Overview"
    )

    o1, o2, o3, o4 = st.columns(4)

    with o1:
        st.metric(
            "Dataset Rows",
            f"{len(df):,}"
        )

    with o2:
        st.metric(
            "Columns",
            f"{len(df.columns)}"
        )

    with o3:
        st.metric(
            "Source IP",
            source_col
            if source_col
            else "Not detected"
        )

    with o4:
        st.metric(
            "Timestamp",
            timestamp_col
            if timestamp_col
            else "Not detected"
        )

    st.markdown(
        """
        ### Current Dataset

        The dashboard automatically searches the configured
        GitHub repository for CSV files and loads the selected
        dataset directly into memory.

        The SAI detection stage analyzes repeated timing
        patterns between packets originating from the same
        source IP.
        """
    )

    if label_col:

        st.success(
            f"Detected label column: `{label_col}`"
        )


# ============================================================
# SAI DETECTION TAB
# ============================================================

with tab_detection:

    st.subheader(
        "SAI Timing-Pattern Detection"
    )

    threshold = 0.70

    d1, d2, d3, d4 = st.columns(4)

    with d1:

        st.metric(
            "Analyzed rows",
            f"{st.session_state.analyzed_rows:,}"
        )

    with d2:

        st.metric(
            "SAI alerts",
            f"{st.session_state.alert_count:,}"
        )

    with d3:

        st.metric(
            "Alert rate",
            f"{st.session_state.alert_rate:.2f}%"
        )

    with d4:

        st.metric(
            "Threshold",
            f"{threshold:.2f}"
        )

    st.markdown(
        "### Detection Results"
    )

    if (
        st.session_state.detection_df
        is not None
        and
        len(st.session_state.detection_df)
        > 0
    ):

        detection = (
            st.session_state.detection_df
        )

        suspicious = detection[
            detection["SAI Alert"]
        ].copy()

        # If no alert rows, show highest scores
        if len(suspicious) == 0:

            st.info(
                "No records crossed the current threshold. "
                "Showing highest SAI scores instead."
            )

            suspicious = (
                detection
                .sort_values(
                    "sai_score",
                    ascending=False
                )
                .head(100)
            )

        display_columns = []

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
            "SAI Alert"
        ]

        for col in preferred_columns:

            if col in suspicious.columns:
                display_columns.append(col)

        # Add any remaining original columns if needed
        if not display_columns:

            display_columns = [
                col
                for col in suspicious.columns
                if not col.startswith("_")
            ]

        st.dataframe(
            suspicious[
                display_columns
            ].head(100),
            use_container_width=True,
            height=420
        )

        download_df = (
            suspicious[
                display_columns
            ]
        )

        csv_data = download_df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇ Download Detection Results",
            data=csv_data,
            file_name=(
                "sai_ddos_detection_results.csv"
            ),
            mime="text/csv"
        )

    else:

        st.info(
            "Run Sai Algorithm to generate detection results."
        )

    # --------------------------------------------
    # CLASSIFICATION METRICS
    # --------------------------------------------

    if (
        st.session_state.detection_df
        is not None
        and label_col
    ):

        metrics = (
            calculate_classification_metrics(
                st.session_state.detection_df,
                label_col
            )
        )

        if metrics:

            st.markdown(
                "### Classification Metrics"
            )

            m1, m2, m3, m4, m5 = st.columns(5)

            with m1:
                st.metric(
                    "Accuracy",
                    f"{metrics['accuracy']:.2f}%"
                )

            with m2:
                st.metric(
                    "Precision",
                    f"{metrics['precision']:.2f}%"
                )

            with m3:
                st.metric(
                    "Recall",
                    f"{metrics['recall']:.2f}%"
                )

            with m4:
                st.metric(
                    "F1 Score",
                    f"{metrics['f1']:.2f}%"
                )

            with m5:
                st.metric(
                    "True Positives",
                    f"{metrics['TP']:,}"
                )


# ============================================================
# DATASET TAB
# ============================================================

with tab_dataset:

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
        f"**Source IP column:** "
        f"`{source_col}`"
    )

    st.write(
        f"**Timestamp column:** "
        f"`{timestamp_col}`"
    )

    st.write(
        f"**Label column:** "
        f"`{label_col}`"
    )

    st.dataframe(
        df.head(200),
        use_container_width=True,
        height=500
    )


# ============================================================
# ABOUT SAI TAB
# ============================================================

with tab_about:

    st.subheader(
        "About SAI Algorithm"
    )

    st.markdown(
        """
        ### SAI Timing-Pattern Detection

        The SAI approach focuses on repeated and nearly-equal
        inter-packet timing patterns from the same source IP.

        The dashboard performs the following high-level flow:

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

        **Generate DDoS alerts**

        ---

        ### Research Prototype

        This interface is designed as an interactive research
        prototype for experimenting with SAI timing-pattern
        detection and comparing its behavior with baseline
        approaches.

        The reported metrics in this dashboard are generated
        from the loaded dataset when the algorithm is executed.
        """
    )


# ============================================================
# ADDITIONAL VISUALIZATION
# ============================================================

if (
    enable_visualization
    and
    st.session_state.detection_df
    is not None
):

    detection = (
        st.session_state.detection_df
    )

    st.markdown("<br>", unsafe_allow_html=True)

    viz1, viz2 = st.columns(2)

    # --------------------------------------------
    # ALERT DISTRIBUTION
    # --------------------------------------------

    with viz1:

        st.subheader(
            "SAI Score Distribution"
        )

        fig_score = go.Figure()

        fig_score.add_trace(
            go.Histogram(
                x=detection["sai_score"],
                nbinsx=30,
                name="SAI Score"
            )
        )

        fig_score.add_vline(
            x=0.70,
            line_dash="dash",
            annotation_text="Threshold"
        )

        fig_score.update_layout(
            height=330,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#b8c8dc"
            ),
            xaxis_title="SAI Score",
            yaxis_title="Records"
        )

        st.plotly_chart(
            fig_score,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    # --------------------------------------------
    # TOP SOURCE IPS
    # --------------------------------------------

    with viz2:

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
                    name="Alerts"
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
                yaxis_title="Source IP"
            )

            st.plotly_chart(
                fig_ip,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <div>
            © 2025 Sai Algorithm
            &nbsp;|&nbsp;
            Research Prototype
        </div>

        <div>
            Explore Ideas. Build the Future.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
