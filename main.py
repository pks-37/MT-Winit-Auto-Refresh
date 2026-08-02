import time
from logger import log

from sales import run_sales
from visits import run_visits
from attendance import run_attendance
from expiry import run_expiry


def execute(name, function, start_date, end_date, errors):

    log(f"\nRefreshing {name}...")

    start = time.time()

    try:

        function(start_date, end_date)

        log(f"✓ {name} completed in {time.time() - start:.1f} sec")

    except Exception as e:

        errors.append(name)

        log(f"❌ {name} failed")
        log(f"Reason : {e}")


def main():

    log("=" * 60)
    log("             FARMLEY AUTO REFRESH")
    log("=" * 60)

    start_date = input("\nEnter Start Date (YYYY-MM-DD): ").strip()
    end_date = input("Enter End Date (YYYY-MM-DD): ").strip()

    overall_start = time.time()

    errors = []

    execute("Sales", run_sales, start_date, end_date, errors)
    execute("Visits", run_visits, start_date, end_date, errors)
    execute("Attendance", run_attendance, start_date, end_date, errors)
    execute("Aging", run_expiry, start_date, end_date, errors)

    log("\n" + "=" * 60)

    if errors:

        log(f"Completed with {len(errors)} error(s).\n")

        for error in errors:
            log(f"❌ {error}")

    else:

        log("✅ ALL REPORTS REFRESHED SUCCESSFULLY!")

    log(f"\n⏱ Total Time : {time.time() - overall_start:.1f} sec")
    log("=" * 60)


if __name__ == "__main__":
    main()