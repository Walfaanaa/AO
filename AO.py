import streamlit as st
import pandas as pd
import os
import time
from io import BytesIO
from datetime import datetime

# ==================================================
# 1️⃣ PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="🎟️ AO Lottery Winners",
    page_icon="🎟️",
    layout="wide"
)

st.title("🎟️ AO Lottery Winners App")
st.markdown("**Authorized • Secure • One-Time Lottery Draw**")

# ==================================================
# 2️⃣ FILE PATHS
# ==================================================
DATA_URL = "https://raw.githubusercontent.com/Walfaanaa/AO/main/AO_uqubii.xlsx"
WINNER_FILE = "winners_record.xlsx"

# ==================================================
# 3️⃣ LOAD MEMBERS FROM GITHUB
# ==================================================
try:
    members_df = pd.read_excel(DATA_URL)
    st.success(f"✅ {len(members_df)} members loaded successfully.")
    st.dataframe(members_df, use_container_width=True)
except Exception as e:
    st.error("❌ Failed to load member file from GitHub.")
    st.error(e)
    st.stop()

# ==================================================
# 4️⃣ ADMIN AUTHENTICATION (STREAMLIT SECRETS)
# ==================================================
try:
    ADMIN_PASSWORD = st.secrets["STREAMLIT_ADMIN_PASSWORD"]
except KeyError:
    st.error("❌ Admin password not found in Streamlit Secrets.")
    st.stop()

password = st.text_input(
    "🔐 Enter Admin Passcode",
    type="password"
)

if password != ADMIN_PASSWORD:
    if password:
        st.error("❌ Invalid passcode.")
    st.info("👀 Member list is visible, but only admin can run the draw.")
    st.stop()

st.success("✅ Admin access granted.")

# ==================================================
# 5️⃣ CHECK IF DRAW ALREADY COMPLETED
# ==================================================
if os.path.exists(WINNER_FILE):

    st.warning("⚠️ Lottery draw already completed.")

    previous_winners = pd.read_excel(WINNER_FILE)
    st.subheader("🎉 Previous Winners")
    st.dataframe(previous_winners, use_container_width=True)

    with st.expander("⚙️ Admin Reset (Danger Zone)"):
        st.warning("This will permanently delete previous winners.")
        if st.button("🔄 Reset Lottery"):
            os.remove(WINNER_FILE)
            st.success("✅ Lottery reset successfully.")
            st.rerun()

    st.stop()

# ==================================================
# 6️⃣ RUN LOTTERY DRAW (ONE-TIME)
# ==================================================
st.subheader("🎯 Run New Lottery Draw")

num_winners = st.number_input(
    "🏆 Number of winners to select",
    min_value=1,
    max_value=len(members_df),
    value=1
)

if st.button("🎲 Pick Winners"):

    progress = st.progress(0)
    status = st.empty()

    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)
        status.text(f"Drawing winners... {i + 1}%")

    winners = members_df.sample(n=num_winners).reset_index(drop=True)
    winners["Draw_Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save permanently
    winners.to_excel(WINNER_FILE, index=False)

    st.success("🎉 Winners Selected Successfully!")
    st.subheader("🏆 Winners List")
    st.dataframe(winners, use_container_width=True)

    # ==================================================
    # 7️⃣ DOWNLOAD WINNERS FILE
    # ==================================================
    def convert_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Winners")
        return output.getvalue()

    st.download_button(
        label="💾 Download Winners (Excel)",
        data=convert_to_excel(winners),
        file_name="AO_lottery_winners.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
