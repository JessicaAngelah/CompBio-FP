import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from matplotlib.animation import FuncAnimation

# Define the system of ODEs
def bacterial_dynamics(t, y, rS, rR, beta, mu, K, A):
    S, R = y  # Sensitive and Resistant bacteria populations
    dSdt = rS * S * (1 - (S + R) / K) - beta * A * S - mu * S
    dRdt = rR * R * (1 - (S + R) / K) + mu * S
    return [dSdt, dRdt]

# Simulate the dynamics
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

# GUI for interactive visualization
def update_plot():
    global animation
    A = A_slider.get()
    treatment_regimen = regimen_var.get()
    t_span = time_slider.get()
    S0 = S0_slider.get()
    R0 = R0_slider.get()
    pulse_duration = pulse_slider.get() if treatment_regimen == "Pulsed" else None

    t, S, R = simulate_dynamics(A, treatment_regimen, t_span, S0, R0, pulse_duration)

    # Clear the previous plot
    ax.clear()
    ax.set_xlabel("Time (days)", fontsize=12, labelpad=10)  # Add unit (e.g., "days")
    ax.set_ylabel("Population (cells/mL)", fontsize=12, labelpad=10)
    ax.set_title(f"Bacterial Dynamics ({treatment_regimen} Treatment, A={A:.2f}, t_span={t_span} days)", fontsize=14, pad=15)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.7)

    # Initialize the animation with a faster interval
    animation = FuncAnimation(fig, animate, frames=len(t), fargs=(t, S, R), repeat=False, interval=10)  # Reduced interval
    canvas.draw()

def animate(frame, t, S, R):
    # Animate the red and blue lines
    ax.clear()
    ax.plot(t[:frame], S[:frame], label="Sensitive Bacteria (S)", color="blue", linewidth=2)
    ax.plot(t[:frame], R[:frame], label="Resistant Bacteria (R)", color="red", linewidth=2)
    ax.set_xlabel("Time (days)", fontsize=12, labelpad=10)
    ax.set_ylabel("Population (cells/mL)", fontsize=12, labelpad=10)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.7)

def toggle_pulse_slider(*args):
    if regimen_var.get() == "Pulsed":
        pulse_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        pulse_slider.grid(row=5, column=1, padx=10, pady=5)
    else:
        pulse_label.grid_remove()
        pulse_slider.grid_remove()

# Create the main window
root = tk.Tk()
root.title("Bacterial Dynamics Simulation")
root.geometry("900x1100")
root.configure(bg="#f8f9fa")

# Title Label
title_label = tk.Label(root, text="Bacterial Dynamics Simulation", font=("Helvetica", 18, "bold"), bg="#f8f9fa", fg="#212529")
title_label.pack(pady=10)

# Create the figure for plotting
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("#f8f9fa")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(pady=10)

# Control Frame
control_frame = tk.Frame(root, bg="#f8f9fa")
control_frame.pack(pady=10)

# Antibiotic concentration slider
A_label = tk.Label(control_frame, text="Antibiotic Concentration (A, mg/L):", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
A_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
A_slider = tk.Scale(control_frame, from_=0, to=2, resolution=0.1, orient="horizontal", length=300, bg="#e9ecef", fg="#212529")
A_slider.set(0.5)
A_slider.grid(row=0, column=1, padx=10, pady=5)

# Time range slider
time_label = tk.Label(control_frame, text="Simulation Time Range (t, days):", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
time_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
time_slider = tk.Scale(control_frame, from_=10, to=100, resolution=5, orient="horizontal", length=300, bg="#e9ecef", fg="#212529")
time_slider.set(50)
time_slider.grid(row=1, column=1, padx=10, pady=5)

# Initial sensitive bacteria population slider
S0_label = tk.Label(control_frame, text="Initial Sensitive Bacteria (S0, cells/mL):", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
S0_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
S0_slider = tk.Scale(control_frame, from_=0, to=1000, resolution=50, orient="horizontal", length=300, bg="#e9ecef", fg="#212529")
S0_slider.set(900)
S0_slider.grid(row=2, column=1, padx=10, pady=5)

# Initial resistant bacteria population slider
R0_label = tk.Label(control_frame, text="Initial Resistant Bacteria (R0, cells/mL):", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
R0_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
R0_slider = tk.Scale(control_frame, from_=0, to=1000, resolution=50, orient="horizontal", length=300, bg="#e9ecef", fg="#212529")
R0_slider.set(100)
R0_slider.grid(row=3, column=1, padx=10, pady=5)

# Treatment regimen dropdown menu
regimen_label = tk.Label(control_frame, text="Treatment Regimen:", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
regimen_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
regimen_var = tk.StringVar(value="Continuous")
regimen_var.trace_add("write", toggle_pulse_slider)
regimen_menu = ttk.Combobox(control_frame, textvariable=regimen_var, values=["Continuous", "Pulsed"], state="readonly", font=("Helvetica", 10))
regimen_menu.grid(row=4, column=1, padx=10, pady=5)

# Pulse duration slider (initially hidden)
pulse_label = tk.Label(control_frame, text="Pulse Duration (days):", font=("Helvetica", 12), bg="#f8f9fa", fg="#212529")
pulse_slider = tk.Scale(control_frame, from_=1, to=10, resolution=1, orient="horizontal", length=300, bg="#e9ecef", fg="#212529")
pulse_slider.set(5)

# Update button
update_button = tk.Button(root, text="Update Plot", command=update_plot, font=("Helvetica", 12, "bold"), bg="#FF92A5", fg="white", relief="raised", borderwidth=2)
update_button.pack(pady=20)

root.mainloop()
