# camera_setup.py

import numpy as np
import datetime, os

def calculate_camera_recording(
    H_fov=(92 - 81) / 100,  # m, field of view height
    z_fov=27.2,             # dimensionless (z/D0)
    Q0=1.7,                 # L/min (primary jet)
    Ry=1024,                # pixels (vertical resolution)
    ds=16,                  # pixels (particle displacement)
    D0=11/1000,             # m (primary nozzle diameter)
    nu=1e-6,                # m2/s (kinematic viscosity)
    dual_jet=False,         # flag for dual-jet setup

    # Secondary jet parameters (only used if dual_jet=True)
    Q1=0.55,                # L/min (secondary jet)
    D1=1.3/1000,            # m (secondary nozzle diameter)
    L_I=0.05,               # m (horizontal spacing)
    H_I=0.10,               # m (vertical offset)
    x_fov=7.5,              # dimensionless (x/D1)

    experiment_name="single_jet_test",
    generate_report=True,
    output_dir="experiment_logs"
):
    """Calculate PIV setup and nondimensional parameters for single or dual jet experiments."""

    # --- Primary jet ---
    U0 = 4 * Q0 / (1000 * 60 * np.pi * D0**2)
    Ucz0 = 5.8 * U0 / z_fov
    Re0 = U0 * D0 / nu

    # --- Dual jet setup ---
    if dual_jet:
        U1 = 4 * Q1 / (1000 * 60 * np.pi * D1**2)
        Re1 = U1 * D1 / nu
        U1_U0 = U1 / U0
        D0_D1 = D0 / D1
        LI_D1 = L_I / D1
        HI_D0 = H_I / D0
        eps = np.sqrt(D1/D0 * U0/U1)

        # Determine dominant jet (based on higher velocity)
        Ucz1 = 5.8 * U1 / x_fov
        if Ucz1 > Ucz0:
            U_ref, dominant_jet = Ucz1, "Secondary"
        else:
            U_ref, dominant_jet = Ucz0, "Primary"
    else:
        U1 = Re1 = U1_U0 = D0_D1 = LI_D1 = HI_D0 = eps = None
        U_ref, dominant_jet = Ucz0, "Primary"

    # --- Timing calculations ---
    delta_t = ds * H_fov / (Ry * U_ref)
    sample_rate = 1 / delta_t

    # --- Summary Report ---
    summary = (
        f"--- Experiment Setup Report ---\n"
        f"Date & Time: {datetime.datetime.now()}\n"
        f"Experiment: {experiment_name}\n"
        f"{'='*40}\n"
        f"Input Parameters:\n"
        f"  H_fov     = {H_fov:.4f} m\n"
        f"  z_fov     = {z_fov:.2f} D0\n"
        f"  Ry        = {Ry} px\n"
        f"  ds        = {ds} px\n"
        f"  ν         = {nu:.2e} m²/s\n"
        f"\nPrimary Jet:\n"
        f"  Q₀        = {Q0:.2f} L/min\n"
        f"  D₀        = {D0*1000:.2f} mm\n"
        f"  U₀        = {U0:.4f} m/s\n"
        f"  U_c₀      = {Ucz0:.4f} m/s\n"
        f"  Re₀       = {Re0:.2f}\n"
    )

    if dual_jet:
        summary += (
            f"\nSecondary Jet:\n"
            f"  x_fov     = {x_fov:.2f} D1\n"
            f"  Q₁        = {Q1:.2f} L/min\n"
            f"  D₁        = {D1*1000:.2f} mm\n"
            f"  U₁        = {U1:.4f} m/s\n"
            f"  U_c₁      = {Ucz1:.4f} m/s\n"
            f"  Re₁       = {Re1:.2f}\n"
            f"\nNon-Dimensional Ratios:\n"
            f"  U₁/U₀     = {U1_U0:.3f}\n"
            f"  D₀/D₁     = {D0_D1:.3f}\n"
            f"  Lᵢ/D₁     = {LI_D1:.3f}\n"
            f"  Hᵢ/D₀     = {HI_D0:.3f}\n"
            f"  ε (sqrt(D1/D0 * U0/U1)) = {eps:.3f}\n"
        )

    summary += (
        f"\nTiming Parameters (based on {dominant_jet} jet):\n"
        f"  Reference U_c = {U_ref:.4f} m/s\n"
        f"  Δt (interframe time) = {delta_t*1e6:.2f} μs\n"
        f"  Frame rate (fps)     = {sample_rate:.2f}\n"
        f"{'='*40}\n"
    )

    # Save report
    if generate_report:
        os.makedirs(output_dir, exist_ok=True)
        fname = f"{experiment_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Report saved: {os.path.join(output_dir, fname)}")

    # Return results
    results = {
        "U0": U0, "Re0": Re0, "Uc_ref": U_ref,
        "delta_t": delta_t, "fps": sample_rate, "dominant_jet": dominant_jet
    }

    if dual_jet:
        results.update({
            "U1": U1, "Re1": Re1, "U1/U0": U1_U0,
            "D0/D1": D0_D1, "LI/DI": LI_D1, "HI/D)": HI_D0, "epsilon": eps
        })

    return results
