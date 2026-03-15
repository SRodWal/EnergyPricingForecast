import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def fourier_coeffs_real_signal(x: np.ndarray):
    x = np.asarray(x, dtype=float)
    N = x.size
    X = np.fft.fft(x)

    K = N // 2
    a = np.zeros(K + 1, dtype=float)
    b = np.zeros(K + 1, dtype=float)

    # a0
    a[0] = X[0].real / N
    b[0] = 0.0

    # 1..K-1 (even) or 1..K (odd)
    upper = K if (N % 2 == 0) else (K + 1)
    for n in range(1, upper):
        a[n] = 2.0 * X[n].real / N
        b[n] = -2.0 * X[n].imag / N

    # Nyquist if even
    if N % 2 == 0:
        a[K] = X[K].real / N
        b[K] = 0.0

    return float(a[0]), a, b


def reconstruct_from_coeffs(N: int, a: np.ndarray, b: np.ndarray, max_harmonic: int = None):
    K = len(a) - 1
    if max_harmonic is None:
        max_harmonic = K
    max_harmonic = min(max_harmonic, K)

    t = np.arange(N)
    y = np.full(N, a[0], dtype=float)

    for n in range(1, max_harmonic + 1):
        y += a[n] * np.cos(2.0 * np.pi * n * t / N) + b[n] * np.sin(2.0 * np.pi * n * t / N)

    return y


def decompose_hourly_by_year(df: pd.DataFrame, price_col: str = "price", enforce_hourly=False):
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("df must have a DatetimeIndex.")

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]

    results = {}
    for year, g in df.groupby(df.index.year):
        g = g.copy()

        if enforce_hourly:
            full_idx = pd.date_range(
                g.index.min().floor("H"),
                g.index.max().ceil("H"),
                freq="H"
            )
            g = g.reindex(full_idx)

            # Missing handling
            g[price_col] = g[price_col].interpolate(method="time").ffill().bfill()

        x = g[price_col].to_numpy(dtype=float)
        N = len(x)
        a0, a, b = fourier_coeffs_real_signal(x)

        results[int(year)] = {
            "N": N,
            "a0": a0,
            "a": a,
            "b": b,
            "index": g.index,
            "raw": x
        }

    return results


def print_raw_and_approx(index, raw, approx, title="", n_head=24, n_tail=24, sample_n=10, seed=0):
    """
    Print a compact view of the raw series and its approximation:
    - first n_head rows
    - last n_tail rows
    - random sample of sample_n points
    - basic error metrics
    """
    s_raw = pd.Series(raw, index=index, name="raw")
    s_hat = pd.Series(approx, index=index, name="fourier_hat")
    df_view = pd.concat([s_raw, s_hat], axis=1)
    df_view["error"] = df_view["raw"] - df_view["fourier_hat"]

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    print("\n--- HEAD (primeras filas) ---")
    print(df_view.head(n_head).to_string())

    print("\n--- TAIL (últimas filas) ---")
    print(df_view.tail(n_tail).to_string())

    # random sample
    rng = np.random.default_rng(seed)
    sample_idx = rng.choice(len(df_view), size=min(sample_n, len(df_view)), replace=False)
    sample_df = df_view.iloc[np.sort(sample_idx)]

    print("\n--- RANDOM SAMPLE (muestra aleatoria) ---")
    print(sample_df.to_string())

    # metrics
    err = df_view["error"].to_numpy()
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err**2))
    mape = np.mean(np.abs(err) / np.maximum(np.abs(df_view["raw"].to_numpy()), 1e-9)) * 100

    print("\n--- ERROR METRICS ---")
    print(f"MAE : {mae:,.6f}")
    print(f"RMSE: {rmse:,.6f}")
    print(f"MAPE: {mape:,.4f}% (ojo: sensible si hay valores cercanos a 0)")

    return df_view


