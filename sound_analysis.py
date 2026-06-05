import os
import numpy as np
import scipy.io.wavfile as wav
import mosqito

# 1. CHARGER LE FICHIER AUDIO
# Attention : la plupart des normes psychoacoustiques exigent une fréquence de 48 kHz
fs, signal = wav.read("test1.wav")

# 2. CALCULER LES BRICKS DE BASE (Exemple avec MOSQITO)
# Calcul de la Sonie (Loudness) selon la norme ISO 532-1 (Zwicker)
# 'field_type' précise si on est au casque (free) ou en pièce (diffuse)
loudness_dict = mosqito.compute_loudness_zwicker_time(signal, fs, field_type="free")
N_5 = loudness_dict["values"][-1] # On extrait le percentile de pointe N5

# Calcul de la Netteté (Sharpness) selon la norme DIN 45692
sharpness_dict = mosqito.compute_sharpness_din(signal, fs_dict=fs)
S = np.mean(sharpness_dict["values"]) # Valeur moyenne de la netteté

# Calcul de la Rugosité (Roughness)
roughness_dict = mosqito.compute_roughness_dw(signal, fs)
R = np.mean(roughness_dict["values"])

# 3. CALCULER L'INDICE D'AGACEMENT (Formule de Zwicker & Fastl)
# On applique les coefficients multiplicateurs liés à la perception humaine
if S > 1.75:
    w_S = (S - 1.75) * np.log(N_5 + 2)
else:
    w_S = 0

w_FR = np.sqrt((0.3 * R)**2 + (0.05 * 0)**2) # (0 ici correspond à la Fluctuation au repos)

# Score final d'agacement psychoacoustique
psychoacoustic_annoyance = N_5 * (1 + np.sqrt(w_S**2 + w_FR**2))

print(f"Indice de perturbation globale : {psychoacoustic_annoyance:.2f}")