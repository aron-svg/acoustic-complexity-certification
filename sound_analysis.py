import numpy as np
import scipy.io.wavfile as wav
from mosqito.sq_metrics import loudness_zwtv, sharpness_din_tv, roughness_dw

# 1. CHARGER ET PRÉPARER LE SIGNAL
fs, signal = wav.read("test1.wav")

if signal.ndim == 2:
    signal = signal.mean(axis=1)
signal = signal.astype(np.float32) / np.iinfo(np.int16).max

# 2. MÉTRIQUES PSYCHOACOUSTIQUES
N, N_spec, bark_axis, time_axis = loudness_zwtv(signal, fs, field_type="free")
N_5 = np.percentile(N, 95)

S, _, _, _ = sharpness_din_tv(signal, fs)  # ✅ Corrigé
S = np.mean(S)

R, _, _, _ = roughness_dw(signal, fs)
R = np.mean(R)

# 3. INDICE D'AGACEMENT (Zwicker & Fastl)
w_S = (S - 1.75) * np.log(N_5 + 2) if S > 1.75 else 0
w_FR = np.sqrt((0.3 * R) ** 2)

psychoacoustic_annoyance = N_5 * (1 + np.sqrt(w_S**2 + w_FR**2))

print(f"Sonie N5          : {N_5:.2f} sone")
print(f"Netteté S         : {S:.2f} acum")
print(f"Rugosité R        : {R:.2f} asper")
print(f"Indice d'agacement: {psychoacoustic_annoyance:.2f}")