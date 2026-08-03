import streamlit as st
import time

from sales import run_sales
from visits import run_visits
from attendance import run_attendance
from expiry import run_expiry


st.set_page_config(
    page_title="Farmley MT Auto Refresh",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Farmley MT Auto Refresh")

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date")

with col2:
    end_date = st.date_input("End Date")


if st.button("🚀 Refresh Data", use_container_width=True):

    overall_start = time.time()

    progress = st.progress(0)

    status = st.empty()

    results = []

    reports = [

        ("Sales", run_sales),
        ("Visits", run_visits),
        ("Attendance", run_attendance),
        ("Aging", run_expiry)

    ]

    total = len(reports)

    for i, (name, function) in enumerate(reports):

        status.write(f"Refreshing **{name}**...")

        start = time.time()

        try:

            function(
                str(start_date),
                str(end_date)
            )

            results.append(
                (
                    name,
                    "✅ Success",
                    f"{time.time()-start:.1f} sec"
                )
            )

        except Exception as e:

            results.append(
                (
                    name,
                    f"❌ {e}",
                    "-"
                )
            )

        progress.progress((i + 1) / total)

    status.success("Refresh Completed!")

    st.subheader("Results")

    st.table(
        {
            "Report": [x[0] for x in results],
            "Status": [x[1] for x in results],
            "Time": [x[2] for x in results],
        }
    )

    st.success(
        f"Completed in {time.time()-overall_start:.1f} sec"
    )