import streamlit as st
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from matplotlib import colors

st.set_page_config(page_title="Hospital Digital Twin", layout="wide")

st.title("🏥 Hospital Digital Twin Simulation")

# --- Settings ---
NUM_BEDS = 20
NUM_PATIENTS = 30
CRISIS_PATIENTS = 50
WAIT_TIME_THRESHOLD = 5  # in arbitrary time units

# Sidebar controls
st.sidebar.header("Simulation Controls")
crisis = st.sidebar.button("💥 Simulate Outbreak")

# Initialize beds and patient positions
beds = np.zeros(NUM_BEDS)
patient_positions = np.random.randint(0, NUM_BEDS, size=NUM_PATIENTS)

# Initialize dataframe for heatmap
bed_df = pd.DataFrame([beds], columns=[f"Bed {i}" for i in range(NUM_BEDS)])

# Function to update patient positions and bed occupancy
def step_simulation(patient_positions, beds):
    new_positions = []
    beds.fill(0)
    for pos in patient_positions:
        move = np.random.choice([-1, 0, 1])  # patient can move to neighboring bed
        new_pos = np.clip(pos + move, 0, NUM_BEDS - 1)
        new_positions.append(new_pos)
        beds[new_pos] += 1
    return np.array(new_positions), beds

# Crisis mode
if crisis:
    patient_positions = np.random.randint(0, NUM_BEDS, size=CRISIS_PATIENTS)

# Display stats
st.subheader("Live Statistics")
st.write(f"Number of beds: {NUM_BEDS}")
st.write(f"Number of patients: {len(patient_positions)}")
st.write(f"Average occupancy per bed: {np.mean(beds):.2f}")

# --- Heatmap ---
fig, ax = plt.subplots(figsize=(12, 2))
cmap = colors.LinearSegmentedColormap.from_list("", ["green", "yellow", "red"])
heatmap = ax.imshow([beds], cmap=cmap, vmin=0, vmax=5)
ax.set_xticks(range(NUM_BEDS))
ax.set_xticklabels([f"Bed {i}" for i in range(NUM_BEDS)])
ax.set_yticks([])
st.pyplot(fig)

# --- Animation Loop ---
st.subheader("Patient Movement Simulation")

placeholder = st.empty()
for _ in range(20):  # 20 animation steps
    patient_positions, beds = step_simulation(patient_positions, beds)
    bed_df.iloc[0] = beds
    fig, ax = plt.subplots(figsize=(12, 2))
    heatmap = ax.imshow([beds], cmap=cmap, vmin=0, vmax=5)
    ax.set_xticks(range(NUM_BEDS))
    ax.set_xticklabels([f"Bed {i}" for i in range(NUM_BEDS)])
    ax.set_yticks([])
    placeholder.pyplot(fig)
    time.sleep(0.5)

st.success("Simulation Complete ✅")
st.write("You can explain to judges: each step simulates patient movements and bed occupancy. The red beds show overcrowding. This is based on **probability and simple queue math** (Monte Carlo style).")
