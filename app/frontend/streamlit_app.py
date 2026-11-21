
import streamlit as st
import requests
import pandas as pd

# =========================================================
# 1. CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(
    page_title="QueryMind AI | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =========================================================
# 3. CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #6558D3;
    --primary-light: #F0EEFF;
    --text: #182230;
    --muted: #718096;
    --border: #E8EBF2;
    --surface: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #F6F7FB;
    color: var(--text);
}

/* TOP HEADER FIX */

[data-testid="stHeader"] {
    background: #F6F7FB;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    display: none;
}

/* MAIN CONTENT */

.block-container {
    max-width: 1450px;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8EBF2;
}

[data-testid="stSidebar"] * {
    color: #253047;
}

/* BRAND */

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #22283A;
    letter-spacing: -1px;
}

.brand span {
    color: #6558D3;
}

/* TYPOGRAPHY */

h1, h2, h3 {
    color: #182230;
    letter-spacing: -0.5px;
}

p {
    color: #526176;
}

/* HERO */

.hero {
    background: linear-gradient(
        115deg,
        #FFFFFF 0%,
        #F0EEFF 100%
    );
    border: 1px solid #E6E2FA;
    border-radius: 20px;
    padding: 38px;
    margin-top: 15px;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 38px;
    line-height: 1.25;
    font-weight: 800;
    letter-spacing: -1.5px;
    color: #20243A;
}

.hero-subtitle {
    color: #69748A;
    font-size: 15px;
    line-height: 1.8;
    margin-top: 14px;
    max-width: 760px;
}

.eyebrow {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.7px;
    color: #8074D8;
    text-transform: uppercase;
}

/* METRICS */

div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8EBF2;
    padding: 19px;
    border-radius: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #78859A;
}

div[data-testid="stMetricValue"] {
    color: #20283A;
}

/* BUTTONS */

.stButton > button {
    border-radius: 10px;
    border: 1px solid #E3E5EF;
    background: #FFFFFF;
    color: #3B4255;
    font-weight: 600;
    min-height: 43px;
    transition: all .2s ease;
}

.stButton > button:hover {
    border-color: #8B7DE5;
    color: #6558D3;
    background: #F7F5FF;
}

div.stButton > button[kind="primary"] {
    background: #6558D3;
    border-color: #6558D3;
    color: #FFFFFF;
}

div.stButton > button[kind="primary"]:hover {
    background: #5144BB;
    color: #FFFFFF;
}

/* CHAT */

[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E8EBF2;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    background: #FFFFFF;
    border: 1px solid #DDE1EC;
    border-radius: 14px;
}

/* DATA TABLE */

[data-testid="stDataFrame"] {
    border: 1px solid #E8EBF2;
    border-radius: 12px;
}

/* CODE */

[data-testid="stCode"] {
    border-radius: 12px;
}

/* FOOTER */

.footer {
    color: #9AA3B2;
    text-align: center;
    font-size: 12px;
    padding: 25px 0;
}

hr {
    border-color: #EAECF2;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. RESPONSE DISPLAY
# =========================================================

def display_response(data, key_suffix):

    if data.get("sql"):

        st.markdown("#### Generated SQL")

        st.code(
            data["sql"],
            language="sql"
        )

    if data.get("explanation"):

        st.markdown("#### Query Explanation")

        st.write(data["explanation"])

    if data.get("assumptions"):

        with st.expander("View assumptions"):

            for assumption in data["assumptions"]:
                st.write(f"• {assumption}")

    results = data.get("results") or []

    if results:

        df = pd.DataFrame(results)

        st.markdown("#### Query Results")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Rows Returned",
                data.get("row_count", len(df))
            )

        with col2:
            st.metric(
                "Columns",
                len(df.columns)
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # CHART

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        category_columns = [
            col for col in df.columns
            if col not in numeric_columns
        ]

        if numeric_columns and category_columns and len(df) > 1:

            with st.expander("📊 Visualize Query Results"):

                chart_df = df.set_index(
                    category_columns[0]
                )[numeric_columns]

                st.bar_chart(chart_df)

        # CSV DOWNLOAD

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download CSV",
            data=csv,
            file_name="query_results.csv",
            mime="text/csv",
            key=f"download_{key_suffix}"
        )

    if data.get("needs_clarification"):

        st.info(
            "Please answer the clarification question "
            "in the chat box below to continue."
        )

    if data.get("error"):

        st.error(data["error"])


# =========================================================
# 5. PROCESS USER QUESTION
# =========================================================

