import os
import numpy as np
import scipy.io.wavfile as wav
from mosqito.sq_metrics import loudness_zwtv, sharpness_din_tv, roughness_dw

# =============================================================================
# CONFIGURATION
# =============================================================================
# Nom du dossier contenant vos fichiers audio
TARGET_DIR = "C"

# Liste pour stocker tous les indices d'agacement calculés
all_pa_scores = []

# Vérification de l'existence du dossier
if not os.path.exists(TARGET_DIR):
    print(f"Erreur : Le dossier '{TARGET_DIR}' n'existe pas.")
    exit()

# Récupération de tous les fichiers .wav du dossier
audio_files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith('.wav')]

if not audio_files:
    print(f"Aucun fichier .wav trouvé dans le dossier '{TARGET_DIR}'.")
    exit()

print(f"Début de l'analyse globale : {len(audio_files)} fichier(s) trouvé(s).\n")
print("-" * 50)

# =============================================================================
# BOUCLE D'ANALYSE FICHIER PAR FICHIER
# =============================================================================
for filename in audio_files:
    file_path = os.path.join(TARGET_DIR, filename)
    print(f"Analyse de : {filename} ...")
    
    try:
        # 1. Chargement et préparation du signal
        fs, signal = wav.read(file_path)
        
        if signal.ndim == 2:
            signal = signal.mean(axis=1)  # Conversion Mono
            
        signal = signal.astype(np.float32) / np.iinfo(np.int16).max
        
        # 2. Calcul des métriques psychoacoustiques
        N, _, _, _ = loudness_zwtv(signal, fs, field_type="free")
        N_5 = np.percentile(N, 95)
        
        S, _ = sharpness_din_tv(signal, fs, skip=0.2)
        S = np.mean(S)
        
        R, _, _, _ = roughness_dw(signal, fs)
        R = np.mean(R)
        
        # 3. Calcul de l'indice d'agacement (PA)
        w_S = (S - 1.75) * np.log(N_5 + 2) if S > 1.75 else 0
        w_FR = np.sqrt((0.3 * R) ** 2)
        
        psychoacoustic_annoyance = N_5 * (1 + np.sqrt(w_S**2 + w_FR**2))
        
        # Enregistrement du score
        all_pa_scores.append(psychoacoustic_annoyance)
        print(f"   -> Score PA : {psychoacoustic_annoyance:.2f}")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du traitement de {filename} : {e}")

# =============================================================================
# CALCUL DE LA MOYENNE FINALE
# =============================================================================
print("-" * 50)
if all_pa_scores:
    average_annoyance = np.mean(all_pa_scores)
    print("\n" + "="*45)
    print("           RÉSULTATS DE L'ANALYSE GLOBAL      ")
    print("="*45)
    print(f"Fichiers analysés avec succès : {len(all_pa_scores)}/{len(audio_files)}")
    print(f"INDICE D'AGACEMENT MOYEN (PA) : {average_annoyance:.2f}")
    print("="*45)
    
    # Petite aide à l'interprétation rapide de la moyenne
    if average_annoyance < 4:
        print("Interprétation globale : Environnement très calme / Négligeable.")
    elif average_annoyance < 12:
        print("Interprétation globale : Nuisance faible / Tolérable.")
    elif average_annoyance < 25:
        print("Interprétation globale : Nuisance modérée à significative (Fatiguant).")
    else:
        print("Interprétation globale : Environnement très agaçant / Critique.")
    print("="*45)
else:
    print("\nAucun fichier n'a pu être analysé avec succès.")