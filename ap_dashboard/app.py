# ap_dashboard/app.py
from flask import Flask, render_template, jsonify
from scipy.io import loadmat
import os

app = Flask(__name__)

MAT_FILE = os.path.join(os.path.dirname(__file__), "latest_results.mat")

def load_results():
    if not os.path.exists(MAT_FILE):
        # If file not present, return empty/default
        return {
            "t": [],
            "glucose": [],
            "insulin": [],
            "insulin_input": [],
            "meal": []
        }

    data = loadmat(MAT_FILE)

    # Use the same variable names you saved from MATLAB
    t_vec = data.get("t_vec", []).squeeze()
    g_vec = data.get("g_vec", []).squeeze()
    i_vec = data.get("i_vec", []).squeeze()
    u_vec = data.get("u_vec", []).squeeze()
    meal  = data.get("meal", []).squeeze()

    # Convert to Python lists (for JSON)
    return {
        "t": t_vec.tolist() if t_vec.size else [],
        "glucose": g_vec.tolist() if g_vec.size else [],
        "insulin": i_vec.tolist() if i_vec.size else [],
        "insulin_input": u_vec.tolist() if u_vec.size else [],
        "meal": meal.tolist() if meal.size else [],
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/results")
def api_results():
    results = load_results()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