def plot_raw_vs_approx(index, raw, approx_20, approx_all, year, days_to_show=14):
    """
    Plot:
    1) A zoomed-in window (first N days_to_show) so you can visually compare
    2) Optionally: a full-year downsampled plot (weekly sampling) for shape
    """
    s_raw = pd.Series(raw, index=index)
    s20 = pd.Series(approx_20, index=index)
    sall = pd.Series(approx_all, index=index)

    # Zoom in: first X days
    start = s_raw.index.min()
    end = start + pd.Timedelta(days=days_to_show)
    raw_zoom = s_raw.loc[start:end]
    s20_zoom = s20.loc[start:end]
    sall_zoom = sall.loc[start:end]

    plt.figure(figsize=(14, 6))
    plt.plot(raw_zoom.index, raw_zoom.values, label="Raw", linewidth=1.0, alpha=0.8)
    plt.plot(s20_zoom.index, s20_zoom.values, label="Fourier (20 harmonics)", linewidth=2.0)
    plt.plot(sall_zoom.index, sall_zoom.values, label="Fourier (all harmonics)", linewidth=1.5, linestyle="--")
    plt.title(f"{year} | Raw vs Fourier approximation (zoom {days_to_show} days)")
    plt.xlabel("Datetime")
    plt.ylabel("Price")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Full-year (downsample for readability)
    raw_ds = s_raw.resample("7D").mean()
    s20_ds = s20.resample("7D").mean()

    plt.figure(figsize=(14, 5))
    plt.plot(raw_ds.index, raw_ds.values, label="Raw (weekly mean)", linewidth=2)
    plt.plot(s20_ds.index, s20_ds.values, label="Fourier 20 (weekly mean)", linewidth=2)
    plt.title(f"{year} | Full-year shape (weekly mean)")
    plt.xlabel("Datetime")
    plt.ylabel("Price")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Dummy demo data:
    #idx = pd.date_range("2025-01-01", "2025-12-31 23:00", freq="H")
    #rng = np.random.default_rng(0)
    #price = 50 + 10*np.sin(2*np.pi*np.arange(len(idx))/(24*7)) + 3*rng.normal(size=len(idx))
    #df = pd.DataFrame({"price": price}, index=idx)

    #Use raw data
    df_dir = r'C:\Users\serw1\OneDrive - RodWal\Professional_WorkTools\Github\EnergyPricingForecast\data\raw\hourly_prices.xlsx'
    df = pd.read_excel(df_dir, sheet_name = 'cleaned', engine = 'openpyxl') #Hours named DateTime, prices named DailyAvg_Median
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df = df.sort_values("DateTime").set_index("DateTime")
    df = df.rename(columns = {'DailyAvg_Median':'price'})
    df = df[['price']]

    

    res = decompose_hourly_by_year(df, price_col="price")

    year = 2025
    a = res[year]["a"]
    b = res[year]["b"]
    N = res[year]["N"]
    index = res[year]["index"]
    raw = res[year]["raw"]

    # Reconstruct
    y_hat_partial = reconstruct_from_coeffs(N, a, b, max_harmonic=4000)
    y_hat_all = reconstruct_from_coeffs(N, a, b)

    print(year, "N =", N, "a0 =", res[year]["a0"])
    print("First 5 a_n:", a[:5])
    print("First 5 b_n:", b[:5])

    # Print raw + approximation side-by-side (compact)
    df_compare_20 = print_raw_and_approx(
        index=index,
        raw=raw,
        approx=y_hat_partial,
        title=f"{year} | Raw vs Fourier(Partial) - compact print",
        n_head=24,
        n_tail=24,
        sample_n=12,
        seed=42
    )

    # Optionally also print the ALL-harmonics (will be almost identical)
    df_compare_all = print_raw_and_approx(
        index=index,
        raw=raw,
        approx=y_hat_all,
        title=f"{year} | Raw vs Fourier(all) - compact print",
        n_head=10,
        n_tail=10,
        sample_n=8,
        seed=7
    )

    # Plot raw vs approximations
    plot_raw_vs_approx(index, raw, y_hat_partial, y_hat_all, year=year, days_to_show=365)
    
    
    sim_df = pd.Series(
        y_hat_all,
        index=index,
        name="price_simulated"
    )

   
    coef_df = pd.DataFrame({
        "year": year,
        "n": np.arange(len(a)),
        "a_n": a,
        "b_n": b,
        "amplitude": np.sqrt(a**2 + b**2),
        "period_hours": [np.inf if n == 0 else N / n for n in range(len(a))]
    })


    sim_df.to_csv(
        rf"data\results\price_simulation_{year}.csv",
        index_label="DateTime"
    )

    coef_df.to_csv(
        rf"data\results\coef_simulation_{year}.csv",
        index_label="DateTime")
