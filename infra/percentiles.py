import marimo

__generated_with = "0.8.18"
app = marimo.App(width="medium")


@app.cell
def __():
    import scipy
    import numpy as np
    import marimo as mo
    from scipy.stats import gamma, gamma


    def p99(series, axis=1):
        return np.percentile(series, 99, method="nearest", axis=axis)

    n_series = 2

    sigmas = mo.ui.array([mo.ui.slider(1.1, 10, 0.1, label=f"Series {i} σ") for i in range(n_series)], label="Series σ")
    sigmas
    return gamma, mo, n_series, np, p99, scipy, sigmas


@app.cell
def __(gamma, mo, np, p99, sigmas):
    import math
    datapoints = 1000
    series=np.array([gamma.rvs(sigma, size=datapoints) for sigma in sigmas.value])

    combined_p99 = p99(np.concatenate(series), axis=0)

    avg_p99 = np.mean(p99(series))
    max_p99 = max(p99(series))
    avgs_p99 = p99(np.average(series, axis=0), axis=0)

    mo.md(f"""P99 of combined series: {combined_p99:.3f}\n
    Average of P99: {avg_p99:.3f}\n
    Max of individual P99: {max_p99:.3f}\n
    P99 of averages: {avgs_p99:.3f}
    """)
    return (
        avg_p99,
        avgs_p99,
        combined_p99,
        datapoints,
        math,
        max_p99,
        series,
    )


@app.cell
def __(gamma, mo, np, sigmas):
    import altair as alt
    import pandas as pd

    def hist_df(s):
        hist, bins_edges = np.histogram(s, bins=20)
        return pd.DataFrame({"count": hist, "bins": bins_edges[:-1]})

    sigma_0 = sigmas.value[0]
    X = np.linspace(*gamma.ppf([0, 0.9999], sigma_0), 1000)
    Y = gamma.pdf(X, sigma_0)
    quantiles = [0.5, 0.9, 0.95, 0.99, 0.999]
    lines = pd.DataFrame({"label": str(q), "q": q_value} for q, q_value in zip(quantiles, gamma.ppf(quantiles, sigma_0)))
    lines = pd.concat([lines, pd.DataFrame([{"label": "Mean", "q": gamma.mean(sigma_0)}])])

    mo.ui.altair_chart(
        alt.Chart(pd.DataFrame({"X": X, "Y": Y})).mark_line().encode(x="X", y="Y") + \
        alt.Chart(lines).mark_rule(size=2).encode(x="q", color=alt.Color("label")).properties(title="Gamma distribution quantiles"))
    return X, Y, alt, hist_df, lines, pd, quantiles, sigma_0


if __name__ == "__main__":
    app.run()
