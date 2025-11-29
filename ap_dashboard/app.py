# app.py
# Simple Flask dashboard to present AP_MPC MATLAB simulation results.
# Run: python -m venv venv && venv\Scripts\activate (Windows) OR source venv/bin/activate (mac/linux)
# pip install -r requirements.txt
# python app.py
from flask import Flask, render_template, send_from_directory, abort
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(APP_ROOT, "AP_MPC_results")

app = Flask(__name__, static_folder="static", template_folder="templates")

def read_readme_metrics(readme_path):
    """Parse README.txt produced by MATLAB to fetch summary metrics."""
    metrics = {"Peak glucose":"-", "Settling time":"-", "Time-in-range":"-"}
    if not os.path.exists(readme_path):
        return metrics
    try:
        with open(readme_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("peak glucose"):
                    parts = line.split(":")
                    metrics["Peak glucose"] = parts[1].strip() if len(parts)>1 else "-"
                if line.lower().startswith("settling time"):
                    parts = line.split(":")
                    metrics["Settling time"] = parts[1].strip() if len(parts)>1 else "-"
                if "time-in-range" in line.lower():
                    parts = line.split(":")
                    metrics["Time-in-range"] = parts[1].strip() if len(parts)>1 else "-"
    except Exception as e:
        print("Error reading README:", e)
    return metrics

@app.route("/")
def index():
    # check results directory
    if not os.path.exists(RESULTS_DIR):
        return render_template("index.html", error="AP_MPC_results folder not found. Run the MATLAB script first to produce results.", plots=[], metrics={})
    # list expected plot filenames
    plots = []
    for name in ["glucose_plot.png", "insulin_plot.png", "meal_plot.png"]:
        p = os.path.join(RESULTS_DIR, name)
        if os.path.exists(p):
            plots.append(name)
    # read README metrics
    readme_path = os.path.join(RESULTS_DIR, "README.txt")
    metrics = read_readme_metrics(readme_path)
    # check zip file
    zip_present = os.path.exists(os.path.join(RESULTS_DIR, "AP_MPC_submission.zip"))
    return render_template("index.html", plots=plots, metrics=metrics, zip_present=zip_present)

@app.route("/results/<path:filename>")
def serve_results(filename):
    """Serve files from AP_MPC_results directory (plots + zip)."""
    safe_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(safe_path):
        abort(404)
    return send_from_directory(RESULTS_DIR, filename, as_attachment=(filename.endswith(".zip")))

if __name__ == "__main__":
    # Run dev server
    app.run(host="127.0.0.1", port=5000, debug=False)
