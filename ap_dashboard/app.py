# ap_dashboard/app.py
from flask import Flask, render_template, jsonify
from scipy.io import loadmat
import numpy as np
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
            "meal": [],
            "target": [],
            "error": [],
        }

    data = loadmat(MAT_FILE)

    def get_arr(*keys):
        """Try multiple possible keys, return squeezed numpy array or empty array."""
        for k in keys:
            if k in data:
                return data[k].squeeze()
        return np.array([])

    t_vec   = get_arr("t_vec")
    g_vec   = get_arr("g_vec", "glucose", "G")
    i_vec   = get_arr("i_vec", "insulin", "I")
    u_vec   = get_arr("u_vec")
    meal    = get_arr("meal_vec", "meal")
    target  = get_arr("G_target_vec", "target")
    err_vec = get_arr("error_vec", "error")

    return {
        "t": t_vec.tolist() if t_vec.size else [],
        "glucose": g_vec.tolist() if g_vec.size else [],
        "insulin": i_vec.tolist() if i_vec.size else [],
        "insulin_input": u_vec.tolist() if u_vec.size else [],
        "meal": meal.tolist() if meal.size else [],
        "target": target.tolist() if target.size else [],
        "error": err_vec.tolist() if err_vec.size else [],
    }


def compute_advanced_stats(results):
    """
    Advanced analysis for artificial pancreas:
    - min / max / mean / std
    - time in range / above / below (70–180 mg/dL)
    - hypo / hyper episodes
    - integral absolute error (IAE) and integral squared error (ISE)
    """
    t = np.array(results["t"])
    g = np.array(results["glucose"])

    if g.size == 0 or t.size == 0:
        return {
            "g_min": None,
            "g_max": None,
            "g_mean": None,
            "g_std": None,
            "time_in_range_pct": None,
            "time_below_range_pct": None,
            "time_above_range_pct": None,
            "hypo_episodes": None,
            "hyper_episodes": None,
            "iae": None,
            "ise": None,
        }

    # basic stats
    g_min = float(g.min())
    g_max = float(g.max())
    g_mean = float(g.mean())
    g_std = float(g.std())

    # time step in minutes (approx)
    if t.size > 1:
        dt = float(np.mean(np.diff(t)))
    else:
        dt = 1.0
    total_time = dt * g.size  # in minutes

    low_thr = 70.0
    high_thr = 180.0

    below = g < low_thr
    inrng = (g >= low_thr) & (g <= high_thr)
    above = g > high_thr

    time_below = float(below.sum() * dt)
    time_inrng = float(inrng.sum() * dt)
    time_above = float(above.sum() * dt)

    time_below_pct = time_below / total_time * 100.0
    time_inrng_pct = time_inrng / total_time * 100.0
    time_above_pct = time_above / total_time * 100.0

    def count_episodes(mask: np.ndarray) -> int:
        if mask.size == 0:
            return 0
        # episode counted when mask goes from False -> True
        shifted = np.concatenate([[False], mask[:-1]])
        return int(np.sum(mask & ~shifted))

    hypo_episodes = count_episodes(below)
    hyper_episodes = count_episodes(above)

    # error relative to 100 mg/dL (target)
    target = 100.0
    e = g - target
    iae = float(np.sum(np.abs(e)) * dt)
    ise = float(np.sum(e**2) * dt)

    return {
        "g_min": g_min,
        "g_max": g_max,
        "g_mean": g_mean,
        "g_std": g_std,
        "time_in_range_pct": time_inrng_pct,
        "time_below_range_pct": time_below_pct,
        "time_above_range_pct": time_above_pct,
        "hypo_episodes": hypo_episodes,
        "hyper_episodes": hyper_episodes,
        "iae": iae,
        "ise": ise,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/results")
def api_results():
    results = load_results()
    return jsonify(results)


@app.route("/api/summary")
def api_summary():
    results = load_results()
    summary = compute_advanced_stats(results)
    return jsonify(summary)


if __name__ == "__main__":
    app.run(debug=True)
