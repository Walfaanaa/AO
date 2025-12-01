import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os

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
    st.success(f"✅ {len(members_df)} members loaded successfully.")
    st.dataframe(members_df)
except FileNotFoundError:
    st.error("❌ AO(uqubii).xlsx file not found! Upload it to your repository or app folder.")
    st.stop()

# -------------------------------
# 3️⃣ Admin Authorization
# -------------------------------
# Check for correct secret key
if "STREAMLIT_ADMIN_PASSWORD" not in st.secrets:
    st.error("❌ Missing secret key: STREAMLIT_ADMIN_PASSWORD.\n\n"
             "➡ Go to Streamlit Cloud → App → Settings → Secrets\n"
             "Add:\n\nSTREAMLIT_ADMIN_PASSWORD = \"EGSA2025_%\"")
    st.stop()

AUTHORIZED_CODE = st.secrets["STREAMLIT_ADMIN_PASSWORD"]

password = st.text_input("Enter admin passcode to enable draw:", type="password")

# -------------------------------
# 4️⃣ Authorized Section
# -------------------------------
if password == AUTHORIZED_CODE:
    st.success("🔓 Access granted!")

    # -------------------------------
    # A. If previous winners exist → only admin reset allowed
    # -------------------------------
    if os.path.exists(WINNER_FILE):
        st.subheader("🎉 Previous Winners Already Recorded")

        prev = pd.read_excel(WINNER_FILE)
        st.dataframe(prev)

        with st.expander("⚙️ Admin Reset Options"):
            st.warning("⚠️ A previous draw exists. Resetting will allow a NEW round.")

            if st.button("🔄 Reset Winners (Admin Only)"):
                os.remove(WINNER_FILE)
                st.success("✅ Winners record cleared. Ready for a new draw.")
                st.experimental_rerun()

    # -------------------------------
    # B. No previous record → allow picking new winners
    # -------------------------------
    else:
        st.subheader("🏆 Pick Winners")

        num_winners = st.number_input(
            "Number of winners to select:",
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
                    time.sleep(0.005)
                    progress_text.text(f"Progress: {i}%")
                    progress_bar.progress(i)

                # Random selection
                winners = members_df.sample(n=num_winners).reset_index(drop=True)

                st.success("🎉 Winners Selected!")
                st.subheader("🏆 Winners List")
                st.dataframe(winners)

                # Save winners record
                winners.to_excel(WINNER_FILE, index=False)

                # Download Excel
                def convert_df_to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Winners")
                    return output.getvalue()

                excel_data = convert_df_to_excel(winners)

                st.download_button(
                    "💾 Download Winners Excel",
                    excel_data,
                    "AO_lottery_winners.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    if password:
        st.error("❌ Invalid passcode.")
    st.info("🔐 Only authorized personnel can conduct the draw.")
