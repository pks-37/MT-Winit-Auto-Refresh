import os
import time
from flask import Flask, render_template, request

from sales import run_sales
from visits import run_visits
from attendance import run_attendance
from expiry import run_expiry

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        overall_start = time.time()

        reports = [
            ("Sales", run_sales),
            ("Visits", run_visits),
            ("Attendance", run_attendance),
            ("Aging", run_expiry)
        ]

        results = []

        for name, function in reports:

            start = time.time()

            try:

                function(start_date, end_date)

                results.append({
                    "name": name,
                    "status": "✅ Success",
                    "time": f"{time.time() - start:.1f} sec"
                })

            except Exception as e:

                results.append({
                    "name": name,
                    "status": f"❌ {str(e)}",
                    "time": "-"
                })

        return render_template(
            "index.html",
            completed=True,
            results=results,
            total_time=f"{time.time() - overall_start:.1f} sec"
        )

    return render_template(
        "index.html",
        completed=False
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )