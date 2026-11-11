# Mathematical & Fixed-Point Precision Analysis
## FPGA-Based Smart Grid FDI Anomaly Detection Engine

**Document Version:** 1.0.0  
**Design Phase:** Stage 1 — Mathematical Derivation & Word-Length Verification  
**Standard:** Signed Two's Complement Fixed-Point Arithmetic  

---

## 1. Fixed-Point Representation Fundamentals

In signed two's complement fixed-point notation, a real number $X \in \mathbb{R}$ is represented by a $W$-bit signed integer $A \in [-2^{W-1}, 2^{W-1}-1]$ such that:
$$X \approx A \cdot 2^{-F}$$
Where:
- $W$ is the total word length in bits.
- $F$ is the number of fractional bits.
- $I = W - F - 1$ is the number of integer magnitude bits (excluding the 1 sign bit).
- Notation: **$QI.F$** or signed **$(W, F)$**.
- The Least Significant Bit (LSB) quantization step size is $\Delta = 2^{-F}$.
- The representable dynamic range is:
$$X \in \left[ -2^{I}, \, 2^{I} - 2^{-F} \right]$$

---

## 2. Derivation of Intermediate Widths & Dynamic Ranges

We rigorously evaluate the provisional format specification across every arithmetic stage in the hardware datapath for $N = 4$ dimensions.

### Summary Specification Table

| Signal Name | Format | Total Bits ($W$) | Sign Bits | Integer Bits ($I$) | Fractional Bits ($F$) | LSB Step ($\Delta$) | Minimum Value ($X_{\min}$) | Maximum Value ($X_{\max}$) |
|---|---|---|---|---|---|---|---|---|
| **Normalized Residual ($r$)** | `Q4.12` | 16 | 1 | 3 | 12 | $2.4414 \times 10^{-4}$ | $-8.0$ | $+7.999755$ |
| **Inverse Covariance ($W_{ij}$)** | `Q6.10` | 16 | 1 | 5 | 10 | $9.7656 \times 10^{-4}$ | $-32.0$ | $+31.999023$ |
| **Matrix Mult Product ($P_{ij}$)** | `Q10.22` | 32 | 1 | 9 | 22 | $2.3842 \times 10^{-7}$ | $-512.0$ | $+511.999999$ |
| **MVM Accumulator ($y_i$)** | `Q12.22` | 34 | 1 | 11 | 22 | $2.3842 \times 10^{-7}$ | $-2048.0$ | $+2047.999999$ |
| **Quadratic Product ($Q_i$)** | `Q16.34` | 50 | 1 | 15 | 34 | $5.8208 \times 10^{-11}$ | $-32768.0$ | $+32767.999999$ |
| **Final Mahalanobis Acc ($D_M^2$)**| `Q18.34` | 52 | 1 | 17 | 34 | $5.8208 \times 10^{-11}$ | $-131072.0$ | $+131071.999999$ |
| **CUSUM State ($S^+ / S^-$)** | `Q16.16` | 32 | 1 | 15 | 16 | $1.5259 \times 10^{-5}$ | $-32768.0$ | $+32767.999985$ |

---

## 3. Mathematical Verification of Each Pipeline Stage

### Stage 1: Normalized Residual $r_i$ (`Q4.12`, 16-bit)
- **Physical Meaning:** Standardized deviation score $r_i = \frac{x_i - \mu_i}{\sigma_i}$.
- **Statistical Distribution:** Under $\mathcal{H}_0$, $r_i \sim \mathcal{N}(0, 1)$.
- **Dynamic Range:**
  - $3\sigma$ coverage: $\pm 3.0$ ($99.73\%$ of normal observations).
  - $6\sigma$ coverage: $\pm 6.0$ ($99.9999998\%$ of normal observations).
  - The format range $[-8.0, +7.999755]$ covers up to **$8.0$ standard deviations** before clipping.
- **Quantization Noise:** $\sigma_q^2 = \frac{\Delta^2}{12} = \frac{(2^{-12})^2}{12} \approx 4.967 \times 10^{-9}$. Signal-to-Quantization-Noise Ratio (SQNR) exceeds $83\text{ dB}$.

### Stage 2: Precision Matrix Coefficients $W_{ij}$ (`Q6.10`, 16-bit)
- **Physical Meaning:** Elements of the inverse correlation/covariance matrix $W = \Sigma^{-1}$.
- **Dynamic Range:**
  - For normalized residuals, the diagonal elements of $\Sigma$ are $1.0$, and off-diagonal correlations $|\rho_{ij}| < 1.0$.
  - In power systems, high correlation between adjacent bus voltages ($\rho \approx 0.95$) yields inverse matrix diagonal elements $W_{ii} \approx \frac{1}{1 - \rho^2} \approx 10.2$.
  - Range $[-32.0, +31.999]$ comfortably accommodates even strongly correlated bus pairs with condition numbers $\kappa(\Sigma) \le 50$.

### Stage 3: Matrix Multiplication Product $P_{ij} = W_{ij} \times r_j$
- Multiplicands: $W_{ij}$ (`Q6.10`, 16-bit signed) $\times$ $r_j$ (`Q4.12`, 16-bit signed).
- Mathematical multiplication of two two's complement numbers:
  - Sign bits: $1 + 1 - 1 = 1$ sign bit.
  - Integer bits: $5 + 3 + 1 = 9$ integer bits.
  - Fractional bits: $10 + 12 = 22$ fractional bits.
  - Total product width: $16 + 16 = 32$ bits (`Q10.22`).
- Extreme product values:
  - $(-32.0) \times (-8.0) = +256.0$.
  - The positive limit of `Q10.22` is $+511.999999$.
  - **Conclusion:** Mathematical overflow during full-precision multiplication is **physically impossible**.

