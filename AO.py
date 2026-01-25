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

st.title("🎟️ EGSA Lottery Winners App (Authorized & One-Time Draw)")
st.markdown(
    "Welcome to the **EGSA Lottery Winners App**. "
    "This system ensures **fair, transparent, and one-time-only draws** "
    "managed by **authorized personnel**."
)

# ===============================
# 2️⃣ FILE PATHS
# ===============================
DATA_FILE = "members_data.xlsx"
WINNER_FILE = "winners_record.xlsx"

# ===============================
# 3️⃣ LOAD MEMBERS DATA
# ===============================
try:
    members_df = pd.read_excel(DATA_FILE)
    st.success(f"✅ {len(members_df)} members loaded successfully.")
    st.dataframe(members_df)
except FileNotFoundError:
    st.error("❌ members_data.xlsx not found. Upload it to your app folder or GitHub repo.")
    st.stop()

# ===============================
# 4️⃣ ADMIN AUTHORIZATION (SECURE)
# ===============================
try:
    AUTHORIZED_CODE = st.secrets["ADMIN_PASSWORD"]
except KeyError:
    st.error("❌ Admin password not configured in Streamlit secrets.")
    st.stop()

password = st.text_input("🔐 Enter admin passcode to enable draw:", type="password")

# ===============================
# 5️⃣ AUTHORIZED ACCESS
# ===============================
if password == AUTHORIZED_CODE:
    st.success("✅ Access granted. Admin controls enabled.")

    # ===============================
    # ADMIN RESET (IF DRAW EXISTS)
    # ===============================
    if os.path.exists(WINNER_FILE):
        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A draw has already been completed.")
            if st.button("🔄 Reset for New Round (Admin Only)"):
                os.remove(WINNER_FILE)
                st.success("✅ Winners record deleted. Ready for a new draw.")
                st.rerun()

        previous_winners = pd.read_excel(WINNER_FILE)
        st.subheader("🎉 Previous Winners")
        st.dataframe(previous_winners)

    # ===============================
    # PICK WINNERS (ONE TIME)
    # ===============================
    else:
        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        if st.button("🎲 Pick Winners"):
            st.info("🎰 Picking winners… please wait")

            progress_text = st.empty()
            progress_bar = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
                progress_text.text(f"Progress: {i + 1}%")

            winners = members_df.sample(n=num_winners).reset_index(drop=True)

            st.success("🎉 Winners Selected!")
            st.subheader("🏆 Winners List")
            st.dataframe(winners)

            # Save winners (lock draw)
            winners.to_excel(WINNER_FILE, index=False)

            # ===============================
            # DOWNLOAD EXCEL
            # ===============================
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="Winners")
                return output.getvalue()

            excel_data = to_excel(winners)

            st.download_button(
                "💾 Download Winners (Excel)",
                excel_data,
                file_name="EGSA_lottery_winners.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# ===============================
# 6️⃣ UNAUTHORIZED ACCESS
# ===============================
else:
    if password:
        st.error("❌ Invalid passcode. Access denied.")
    st.info("📄 Member list is view-only. Admin access required to run the draw.")
