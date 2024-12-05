import numpy as np
from scipy.integrate import solve_ivp

# Define the system of ODEs
def bacterial_dynamics(t, y, rS, rR, beta, mu, K, A):
    S, R = y  # Sensitive and Resistant bacteria populations
    dSdt = rS * S * (1 - (S + R) / K) - beta * A * S - mu * S
    dRdt = rR * R * (1 - (S + R) / K) + mu * S
    return [dSdt, dRdt]

def simulate_dynamics(A, treatment_regimen, t_span, S0, R0, pulse_duration):
    # Parameters
    rS = 1.0    # Growth rate of sensitive bacteria
    rR = 0.7    # Growth rate of resistant bacteria
    beta = 1.5  # Effectiveness of the antibiotic
    mu = 0.01   # Mutation rate
    K = 1000    # Carrying capacity

    t_eval = np.linspace(0, t_span, 500)  # Time points to evaluate

    # Antibiotic concentration over time (based on treatment regimen)
    if treatment_regimen == "Continuous":
        A_func = lambda t: A
    elif treatment_regimen == "Pulsed":
        A_func = lambda t: A if (t % (2 * pulse_duration)) < pulse_duration else 0
    else:
        raise ValueError("Unknown treatment regimen")

    # Define a wrapper for the ODE to include time-dependent A
    def ode_system(t, y):
        return bacterial_dynamics(t, y, rS, rR, beta, mu, K, A_func(t))

    # Solve the ODE
    solution = solve_ivp(ode_system, [0, t_span], [S0, R0], t_eval=t_eval)

    # Extract results
    t = solution.t
    S = solution.y[0]
    R = solution.y[1]
    return t, S, R

