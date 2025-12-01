import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os
from dotenv import load_dotenv

# -------------------------------
# 1️⃣ Page Setup
# -------------------------------
st.set_page_config(page_title="🎟️ AO Lottery Winners", layout="wide", page_icon="🎟️")
st.title("🎟️ AO Lottery Winners App (Authorized & One-Time Draw)")
st.markdown(
    "Welcome to the **AO Lottery Winners App**. "
    "This system ensures fair, transparent, and one-time-only draws managed by authorized personnel."
)

# -------------------------------
# 2️⃣ Load Members Data
# -------------------------------
DATA_FILE = "AO(uqubii).xlsx"
WINNER_FILE = "winners_record.xlsx"

try:
    members_df = pd.read_excel(DATA_FILE)
    st.success(f"✅ {len(members_df)} members loaded successfully from admin file.")
    st.dataframe(members_df)
except FileNotFoundError:
    st.error("❌ AO(uqubii).xlsx file not found! Please upload it to your app folder or GitHub repo.")
    st.stop()

# -------------------------------
# 3️⃣ Admin Authorization
# -------------------------------
load_dotenv()  # load .env file
AUTHORIZED_CODE = os.getenv("STREAMLIT_ADMIN_PASSWORD")

if not AUTHORIZED_CODE:
    st.error("❌ STREAMLIT_ADMIN_PASSWORD is missing in your .env file!")
    st.stop()

password = st.text_input("Enter admin passcode to enable draw:", type="password")

if password == AUTHORIZED_CODE:
    st.success("Access granted! You can now enable the draw.")

    # -------------------------------
    # Admin Reset
    # -------------------------------
    if os.path.exists(WINNER_FILE):
        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A previous draw has already been conducted.")
            
            reset_clicked = st.button("🔄 Reset for New Round (Admin Only)")
            if reset_clicked:
                try:
                    os.remove(WINNER_FILE)
                    st.success("✅ Winners record deleted. Please refresh the page to start a new draw.")
                except Exception as e:
                    st.error(f"Error deleting winners file: {e}")

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
                    file_name="AO_lottery_winners.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    if password:
        st.error("❌ Invalid passcode. Access denied.")
    st.info("You can view the member list, but only authorized staff can pick winners.")
