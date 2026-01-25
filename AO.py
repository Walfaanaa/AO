import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os
from dotenv import load_dotenv

# -------------------------------
# 1️⃣ Page Setup
# -------------------------------
st.set_page_config(
    page_title="🎟️ EGSA Lottery Winners",
    layout="wide",
    page_icon="🎟️"
)

st.title("🎟️ EGSA Lottery Winners App (Authorized & One-Time Draw)")
st.markdown(
    "Welcome to the **EGSA Lottery Winners App**. "
    "This system ensures fair, transparent, and one-time-only draws managed by authorized personnel."
)

# -------------------------------
# 2️⃣ Load Members Data
# -------------------------------
DATA_FILE = "AO_uqubii.xlsx"  # Your actual data file
WINNER_FILE = "winners_record.xlsx"

try:
    members_df = pd.read_excel(DATA_FILE)
    st.success(f"✅ {len(members_df)} members loaded successfully from {DATA_FILE}.")
    st.dataframe(members_df)
except FileNotFoundError:
    st.error(f"❌ {DATA_FILE} file not found! Please upload it to your app folder or GitHub repo.")
    st.stop()

# -------------------------------
# 3️⃣ Admin Authorization
# -------------------------------
# Hybrid password: Cloud secret or local .env
def get_admin_password():
    try:
        # Try Cloud secret first
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        # Fallback to local .env
        load_dotenv()
        return os.getenv("STREAMLIT_ADMIN_PASSWORD")

AUTHORIZED_CODE = get_admin_password()

if AUTHORIZED_CODE is None:
    st.warning("⚠️ Admin password not set! Add it to Streamlit Secrets (Cloud) or .env (local).")
    
password = st.text_input("Enter admin passcode to enable draw:", type="password")

if password == AUTHORIZED_CODE:
    st.success("Access granted! You can now enable the draw.")

    # -------------------------------
    # Admin Reset
    # -------------------------------
    if os.path.exists(WINNER_FILE):
        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A previous draw has already been conducted.")
            if st.button("🔄 Reset for New Round (Admin Only)"):
                os.remove(WINNER_FILE)
                st.success("✅ Winners record deleted. You can now run a new draw.")
                st.experimental_rerun()

        # Show previous winners
        previous_winners = pd.read_excel(WINNER_FILE)
        st.subheader("🎉 Previous Winners")
        st.dataframe(previous_winners)

    # -------------------------------
    # Pick Winners
    # -------------------------------
    else:
        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        if st.button("🎲 Pick Winners"):
            placeholder = st.empty()
            with placeholder.container():
                st.info("Picking winners... Please wait.")
                progress_text = st.empty()
                progress_bar = st.progress(0)
                for i in range(101):
                    time.sleep(0.01)
                    progress_text.text(f"Progress: {i}%")
                    progress_bar.progress(i)

                winners = members_df.sample(n=num_winners).reset_index(drop=True)
                st.success("🎉 Winners Selected!")
                st.subheader("🎉 Winners List")
                st.dataframe(winners)

                # Save winners record
                winners.to_excel(WINNER_FILE, index=False)

                # Download winners
                def convert_df_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Winners")
                    return output.getvalue()

                excel_data = convert_df_to_excel(winners)

                st.download_button(
                    label="💾 Download Winners as Excel",
                    data=excel_data,
                    file_name="EGSA_lottery_winners.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

elif password:
    st.error("❌ Invalid passcode. Access denied.")
    st.info("You can view the member list, but only authorized staff can pick winners.")
