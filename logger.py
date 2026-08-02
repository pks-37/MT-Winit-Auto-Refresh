from pathlib import Path
from datetime import datetime

log_folder = Path("logs")
log_folder.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

log_file = log_folder / f"{timestamp}.log"


def log(message):

    print(message)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")