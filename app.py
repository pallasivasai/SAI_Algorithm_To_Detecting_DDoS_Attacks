import streamlit as st

# ============================================================
# SAI ALGORITHM
# Interactive Research Prototype
# ============================================================

st.set_page_config(
    page_title="SAI ALGORITHM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.stApp {
    background: #07152d;
}

/* Remove Streamlit top padding */
.block-container {
    padding-top: 1.5rem;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #07152d;
    border-right: 1px solid #203452;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* LOGO */

.logo-box {
    background: #f8fafc;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    margin-bottom: 25px;
}

.infinity {
    font-size: 55px;
    color: #07152d;
    line-height: 1;
}

.logo-title {
    font-size: 20px;
    font-weight: 700;
    color: #07152d;
    margin-top: 8px;
}

.logo-subtitle {
    font-size: 14px;
    color: #536174;
    margin-top: 5px;
}

/* MAIN HEADER */

.header {
    background: #f8fafc;
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 22px;
}

.header-title {
    font-size: 34px;
    font-weight: 800;
    color: #172033;
}

.header-title span {
    color: #2477ff;
}

.header-subtitle {
    color: #5b6678;
    font-size: 16px;
    margin-top: 6px;
}

.tags {
    margin-top: 15px;
}

.tag {
    display: inline-block;
    background: #e9f1ff;
    color: #2167d5;
    border-radius: 20px;
    padding: 7px 14px;
    margin-right: 7px;
    font-size: 13px;
}

/* CARDS */

.card {
    background: #f8fafc;
    border-radius: 18px;
    padding: 25px;
    min-height: 160px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 18px;
    font-weight: 700;
    color: #172033;
}

.card-text {
    color: #5b6678;
    line-height: 1.6;
    margin-top: 8px;
}

/* STATUS */

.status {
    background: #0c2446;
    border: 1px solid #24466e;
    border-radius: 14px;
    padding: 15px 18px;
    color: white;
    margin-bottom: 20px;
}

.status-dot {
    color: #36d98a;
}

/* COMMAND */

.command-box {
    background: #f8fafc;
    border-radius: 18px;
    padding: 25px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div class="logo-box">

        <div class="infinity">
            ∞
        </div>

        <div class="logo-title">
            SAI ALGORITHM
        </div>

        <div class="logo-subtitle">
            Research Prototype
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.page_link(
        "#",
        label="⌂  Home"
    )

    st.page_link(
        "#algorithm",
        label="♟  Algorithm"
    )

    st.page_link(
        "#simulation",
        label="▷  Run Simulation"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header">

    <div class="header-title">
        SAI <span>ALGORITHM</span>
    </div>

    <div class="header-subtitle">
        Interactive Research Prototype
    </div>

    <div class="tags">
        <span class="tag">Explore</span>
        <span class="tag">Experiment</span>
        <span class="tag">Analyze</span>
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# STATUS
# ============================================================

st.markdown("""
<div class="status">
    <span class="status-dot">●</span>
    SAI SYSTEM READY
</div>
""", unsafe_allow_html=True)


# ============================================================
# HOME
# ============================================================

st.markdown("""
<div class="card">

    <div class="card-title">
        🧠 SAI Algorithm
    </div>

    <div class="card-text">
        Welcome to the SAI Algorithm interactive research
        prototype. Use the controls below to explore the
        algorithm and run a simulation.
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# ALGORITHM
# ============================================================

st.markdown(
    '<div id="algorithm"></div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="card">

    <div class="card-title">
        Algorithm Flow
    </div>

    <div class="card-text">

        Input
        →
        Processing
        →
        Intelligence
        →
        Decision
        →
        Output

    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIMULATION
# ============================================================

st.markdown(
    '<div id="simulation"></div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="card">

    <div class="card-title">
        Run Simulation
    </div>

    <div class="card-text">
        Enter an input and run the SAI algorithm.
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================

user_input = st.text_input(
    "Input",
    placeholder="Enter something to test..."
)


# ============================================================
# RUN
# ============================================================

if st.button(
    "▶ Run SAI Algorithm",
    use_container_width=True
):

    if not user_input.strip():

        st.warning(
            "Please enter an input."
        )

    else:

        st.success(
            "SAI Algorithm executed successfully."
        )

        st.write(
            f"Input received: **{user_input}**"
        )

        st.info(
            "Processing complete."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="
    text-align:center;
    color:#8b9bb4;
    padding:35px 0 10px 0;
    font-size:13px;
">
    SAI ALGORITHM • Interactive Research Prototype
</div>
""", unsafe_allow_html=True)
