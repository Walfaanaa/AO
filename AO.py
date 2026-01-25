import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os

# ===============================
# 1️⃣ PAGE SETUP
# ===============================
st.set_page_config(
    page_title="🎟️ EGSA Lottery Winners",
    layout="wide",
    page_icon="🎟️"
)

st.title("🎟️ EGSA Lottery Winners App")
st.markdown(
    """
    **Authorized & One-Time Lottery Draw System**

    This system ensures **fair, transparent, and one-time-only draws**
    controlled strictly by **authorized administrators**.
    """
)

# ===============================
# 2️⃣ FILE NAMES
# ===============================
DATA_FILE = "AO_uqubii.xlsx"      # your Excel file
WINNER_FILE = "winners_record.xlsx"

# ===============================
# 3️⃣ LOAD MEMBERS DATA
# ===============================
try:
    members_df = pd.read_excel(DATA_FILE)
    st.success(f"✅ {len(members_df)} members loaded successfully.")
    st.dataframe(members_df)
except FileNotFoundError:
    st.error(f"❌ Data file `{DATA_FILE}` not found in the repository.")
    st.stop()

# ===============================
# 4️⃣ ADMIN PASSWORD (STREAMLIT SECRETS)
# ===============================
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except KeyError:
    st.error("❌ ADMIN_PASSWORD not set in Streamlit Secrets.")
    st.stop()

password = st.text_input("🔐 Enter admin passcode to enable draw:", type="password")

# ===============================
# 5️⃣ ADMIN ACCESS
# ===============================
if password == ADMIN_PASSWORD:
    st.success("✅ Access granted. Admin controls unlocked.")

    # -------------------------------
    # ADMIN RESET (IF DRAW EXISTS)
    # -------------------------------
    if os.path.exists(WINNER_FILE):
        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A draw has already been conducted.")
            if st.button("🔄 Reset for New Draw (Admin Only)"):
                os.remove(WINNER_FILE)
                st.success("✅ Winners record deleted. Ready for a new draw.")
                st.rerun()

        previous_winners = pd.read_excel(WINNER_FILE)
        st.subheader("🎉 Previous Winners")
        st.dataframe(previous_winners)

    # -------------------------------
    # RUN LOTTERY (ONE TIME ONLY)
    # -------------------------------
    else:
        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        if st.button("🎲 Run Lottery Draw"):
            st.info("🎰 Drawing winners… please wait")

            progress = st.progress(0)
            status = st.empty()

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
                status.text(f"Progress: {i + 1}%")

            winners = members_df.sample(n=num_winners).reset_index(drop=True)

            st.success("🎉 Winners Selected!")
            st.subheader("🏆 Winners List")
            st.dataframe(winners)

            # Save winners to lock the draw
            winners.to_excel(WINNER_FILE, index=False)

            # -------------------------------
            # DOWNLOAD WINNERS FILE
            # -------------------------------
            def to_excel(df):
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Winners")
                return buffer.getvalue()

            excel_bytes = to_excel(winners)

            st.download_button(
                label="💾 Download Winners (Excel)",
                data=excel_bytes,
                file_name="EGSA_Lottery_Winners.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ===============================
# 6️⃣ NON-ADMIN USERS
# ===============================
else:
    if password:
        st.error("❌ Invalid passcode.")
    st.info("📄 Member list is view-only. Admin authorization required to run the draw.")
