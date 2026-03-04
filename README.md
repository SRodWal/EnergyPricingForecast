# Long-Term Electricity Price Forecasting
**Fourier Decomposition + Gaussian Process Regression**

This repository implements and replicates the methodology proposed in:

> **Gabrielli, P., Wüthrich, M., Blume, S., & Sansavini, G. (2022)**  
> *Data-driven modeling for long-term electricity price forecasting*  
> Energy, 244, 123107.

The objective is to generate **hourly-resolved electricity price scenarios over long-term horizons (years to decades)** using only **annual price drivers**, while preserving realistic intraday, weekly, and seasonal price dynamics.

---

## 1. Conceptual Overview

Electricity prices exhibit:
- Strong **hourly volatility**
- Weak correlation with fundamentals at high resolution
- Strong correlation with fundamentals at **annual resolution**

This project addresses this mismatch by separating prices into:

1. **Base evolution**  
   Captured by a small number of dominant Fourier frequencies  
   (annual, weekly, daily, intraday patterns)

2. **Volatility and extremes**  
   Captured via residuals sampled from historical hourly price data

### High-level workflow

1. Decompose historical hourly prices (per year) using a Discrete Fourier Transform (DFT)
2. Identify dominant frequencies representing base price dynamics
3. Regress annual Fourier coefficients on annual price drivers
4. Reconstruct future hourly prices from predicted coefficients
5. Superimpose sampled historical residuals
6. (Optional) Propagate uncertainty via Monte Carlo simulation

This approach produces **realistic hourly price profiles** suitable for:
- Renewable project valuation
- Merchant risk analysis (P50 / P90)
- Long-term energy system studies

---

## 2. Repository Structure

```text
src/ltppf/
├─ fourier/        # DFT, dominant frequency selection, reconstruction
├─ models/         # Regression models (GPR, linear, ANN)
├─ residuals/      # Residual extraction and sampling
├─ uncertainty/    # Driver uncertainty + Monte Carlo
├─ evaluation/     # Metrics and cross-validation
├─ pipeline/       # Training and prediction pipelines
└─ cli.py          # Command-line interface
```

---

## 3. Data Requirements

a. Hourly Electric Prices
- Wholesale Hourly Prices
- 3 to 5 consecutive years
- Consistent Market / Spot Market
- Leap years to be standardized to 8760 h/yr

b. Annual Price Divers:
- Annual Electric Demand/Generation
- Annual Generation by technology
- Fuel/Oil/Gas/Coal/LPG prices:
```
year	total_generation	solar_gen	bunker_gen	hydro_gen	eolic_gen	crude_prices
2019						
2020						
2021						
```
---

## 4. Methodology Details

### 4.1 Fourier decomposition

For each year, hourly electricity prices $p_t$ are decomposed as:

$$p_t = a_0 + \sum_{n=1}^{N/2} \left[a_n \cos\left(\frac{2\pi n t}{N}\right) + b_n \sin\left(\frac{2\pi n t}{N}\right) \right]$$

Where:
- $N = 8760$ is the number of hours in a year  
- $a_0$ is the annual mean electricity price  
- $a_n$ and $b_n$ are Fourier coefficients associated with frequency $n$

### 4.2 Dominant frequency selection

Frequencies are ranked by amplitude:

$$A_n= \sqrt{a_n^2 + b_n^2} ;  A_n^2​=a_n^2​+b_n^2​​ $$

A small subset of frequencies is selected to represent the base price evolution
(e.g. annual, weekly, daily, intraday components).

### 4.3 Regression model

-Single-output Gaussian Process Regression (GPR)
-One model per Fourier coefficient
-Inputs: annual price drivers
-Targets: annual Fourier coefficients
-Validation: leave-one-year-out cross-validation
-Metric: MAPE on reconstructed hourly base price

### 4.4 Price reconstruction

Future hourly prices are generated as:

$$
p_t^{\text{future}} = f_t^{\text{predicted}} + R_t^{\text{sampled}}
$$

Where:
- $f_t​$: reconstructed base evolution from predicted Fourier coefficients
- $R_t​$: residual profile sampled from historical years

---