### Stage 4: Accumulator Guard Bits & $y_i = \sum_{j=1}^{N} P_{ij}$
- Accumulating $N = 4$ independent products:
$$\text{Guard Bits} = \lceil \log_2(N) \rceil = \lceil \log_2(4) \rceil = 2\text{ bits}$$
- Accumulator width: $32\text{ bits} + 2\text{ guard bits} = 34\text{ bits}$ (`Q12.22`).
- Maximum possible sum: $4 \times 256.0 = 1024.0$.
- Representable maximum of `Q12.22` is $+2047.999999$.
- **Conclusion:** $y_i$ accumulation is **100% immune to overflow**.

### Stage 5: Quadratic Multiplication $Q_i = r_i \times y_i$
- Multiplicands: $r_i$ (`Q4.12`, 16-bit) $\times$ $y_i$ (`Q12.22`, 34-bit).
- Resulting format:
  - Total bits: $16 + 34 = 50$ bits.
  - Fractional bits: $12 + 22 = 34$ bits.
  - Sign + Integer bits: $4 + 12 = 16$ bits (`Q16.34`).
- Extreme values: $8.0 \times 1024.0 = 8192.0$.
- Representable maximum of `Q16.34` is $+32767.999999$.
- **Conclusion:** Zero overflow risk.

### Stage 6: Final Mahalanobis Accumulator $D_M^2 = \sum_{i=1}^{N} Q_i$
- Accumulating $N = 4$ quadratic products:
$$\text{Guard Bits} = \lceil \log_2(4) \rceil = 2\text{ bits}$$
- Accumulator width: $50\text{ bits} + 2\text{ bits} = 52\text{ bits}$ (`Q18.34`).
- Theoretical properties:
  - Because $W$ is symmetric positive-definite, $D_M^2 = r^T W r \ge 0$ is strictly non-negative.
  - Under $\mathcal{H}_0$, $D_M^2 \sim \chi_4^2$, with mean $\mathbb{E}[D_M^2] = 4.0$ and variance $\mathrm{Var}(D_M^2) = 2 \times 4 = 8$.
  - Detection threshold at $\alpha = 10^{-4}$ is $T^2 = \chi_4^2(0.9999) = 23.51$.
  - Accumulator range is $[0, 131071.999999]$, providing $> 5000\times$ dynamic headroom above the detection threshold.

---

## 4. Safely Converting Mahalanobis Distance to CUSUM Input

The CUSUM engine requires scalar input $z[n] = D_M^2[n]$ in **`Q16.16`** format (32-bit signed).

```
D_M² Accumulator: Q18.34 (52 bits)
[51]        [50:34]                [33:18]                 [17:0]
Sign (1b)   Integer (17b)          High Frac (16b)         Low Frac (18b)
    │            │                        │                      │
    │      Check Overflow                 │                 Round Bit (bit 17)
    │      (Bits [50:49])                 │                      │
    ▼            ▼                        ▼                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Saturate if D_M² > 32767.99998: Output = 32'sh7FFF_FFFF               │
│  Clamp if D_M² < 0:              Output = 32'sh0000_0000               │
│  Normal:                         Output = [49:18] + round_bit          │
└────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                         CUSUM Input (Q16.16)
```

### Quantization & Rounding Policy:
1. **Rounding:** Add convergent rounding offset $2^{-17}$ (bit 17) before discarding the lower 18 fractional bits.
2. **Integer Truncation & Saturation:**
   - `Q18.34` has 17 integer bits; `Q16.16` has 15 integer bits.
   - If bits `[50:49]` are non-zero (meaning $D_M^2 \ge 32768.0$), saturate to `32'sh7FFF_FFFF` ($+32767.99998$).
   - Since $T^2 \sim 23.5$, any sample exceeding $32768.0$ represents an astronomical $1000\sigma$ cyber-attack, where saturation preserves the positive alert trigger without register wrap-around.
   - If sign bit `[51]` is asserted (due to precision noise near zero), clamp to `32'sh0000_0000`.

---

## 5. CUSUM Detection Engine Arithmetic & Guarding

The two-sided recursive CUSUM equations are:
$$S^+(n) = \max\left(0, \, S^+(n-1) + z(n) - \nu_0 - k\right)$$
$$S^-(n) = \max\left(0, \, S^-(n-1) - (z(n) - \nu_0 + k)\right)$$

### Arithmetic Safety in `Q16.16`:
1. **Precomputed Slack Offsets:**
   - Offset positive: $\Delta^+_{\text{offset}} = \nu_0 + k$ (Constant in `Q16.16`).
   - Offset negative: $\Delta^-_{\text{offset}} = \nu_0 - k$ (Constant in `Q16.16`).
2. **Intermediate Subtraction Guarding:**
   - $z(n) \in [0, 32767]$, $\nu_0 \approx 4.0$, $k \approx 1.0$.
   - Difference term $z(n) - (\nu_0 + k) \in [-5.0, +32762.0]$.
   - Addition $S^+(n-1) + \Delta$: A 34-bit signed temporary sum prevents wrap-around before the non-negative clamping $\max(0, \cdot)$ and saturation at $+32767.99998$.

---

## 6. Adjustments to Provisional Formats

All provisional formats proposed in the project specification are **theoretically validated and confirmed**. 

No bit-width reductions are recommended because:
1. The 16-bit operands ($r_i$ in `Q4.12` and $W_{ij}$ in `Q6.10`) map directly into a single input port of AMD/Xilinx DSP48 slices ($18 \times 25$ multiplier), ensuring minimum resource utilization and single-cycle DSP pipelining.
2. Full intermediate precision is maintained through the 52-bit accumulator, guaranteeing zero truncation error in the inner loop.

