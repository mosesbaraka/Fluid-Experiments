import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('classic')  # nicer background
from camera_and_flow_setup import calculate_camera_recording

st.title("Dual / Single Jet PIV Setup Calculator")

st.markdown("""
This tool is designed by *Moise Baraka*, a PhD student at Texas A&M in Dr. Scott Socolofsky's research group.
To reach out to me, please send me an email at *mbaraka@tamu.edu*.

This app calculates optimal **high-speed camera recording parameters** for single or dual jet PIV experiments.
It provides **interactive plots** showing particle displacement ($\delta_s$) vs time interval ($\Delta t$), sampling rate (fps), and flow velocity ($U_c$).
""")

# Sidebar Inputs
st.sidebar.header("Experiment Settings")
experiment_name = st.sidebar.text_input("Experiment Name", "dual_jet_test")
dual_jet = st.sidebar.checkbox("Dual Jet Configuration", value=False)

with st.sidebar.expander("Primary Jet Parameters", expanded=True):
    H_fov = st.number_input("Field of view height (m)", value=(92-81)/100)
    z_fov = st.number_input(r"$z_{\rm fov}$ ($D_0$ units)", value=27.2)
    Q0 = st.number_input("Primary flow rate $Q_0$ (L/min)", value=1.7)
    D0 = st.number_input("Primary nozzle diameter $D_0$ (m)", value=11/1000)
    Ry = st.number_input("Vertical resolution $R_y$ (px)", value=1024)
    ds = st.number_input(r"Particle displacement $\delta_s$ (px)", value=16)
    nu = st.number_input(r"Kinematic viscosity $\nu \rm (m^2/s)$", value=1e-6, format="%.3g")

if dual_jet:
    with st.sidebar.expander("Secondary Jet Parameters", expanded=True):
        Q1 = st.number_input("Secondary flow rate $Q_1$ (L/min)", value=0.55)
        D1 = st.number_input("Secondary nozzle diameter $D_1$ (m)", value=1.3/1000, format="%.3g")
        L_I = st.number_input("Horizontal spacing $L_I$ (m)", value=0.05, format="%.3g")
        H_I = st.number_input("Vertical offset $H_I$ (m)", value=0.10)
        x_fov = st.number_input(r"$x_{\rm fov}$ ($D_1$ units)", value=7.5)

if st.button("Compute Setup"):
    results, summary = calculate_camera_recording(
        H_fov=H_fov, z_fov=z_fov, Q0=Q0, Ry=Ry, ds=ds, D0=D0, nu=nu,
        dual_jet=dual_jet,
        Q1=Q1 if dual_jet else None,
        D1=D1 if dual_jet else None,
        L_I=L_I if dual_jet else None,
        H_I=H_I if dual_jet else None,
        x_fov=x_fov if dual_jet else None,
        experiment_name=experiment_name,
        generate_report=True
    )
    st.success("Setup computed successfully!")
    
    st.markdown("<h3 style='color:darkblue'>Calculated Parameters</h3>", unsafe_allow_html=True)
    # st.subheader("Calculated Parameters")
    st.table(results)
    
    # --- LaTeX Notes ---
    st.markdown("**Notes:**")
    st.latex(r"Re = \frac{Q_0}{\nu \cdot D_0}")
    st.latex(r"\Delta t = \frac{\delta_s H_{\rm fov}}{R_y \cdot U_c}, \quad fps = \frac{1}{\Delta t}")
    
    # --- PIV Plots ---
    st.markdown("<h3 style='color:darkblue'>PIV Parameter Plots</h3>", unsafe_allow_html=True)
    U_c = results['Uc_ref']

    ds_range = np.linspace(ds*0.5, ds*2, 50)  # vary displacement
    U_range = np.linspace(U_c*0.5, U_c*2, 50) # vary velocity
    
    # 1️d_s vs delta t at given U_c
    # delta_t = ds_range / U_c
    delta_t = ds_range * H_fov / (Ry * U_c)
    fig1, ax1 = plt.subplots(figsize=(6,4))
    ax1.plot(ds_range, delta_t, 'b-o')
    ax1.set_xlabel(r"$\delta_s$ (px)"); ax1.set_ylabel(r"$\Delta t$ (s)")
    ax1.set_title(r"Particle displacement $\delta_s$ vs Time Interval $\Delta t$")
    ax1.grid(True); st.pyplot(fig1)
    
    # d_s vs fps at given U_c
    fps = 1 / (delta_t)
    fig2, ax2 = plt.subplots(figsize=(6,4))
    ax2.plot(ds_range, fps, 'r-o')
    ax2.set_xlabel("$d_s$ (px)"); ax2.set_ylabel(r"$\omega$ (fps)")
    ax2.set_title(r"Particle displacement $\delta_s$ vs Sampling Rate (fps)")
    ax2.grid(True); st.pyplot(fig2)
    
    # d_s fixed vs U_c
    delta_t_fixed = results['delta_t'] #ds / U_range
    ds = delta_t_fixed * Ry * U_range/ H_fov
    fig3, ax3 = plt.subplots(figsize=(6,4))
    ax3.plot(U_range, ds, 'g-', label=rf"$\Delta t = {delta_t_fixed:.3g} s$")
    ax3.set_xlabel("$U_c$ (m/s)"); ax3.set_ylabel(r"$\delta s = \frac{\Delta t\cdot R_y \cdot U_c}{H_{\rm fov}}$")
    ax3.set_title(r"Particle displacement $\delta_s$ vs Flow Velocity $U_c$")
    ax3.legend(); ax3.grid(True); st.pyplot(fig3)

    # Create a download button
    st.markdown("""
    To save the result as a txt file, please click below.
    """)
    st.download_button(
        label="📥 Download Experiment Report",
        data=summary,  # this can also be bytes or CSV
        file_name=f"{experiment_name}_report.txt",
        mime="text/plain"
    )





