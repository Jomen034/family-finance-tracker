import streamlit as st


def require_login():
    """Single shared password for the whole family app. This is deliberately
    simple (no per-user Google OAuth) - it exists to keep the app off the
    open internet, not to distinguish who's using it. See select_user()
    for that."""
    if st.session_state.get("authenticated"):
        return

    st.title("🔒 Gaudete Fams Finance Tracker")
    st.caption("Enter the family password to continue.")
    pw = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
    if st.button("Enter", use_container_width=True, type="primary"):
        if pw and pw == st.secrets["app"]["password"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Wrong password.")
    st.stop()


def select_user():
    """Asks once per browser session who's using the app, so EnteredBy on
    every transaction auto-fills without asking again and again."""
    if st.session_state.get("entered_by"):
        return

    st.title("👋 Who's logging in?")
    choice = st.radio("Select", ["Suami", "Istri"], label_visibility="collapsed")
    if st.button("Continue", use_container_width=True, type="primary"):
        st.session_state["entered_by"] = choice
        st.rerun()
    st.stop()
