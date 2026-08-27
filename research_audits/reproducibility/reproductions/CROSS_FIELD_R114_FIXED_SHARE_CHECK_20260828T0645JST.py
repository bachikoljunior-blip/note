import itertools
import math
import random

J = 3
T = 300
K_SWITCHES = 3
B = 25.0 / 9.0
ALPHA_SWITCH = K_SWITCHES / (T - 1)
C = (
    math.log(J)
    + (T - K_SWITCHES - 1) * math.log(1.0 / (1.0 - ALPHA_SWITCH))
    + K_SWITCHES * (math.log(1.0 / ALPHA_SWITCH) + math.log(J - 1))
)
ETA_HOEFFDING = math.sqrt(8.0 * C / T)
WORST_CASE_NORMALIZED = C / ETA_HOEFFDING + ETA_HOEFFDING * T / 8.0
WORST_CASE_VARIANCE = B * WORST_CASE_NORMALIZED

print("alpha_switch", ALPHA_SWITCH)
print("C", C)
print("eta_hoeffding", ETA_HOEFFDING)
print("worst_case_normalized", WORST_CASE_NORMALIZED)
print("worst_case_variance", WORST_CASE_VARIANCE)

# Independent arithmetic reconstruction of source aggregate values.
mean_C = 19.3076
mean_delta = 0.65784
mean_bound = mean_C / 16.0 + mean_delta
print("aggressive_mean_bound_normalized", mean_bound)
print("aggressive_mean_bound_variance_units", B * mean_bound)
print("aggressive_gap_vs_oracle_pct", (187.912813 / 184.594188 - 1.0) * 100.0)
print("aggressive_improvement_vs_fixed_eps06_pct", (1.0 - 187.912813 / 215.495571) * 100.0)
print("aggressive_improvement_vs_all_base_pct", (1.0 - 187.912813 / 199.6) * 100.0)

# Fixed Share has multiple common parameterizations.  The audited path-prior
# convention switches away from the current expert with total probability a,
# so each other expert receives a/(J-1).  The public opera package instead
# uses w_new=(1-a_opera)*v + a_opera/J, which has effective switch probability
# a_opera*(J-1)/J.  Convert parameters before comparing or replaying.
ALPHA_OPERA_EQUIV = ALPHA_SWITCH * J / (J - 1)
print("opera_alpha_equivalent", ALPHA_OPERA_EQUIV)

C_same_alpha_opera = (
    math.log(J)
    - (T - K_SWITCHES - 1) * math.log(1.0 - ALPHA_SWITCH + ALPHA_SWITCH / J)
    - K_SWITCHES * math.log(ALPHA_SWITCH / J)
)
print("C_if_opera_uses_same_numeric_alpha", C_same_alpha_opera)

# Deterministic independent finite-horizon check of the exact HMM/mixability
# identity and pathwise certificate on an unrelated synthetic bounded-loss
# sequence.  This is a structural reproduction of the theorem, not a replay
# of the worker's 300/1000-replicate rare-event simulation.
rng = random.Random(202608280645)
small_T = 7
eta = 4.2
alpha = 0.17
losses = [[rng.random() for _ in range(J)] for _ in range(small_T)]
weights = [1.0 / J] * J
H = 0.0
M = 0.0
Delta = 0.0
for t in range(small_T):
    h = sum(weights[j] * losses[t][j] for j in range(J))
    z = sum(weights[j] * math.exp(-eta * losses[t][j]) for j in range(J))
    m = -math.log(z) / eta
    H += h
    M += m
    Delta += h - m
    posterior = [weights[j] * math.exp(-eta * losses[t][j]) / z for j in range(J)]
    if t < small_T - 1:
        weights = [
            (1.0 - alpha) * posterior[j]
            + alpha / (J - 1) * (1.0 - posterior[j])
            for j in range(J)
        ]

path_partition = 0.0
max_certificate_violation = -1e300
for path in itertools.product(range(J), repeat=small_T):
    prior = 1.0 / J
    switches = 0
    path_loss = 0.0
    for t in range(small_T):
        path_loss += losses[t][path[t]]
        if t < small_T - 1:
            if path[t + 1] == path[t]:
                prior *= 1.0 - alpha
            else:
                prior *= alpha / (J - 1)
                switches += 1
    path_partition += prior * math.exp(-eta * path_loss)
    path_code = (
        math.log(J)
        + (small_T - switches - 1) * math.log(1.0 / (1.0 - alpha))
        + switches * (math.log(1.0 / alpha) + math.log(J - 1))
    )
    violation = (H - path_loss) - (path_code / eta + Delta)
    max_certificate_violation = max(max_certificate_violation, violation)

M_enum = -math.log(path_partition) / eta
print("small_H", H)
print("small_M_forward", M)
print("small_M_enumerated", M_enum)
print("small_Delta", Delta)
print("small_H_minus_M_minus_Delta", H - M - Delta)
print("small_max_certificate_violation", max_certificate_violation)

assert abs(C - 19.968446928236975) < 1e-12
assert abs(ETA_HOEFFDING - 0.7297204383093017) < 1e-12
assert abs(WORST_CASE_VARIANCE - 152.02509131443784) < 1e-10
assert abs(M - M_enum) < 1e-12
assert abs(H - M - Delta) < 1e-12
assert max_certificate_violation <= 1e-12