def process_question(question):

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    payload = {
        "question": question
    }

    if st.session_state.conversation_id:

        payload["conversation_id"] = (
            st.session_state.conversation_id
        )

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=240
        )

        response.raise_for_status()

        data = response.json()

        # CLARIFICATION

        if data.get("needs_clarification"):

            st.session_state.conversation_id = (
                data.get("conversation_id")
            )

            content = (
                "🤔 **I need a little more information.**\n\n"
                + data.get(
                    "clarification_question",
                    "Could you clarify your question?"
                )
            )

        # SUCCESS

        elif data.get("success"):

            st.session_state.conversation_id = None

            content = (
                "✅ **Your query was executed successfully!**"
            )

        # FAILURE

        else:

            st.session_state.conversation_id = None

            content = (
                data.get("error")
                or "Unable to process your question."
            )

        st.session_state.messages.append({
            "role": "assistant",
            "content": content,
            "data": data
        })

    except requests.exceptions.Timeout:

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "⏳ The AI is taking longer than expected. "
                "Please try again."
            )
        })

    except requests.exceptions.ConnectionError:

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "❌ Cannot connect to FastAPI. "
                "Please make sure the backend is running."
            )
        })

    except requests.exceptions.HTTPError as error:

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Backend HTTP error: {error}"
        })

    except Exception as error:

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Unexpected error: {error}"
        })


# =========================================================
# 6. SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Query<span>Mind</span> AI</div>',
        unsafe_allow_html=True
    )

    st.caption("INTELLIGENT DATA WORKSPACE")

    st.divider()

    st.markdown("### Workspace")

    st.markdown("📊 AI Query Assistant")
    st.markdown("🗄️ Database Explorer")
    st.markdown("🧾 Query History")

    st.divider()

    st.markdown("### AI Configuration")

    st.markdown("**AI Model**")
    st.caption("Qwen 2.5 · 3B parameters")

    st.markdown("**Inference Engine**")
    st.caption("Ollama · Local execution")

    st.markdown("**Database**")
    st.caption("SQLite · Read-only execution")

    st.divider()

    st.markdown("### Technology Stack")

    st.caption("Python · FastAPI · Streamlit")
    st.caption("SQLGlot · SQLite · Ollama")

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True,
        type="primary"
    ):

        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.pending_question = None

        st.rerun()

    st.caption("QueryMind AI · Analytics Workspace")


# =========================================================
# 7. MAIN HEADER
# =========================================================

st.markdown(
    '<div class="eyebrow">AI-POWERED DATA ANALYTICS</div>',
    unsafe_allow_html=True
)

# IMPORTANT:
# HTML begins at the left edge inside this string.
# This prevents Streamlit from displaying it as a code block.

st.markdown(
    """
<div class="hero">
<div class="hero-title">
Understand your data.<br>
<span style="color:#6558D3;">Just by asking.</span>
</div>
<div class="hero-subtitle">
Transform everyday language into SQL queries,
explore database results, and discover meaningful
insights without writing SQL manually.
</div>
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# 8. DASHBOARD METRICS
# =========================================================

total_queries = sum(
    1 for msg in st.session_state.messages
    if msg["role"] == "user"
)

successful_queries = sum(
    1 for msg in st.session_state.messages
    if msg["role"] == "assistant"
    and msg.get("data", {}).get("success")
)

clarifications = sum(
    1 for msg in st.session_state.messages
    if msg["role"] == "assistant"
    and msg.get("data", {}).get("needs_clarification")
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Questions Asked",
        total_queries
    )

with col2:
    st.metric(
        "Successful Queries",
        successful_queries
    )

with col3:
    st.metric(
        "Clarifications",
        clarifications
    )


# =========================================================
# 9. SUGGESTED QUESTIONS
# =========================================================

st.markdown("### Explore Your Database")

st.caption(
    "Choose a suggested question or write your own."
)

examples = [
    "Show all customers from Bengaluru.",
    "Find the top 3 customers based on their total spending.",
    "Show all orders."
]

example_cols = st.columns(3)

for index, example in enumerate(examples):

    with example_cols[index]:

        if st.button(
            example,
            key=f"example_{index}",
            use_container_width=True
        ):

            st.session_state.pending_question = example

            st.rerun()


# =========================================================
# 10. AI CHAT ASSISTANT
# =========================================================

st.markdown("### AI Query Assistant")

st.caption(
    "Your conversation, generated SQL, and database results."
)

for index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("data"):

            display_response(
                message["data"],
                key_suffix=str(index)
            )


# =========================================================
# 11. CHAT INPUT
# =========================================================

question = st.chat_input(
    "Ask a question about your database..."
)

if st.session_state.pending_question:

    question = st.session_state.pending_question

    st.session_state.pending_question = None


# =========================================================
# 12. EXECUTE QUERY
# =========================================================

if question:

    with st.spinner(
        "🧠 AI is understanding your question and generating SQL..."
    ):

        process_question(question)

    st.rerun()


# =========================================================
# 13. FOOTER
# =========================================================

st.divider()

st.markdown(
    """
<div class="footer">
QUERYMIND AI · INTELLIGENT TEXT-TO-SQL PLATFORM<br>
Built with Python · Ollama · FastAPI · SQLite · Streamlit
</div>
""",
    unsafe_allow_html=True
)
