# ============================================================
# app.py — Student Academic Tracking System (Stage 1)
# ============================================================
# A clean Streamlit prototype that lets Teachers add students
# and grades, and lets Parents view academic progress.
#
# Run with:  streamlit run app.py
#
# Libraries: streamlit, pandas
# ============================================================

import streamlit as st
import pandas as pd

# ────────────────────────────────────────────────────────────
# 0.  PAGE CONFIGURATION  (must be the very first st call)
# ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Academic Tracking System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────────────────
# 1.  CUSTOM CSS — school-friendly colours & card styling
# ────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ---------- Global background ---------- */
    .stApp {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f8f0 100%);
    }

    /* ---------- Top banner ---------- */
    .main-header {
        background: linear-gradient(90deg, #4db8d1 0%, #45b389 100%);
        padding: 28px 40px;
        border-radius: 0 0 24px 24px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,.08);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.4rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: .3px;
    }
    .main-header p {
        color: #e0f7fa;
        font-size: 1.05rem;
        margin: 8px 0 0 0;
        font-weight: 400;
    }

    /* ---------- White card container ---------- */
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,.06);
        border: 1px solid #e8f0f2;
    }
    .card h3 {
        color: #2c3e50;
        margin-top: 0;
        font-weight: 600;
    }

    /* ---------- Metric cards ---------- */
    .metric-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 22px 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,.06);
        border-left: 5px solid #4db8d1;
    }
    .metric-card.green  { border-left-color: #45b389; }
    .metric-card.orange { border-left-color: #f0a04b; }
    .metric-card .num   { font-size: 2rem; font-weight: 700; color: #2c3e50; }
    .metric-card .label { font-size: .88rem; color: #7f8c8d; margin-top: 2px; }

    /* ---------- Login box ---------- */
    .login-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 40px 44px;
        max-width: 440px;
        margin: 60px auto;
        box-shadow: 0 8px 32px rgba(0,0,0,.10);
        border-top: 5px solid #4db8d1;
    }
    .login-box h2 {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 6px;
    }
    .login-box .sub {
        text-align: center;
        color: #7f8c8d;
        font-size: .92rem;
        margin-bottom: 24px;
    }

    /* ---------- Role badge ---------- */
    .role-badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: .82rem;
        font-weight: 600;
        color: #fff;
    }
    .role-badge.teacher { background: #4db8d1; }
    .role-badge.parent  { background: #45b389; }

    /* ---------- Grade pill colours ---------- */
    .grade-a  { background: #d5f5e3; color: #1e8449; padding: 3px 12px; border-radius: 10px; font-weight: 600; }
    .grade-b  { background: #d4efdf; color: #27ae60; padding: 3px 12px; border-radius: 10px; font-weight: 600; }
    .grade-c  { background: #fef9e7; color: #d4ac0d; padding: 3px 12px; border-radius: 10px; font-weight: 600; }
    .grade-d  { background: #fdebd0; color: #e67e22; padding: 3px 12px; border-radius: 10px; font-weight: 600; }
    .grade-f  { background: #fadbd8; color: #e74c3c; padding: 3px 12px; border-radius: 10px; font-weight: 600; }

    /* ---------- Info banner ---------- */
    .info-banner {
        background: linear-gradient(90deg, #eafaf1 0%, #e8f8f5 100%);
        border-left: 5px solid #45b389;
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 20px;
        color: #2c3e50;
    }

    /* ---------- Success toast ---------- */
    .success-toast {
        background: #d5f5e3;
        border-radius: 10px;
        padding: 14px 20px;
        color: #1e8449;
        font-weight: 500;
        text-align: center;
        margin-bottom: 16px;
    }

    /* ---------- Misc tweaks ---------- */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ────────────────────────────────────────────────────────────
# 2.  DEMO CREDENTIALS
# ────────────────────────────────────────────────────────────
DEMO_USERS = {
    "teacher": {"password": "1234", "role": "Teacher", "name": "Mr. Davis"},
    "parent":  {"password": "1234", "role": "Parent",  "name": "Mrs. Garcia"},
}


# ────────────────────────────────────────────────────────────
# 3.  SESSION-STATE INITIALISATION
# ────────────────────────────────────────────────────────────
# We keep everything in st.session_state so data survives re-runs.

if "logged_in" not in st.session_state:
    st.session_state.logged_in  = False
    st.session_state.role       = ""
    st.session_state.user_name  = ""

if "students" not in st.session_state:
    # Pre-loaded sample data so the dashboard is never empty
    st.session_state.students = pd.DataFrame(
        {
            "Student":     ["Alex Chen", "Maria Garcia", "Sam Lee"],
            "Mathematics": [95, 85, 79],
            "English":     [92, 98, 84],
            "Science":     [88, 90, 81],
        }
    )


# ────────────────────────────────────────────────────────────
# 4.  HELPER FUNCTIONS
# ────────────────────────────────────────────────────────────

def letter_grade(score: int) -> str:
    """Convert a numeric score (0-100) to a letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def grade_pill(score: int) -> str:
    """Return an HTML <span> styled as a coloured pill for a score."""
    lg = letter_grade(score)
    css_class = f"grade-{lg.lower()[0]}"
    return f'<span class="{css_class}">{lg} ({score})</span>'


def build_styled_table(df: pd.DataFrame) -> str:
    """Build a rich HTML table with coloured grade pills."""
    rows = ""
    for _, row in df.iterrows():
        rows += "<tr>"
        rows += f'<td style="padding:12px 16px;font-weight:600;color:#2c3e50;">{row["Student"]}</td>'
        for subj in ["Mathematics", "English", "Science"]:
            rows += f'<td style="padding:12px 16px;text-align:center;">{grade_pill(int(row[subj]))}</td>'
        rows += "</tr>"

    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:.95rem;">
        <thead>
            <tr style="background:#f0f8ff;border-bottom:2px solid #d5e8f0;">
                <th style="padding:14px 16px;text-align:left;color:#34495e;">Student Name</th>
                <th style="padding:14px 16px;text-align:center;color:#34495e;">Mathematics</th>
                <th style="padding:14px 16px;text-align:center;color:#34495e;">English</th>
                <th style="padding:14px 16px;text-align:center;color:#34495e;">Science</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


def compute_class_stats(df: pd.DataFrame) -> dict:
    """Return quick statistics about the class."""
    subjects = ["Mathematics", "English", "Science"]
    if df.empty:
        return {"total": 0, "avg": 0.0, "top": "—"}
    avg = round(df[subjects].mean().mean(), 1)
    # Best student by total score
    df_copy = df.copy()
    df_copy["_total"] = df_copy[subjects].sum(axis=1)
    top = df_copy.loc[df_copy["_total"].idxmax(), "Student"]
    return {"total": len(df), "avg": avg, "top": top}


# ────────────────────────────────────────────────────────────
# 5.  HEADER BANNER  (always visible)
# ────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="main-header">
        <h1>🎓 Student Academic Tracking System</h1>
        <p>A platform that connects teachers, parents, and students to track academic progress.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 6.  LOGIN SECTION
# ============================================================

def show_login():
    """Render the login form inside a centred card."""

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h2>🔐 Welcome Back</h2>", unsafe_allow_html=True)
    st.markdown('<p class="sub">Sign in to access your dashboard</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Centre the form using columns
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        with st.form("login_form"):
            username = st.text_input("👤  Username", placeholder="teacher or parent")
            password = st.text_input("🔒  Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🚀  Sign In", use_container_width=True)

            if submitted:
                user = DEMO_USERS.get(username)
                if user and user["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.role      = user["role"]
                    st.session_state.user_name = user["name"]
                    st.rerun()                       # refresh page into dashboard
                else:
                    st.error("❌ Invalid username or password. Please try again.")

        # Helpful hint for demo
        st.markdown(
            """
            <div style="text-align:center;margin-top:12px;font-size:.84rem;color:#95a5a6;">
                <strong>Demo accounts →</strong>
                teacher / 1234 &nbsp;•&nbsp; parent / 1234
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 7.  TEACHER DASHBOARD
# ============================================================

def show_teacher_dashboard():
    """Full teacher view: metrics, add-student form, grades table."""

    df = st.session_state.students
    stats = compute_class_stats(df)

    # --- Top bar: greeting + logout ---
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.5rem;">👋</span>
                <span style="font-size:1.25rem;font-weight:600;color:#2c3e50;">
                    Welcome, {st.session_state.user_name}
                </span>
                <span class="role-badge teacher">Teacher</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # --- Metric cards ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="num">{stats["total"]}</div>
                <div class="label">📚 Total Students</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card green">
                <div class="num">{stats["avg"]}</div>
                <div class="label">📊 Class Average</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card orange">
                <div class="num" style="font-size:1.4rem;">{stats["top"]}</div>
                <div class="label">🏆 Top Student</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Two-column layout: form on left, table on right ---
    col_form, col_table = st.columns([1, 2])

    # ---- Add Student Form ----
    with col_form:
        st.markdown('<div class="card"><h3>➕ Add New Student</h3>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("add_student", clear_on_submit=True):
            student_name = st.text_input(
                "Student Name",
                placeholder="e.g. John Smith",
            )
            st.markdown("##### 📝 Enter Grades (0 – 100)")
            math_grade    = st.number_input("Mathematics", min_value=0, max_value=100, value=85, step=1)
            english_grade = st.number_input("English",     min_value=0, max_value=100, value=85, step=1)
            science_grade = st.number_input("Science",     min_value=0, max_value=100, value=85, step=1)
            add_clicked   = st.form_submit_button("✅  Add Student", use_container_width=True)

        if add_clicked:
            if student_name.strip() == "":
                st.warning("⚠️ Please enter the student's name.")
            elif student_name.strip() in df["Student"].values:
                st.warning("⚠️ A student with that name already exists.")
            else:
                new_row = pd.DataFrame(
                    [{
                        "Student":     student_name.strip(),
                        "Mathematics": math_grade,
                        "English":     english_grade,
                        "Science":     science_grade,
                    }]
                )
                st.session_state.students = pd.concat(
                    [df, new_row], ignore_index=True
                )
                st.markdown(
                    f'<div class="success-toast">🎉 <strong>{student_name.strip()}</strong> added successfully!</div>',
                    unsafe_allow_html=True,
                )
                st.rerun()

    # ---- Student Grades Table ----
    with col_table:
        st.markdown('<div class="card"><h3>📋 Student Grades</h3>', unsafe_allow_html=True)

        if df.empty:
            st.info("No students yet. Use the form on the left to add one!")
        else:
            st.markdown(build_styled_table(df), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Detailed editable view (expandable) ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card"><h3>📊 Overall Class Performance — Detailed View</h3>', unsafe_allow_html=True)

    if not df.empty:
        # Show the raw DataFrame with Streamlit's built-in component
        display_df = df.copy()
        display_df.index = range(1, len(display_df) + 1)   # 1-based index
        display_df.index.name = "#"
        st.dataframe(display_df, use_container_width=True, height=260)

        # Quick per-subject averages
        st.markdown("##### Subject Averages")
        sa1, sa2, sa3 = st.columns(3)
        sa1.metric("Mathematics", f"{df['Mathematics'].mean():.1f}")
        sa2.metric("English",     f"{df['English'].mean():.1f}")
        sa3.metric("Science",     f"{df['Science'].mean():.1f}")
    else:
        st.info("Add students to see detailed analytics here.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 8.  PARENT DASHBOARD
# ============================================================

def show_parent_dashboard():
    """Read-only parent view: greeting, info banner, grades table."""

    df = st.session_state.students
    stats = compute_class_stats(df)

    # --- Top bar: greeting + logout ---
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:1.5rem;">👋</span>
                <span style="font-size:1.25rem;font-weight:600;color:#2c3e50;">
                    Welcome, {st.session_state.user_name}
                </span>
                <span class="role-badge parent">Parent</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")

    # --- Info banner ---
    st.markdown(
        """
        <div class="info-banner">
            👨‍👩‍👧‍👦 <strong>Parents can view their child's academic progress here.</strong><br>
            <span style="font-size:.9rem;">
                Below you will find the latest grades recorded by the teacher.
                If you have questions, please contact the school office.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Metric cards ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="num">{stats["total"]}</div>
                <div class="label">📚 Students in Class</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card green">
                <div class="num">{stats["avg"]}</div>
                <div class="label">📊 Class Average</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card orange">
                <div class="num" style="font-size:1.4rem;">{stats["top"]}</div>
                <div class="label">🏆 Top Student</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Grades table (read-only) ---
    st.markdown('<div class="card"><h3>📋 Student Grades</h3>', unsafe_allow_html=True)

    if df.empty:
        st.info("No grades have been recorded yet. Please check back later.")
    else:
        st.markdown(build_styled_table(df), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Simple Streamlit table as fallback ---
    st.markdown('<div class="card"><h3>📊 Detailed Grades Table</h3>', unsafe_allow_html=True)

    if not df.empty:
        display_df = df.copy()
        display_df.index = range(1, len(display_df) + 1)
        display_df.index.name = "#"
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Nothing to display yet.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 9.  APP ROUTER — show the right page based on state
# ============================================================

if not st.session_state.logged_in:
    show_login()
elif st.session_state.role == "Teacher":
    show_teacher_dashboard()
elif st.session_state.role == "Parent":
    show_parent_dashboard()
else:
    # Fallback — should never happen
    st.error("Unknown role. Please log out and try again.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


# ────────────────────────────────────────────────────────────
# 10. FOOTER
# ────────────────────────────────────────────────────────────
st.markdown(
    """
    <br><br>
    <div style="text-align:center;color:#aab7b8;font-size:.82rem;padding-bottom:24px;">
        © 2025 Student Academic Tracking System — Stage 1 Prototype<br>
        Built with ❤️ using Streamlit & Pandas
    </div>
    """,
    unsafe_allow_html=True,
)