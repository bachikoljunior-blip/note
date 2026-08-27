"""Independent transcription/recalculation for clean-g1 C18 cross_field r86.

Reconstructs the standardized NIG predictive problem and the symmetric four-corner
null mixture from source-published formulas.  It does not import worker code.
"""
import math
import numpy as np
from scipy.special import gammaln, gamma, roots_genlaguerre, roots_hermitenorm
from scipy.stats import chi2, norm
from scipy.optimize import differential_evolution

M = 32
N_REF = 684
DF_REF = 683
KAPPA0 = 3.0
ALPHA0 = 3.0
BETA0 = 2.0

z = norm.ppf(0.995)
qlo = chi2.ppf(0.005, DF_REF)
qhi = chi2.ppf(0.995, DF_REF)
h0 = z * math.sqrt(DF_REF / qlo) / math.sqrt(N_REF)
ell0 = math.sqrt(DF_REF / qhi)
u0 = math.sqrt(DF_REF / qlo)

# q expectation: tau=1/sigma^2 ~ Gamma(alpha0, rate=beta0),
# ybar|tau ~ N(0,(1/kappa0+1/M)/tau), W*tau ~ chi2_{M-1}.
xt, wt = roots_genlaguerre(50, ALPHA0 - 1.0)
wt = wt / gamma(ALPHA0)
xu, wu = roots_hermitenorm(60)
wu = wu / math.sqrt(2.0 * math.pi)
xv, wv = roots_genlaguerre(50, (M - 1.0) / 2.0 - 1.0)
wv = wv / gamma((M - 1.0) / 2.0)

ys, ws, weights = [], [], []
for i, x in enumerate(xt):
    tau = x / BETA0
    for j, u in enumerate(xu):
        ys.append(np.full_like(xv, math.sqrt((1.0 / KAPPA0 + 1.0 / M) / tau) * u))
        ws.append((2.0 * xv) / tau)
        weights.append(wt[i] * wu[j] * wv)
ybar = np.concatenate(ys)
W = np.concatenate(ws)
qw = np.concatenate(weights)


def logp(mu, sigma):
    return (-M / 2.0 * math.log(2.0 * math.pi) - M * math.log(sigma)
            - (W + M * (ybar - mu) ** 2) / (2.0 * sigma ** 2))


log_pL = np.logaddexp(logp(-h0, ell0), logp(h0, ell0)) - math.log(2.0)
log_pU = np.logaddexp(logp(-h0, u0), logp(h0, u0)) - math.log(2.0)


def active_expectations(rho):
    log_prho = np.logaddexp(math.log(rho) + log_pL, math.log1p(-rho) + log_pU)
    eL = np.sum(qw * np.exp(log_pL - log_prho))
    eU = np.sum(qw * np.exp(log_pU - log_prho))
    return eL, eU, log_prho


lo, hi = 0.4, 0.7
for _ in range(60):
    mid = (lo + hi) / 2.0
    eL, eU, _ = active_expectations(mid)
    if eL > eU:
        lo = mid
    else:
        hi = mid
rho = (lo + hi) / 2.0
eL, eU, log_prho = active_expectations(rho)

alpha_n = ALPHA0 + M / 2.0
beta_n = BETA0 + W / 2.0 + KAPPA0 * M * ybar ** 2 / (2.0 * (KAPPA0 + M))
log_q = (-M / 2.0 * math.log(2.0 * math.pi)
         + 0.5 * math.log(KAPPA0 / (KAPPA0 + M))
         + ALPHA0 * math.log(BETA0) - alpha_n * np.log(beta_n)
         + gammaln(alpha_n) - gammaln(ALPHA0))
mu_hat = np.clip(ybar, -h0, h0)
S = W + M * (ybar - mu_hat) ** 2
sigma_hat = np.clip(np.sqrt(S / M), ell0, u0)
log_pmax = (-M / 2.0 * math.log(2.0 * math.pi) - M * np.log(sigma_hat)
            - S / (2.0 * sigma_hat ** 2))

elog_ui = np.sum(qw * (log_q - log_pmax))
elog_rho = np.sum(qw * (log_q - log_prho))


def C(mu, sigma):
    return float(np.sum(qw * np.exp(logp(mu, sigma) - log_prho)))


opt = differential_evolution(lambda x: -C(x[0], x[1]),
                             [(0.0, h0), (ell0, u0)], seed=12345,
                             popsize=12, maxiter=100, tol=1e-9, polish=True)

print({
    "h0": h0,
    "ell0": ell0,
    "u0": u0,
    "rho": rho,
    "active_low": eL,
    "active_high": eU,
    "Elog_UI": elog_ui,
    "Elog_four_corner": elog_rho,
    "gain_nat_per_block": elog_rho - elog_ui,
    "numerical_C_max": -opt.fun,
    "numerical_C_argmax_mu_sigma": opt.x.tolist(),
    "note": "The optimizer result is numerical evidence only, not a continuum proof."
})
