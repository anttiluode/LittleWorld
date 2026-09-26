import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
np.random.seed(42)
dt = 0.001          # 1 ms resolution
t_max = 4.0         # 4 seconds
time = np.arange(0, t_max, dt)
N = len(time)

# 1. Environment & Sender Sequencer
# Shared LFP-like background oscillation
lfp = 0.3 * np.sin(2 * np.pi * 4 * time) + 0.1 * np.random.randn(N)

# Sender internal drive: a continuous behavioral trajectory
internal_drive = (
    0.6 * np.sin(2 * np.pi * 0.8 * time)
    + 0.3 * np.cos(2 * np.pi * 2.1 * time)
    + 0.5
)
internal_drive = np.clip(internal_drive, 0.05, 1.2)

# 2. Spike Generation with State-Dependent Waveform Parameters
# Firing threshold driven by internal drive + LFP modulation
v_membrane = 0.0
threshold = 0.8
spike_indices = []

# Extracted waveform features per spike: [peak_sharpness, decay_lambda, peak_width]
# Grounded in Martin-Burgos et al. (2026): drive and LFP systematically alter kinetics
waveform_features = []
true_drives_at_spikes = []

# Synthetic AP template generator (linear ramp -> peak -> exp decay)
def generate_waveform(drive_val, lfp_val):
    # Higher drive & positive LFP -> sharper peak, faster repol lambda, narrower width
    sharpness = 1.5 + 1.2 * drive_val + 0.4 * lfp_val + np.random.normal(0, 0.05)
    decay_lambda = 1.0 + 1.8 * drive_val + 0.3 * lfp_val + np.random.normal(0, 0.05)
    width = 1.2 - 0.4 * drive_val + np.random.normal(0, 0.03)
    return sharpness, decay_lambda, width

for i in range(N):
    # Leaky integration toward threshold
    v_membrane += (internal_drive[i] + 0.2 * lfp[i] - 0.5 * v_membrane) * dt * 25.0
    if v_membrane >= threshold:
        spike_indices.append(i)
        true_drives_at_spikes.append(internal_drive[i])
        feats = generate_waveform(internal_drive[i], lfp[i])
        waveform_features.append(feats)
        v_membrane = 0.0  # reset

spike_indices = np.array(spike_indices)
waveform_features = np.array(waveform_features)
true_drives_at_spikes = np.array(true_drives_at_spikes)

# 3. Receiver Decoding: Inverse Model vs. Binary Rate Code
# Model A: Binary Rate Decoder (exponential leaky filter of 0/1 pulses)
binary_signal = np.zeros(N)
binary_signal[spike_indices] = 1.0 / dt
binary_decoded = np.zeros(N)
tau_filter = 0.15  # 150 ms smoothing window
for i in range(1, N):
    binary_decoded[i] = binary_decoded[i-1] + (binary_signal[i] - binary_decoded[i-1]) * (dt / tau_filter)
# Normalize to match drive scale
binary_decoded = (binary_decoded - np.mean(binary_decoded)) / (np.std(binary_decoded) + 1e-6) * np.std(internal_drive) + np.mean(internal_drive)

# Model B: Waveform Inverse Model (decodes drive instantaneously per spike)
# Linear inverse model mapping [sharpness, decay_lambda, width] -> drive
X = np.hstack([waveform_features, np.ones((len(waveform_features), 1))])
weights, _, _, _ = np.linalg.lstsq(X, true_drives_at_spikes, rcond=None)
decoded_spike_drive = X @ weights

# Sample-and-hold / zero-order hold for receiver's continuous representation
waveform_decoded = np.zeros(N)
current_est = decoded_spike_drive[0]
spike_ptr = 0
for i in range(N):
    if spike_ptr < len(spike_indices) and i >= spike_indices[spike_ptr]:
        current_est = decoded_spike_drive[spike_ptr]
        spike_ptr += 1
    waveform_decoded[i] = current_est

# 4. Diagnostics & Evaluation
corr_binary = np.corrcoef(internal_drive, binary_decoded)[0, 1]
corr_waveform = np.corrcoef(internal_drive, waveform_decoded)[0, 1]
mse_binary = np.mean((internal_drive - binary_decoded) ** 2)
mse_waveform = np.mean((internal_drive - waveform_decoded) ** 2)

print("--- INVERSE MODEL DECODING COMPARISON ---")
print(f"Total Action Potentials Emitted: {len(spike_indices)}")
print(f"Binary Rate Code Tracking -> Pearson r: {corr_binary:.3f}, MSE: {mse_binary:.4f}")
print(f"Waveform Inverse Model     -> Pearson r: {corr_waveform:.3f}, MSE: {mse_waveform:.4f}")

# 5. Plotting
fig, axs = plt.subplots(3, 1, figsize=(11, 7), sharex=True)

# Panel 1: Environmental LFP & Sender Drive
axs[0].plot(time, internal_drive, 'black', lw=2, label="Sender Latent Drive $I(t)$")
axs[0].plot(time, lfp, 'purple', alpha=0.35, label="Shared Medium (LFP)")
axs[0].scatter(time[spike_indices], internal_drive[spike_indices], color='crimson', s=25, zorder=4, label="Emitted APs")
axs[0].set_ylabel("State Amplitude")
axs[0].set_title("Sender Inner Sequencer & Continuous Environmental Bath")
axs[0].legend(loc="upper right")
axs[0].grid(True, alpha=0.3)

# Panel 2: State-Dependent Waveform Feature Trajectories
axs[1].plot(time[spike_indices], waveform_features[:, 0], 'o-', color='navy', ms=4, label="Peak Sharpness")
axs[1].plot(time[spike_indices], waveform_features[:, 1], 's-', color='teal', ms=4, label="Decay Rate $\\lambda$")
axs[1].plot(time[spike_indices], waveform_features[:, 2], '^-', color='darkorange', ms=4, label="Peak Width")
axs[1].set_ylabel("Waveform Metric")
axs[1].set_title("Analog State-Modulated Waveform Features (Martin-Burgos et al., 2026)")
axs[1].legend(loc="upper right")
axs[1].grid(True, alpha=0.3)

# Panel 3: Receiver Reconstruction
axs[2].plot(time, internal_drive, 'black', lw=1.5, alpha=0.5, label="True Sender Drive")
axs[2].plot(time, binary_decoded, color='gray', linestyle='--', label=f"Binary Rate Filter (r={corr_binary:.2f})")
axs[2].plot(time, waveform_decoded, color='crimson', lw=2, label=f"Waveform Inverse Model (r={corr_waveform:.2f})")
axs[2].set_ylabel("Decoded Drive")
axs[2].set_xlabel("Time (s)")
axs[2].set_title("Receiver Reconstruction: Waveform Inverse Decoding vs. Binary Pulse Rate")
axs[2].legend(loc="upper right")
axs[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
