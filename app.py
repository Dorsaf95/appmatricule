import pandas as pd
from datetime import datetime
import streamlit as st

# Fonction pour convertir les secondes en heures, minutes et secondes
def format_hours_minutes_and_seconds(total_seconds):
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{int(hours)} heures, {int(minutes)} minutes et {int(seconds)} secondes"

# Fonction principale pour calculer les heures supplémentaires
def calculate_overtime(data, matricule):
    filtered_data = data[data["Matricule"].astype(str).str.strip() == matricule]
    if filtered_data.empty:
        return None, None
    
    # Extraire les colonnes Date et Time
    filtered_data["Date"] = filtered_data["DateTime"].str.split(" ").str[0]
    filtered_data["Time"] = filtered_data["DateTime"].str.split(" ").str[1]

    # Calcul des heures supplémentaires par jour
    overtime_data = []
    grouped = filtered_data.groupby("Date")
    total_overtime_seconds = 0

    for date, group in grouped:
        times = group["Time"].tolist()
        if len(times) >= 2:
            exit_time = times[-1]
            exit_time_dt = datetime.strptime(exit_time, "%H:%M:%S")
            overtime_start = datetime.strptime("17:00:00", "%H:%M:%S")

            if exit_time_dt > overtime_start:
                overtime_seconds = (exit_time_dt - overtime_start).total_seconds()
                total_overtime_seconds += overtime_seconds

                # Convertir en heures, minutes, secondes
                hours = int(overtime_seconds // 3600)
                remaining_seconds = overtime_seconds % 3600
                minutes = int(remaining_seconds // 60)
                seconds = int(remaining_seconds % 60)

                formatted_overtime = format_hours_minutes_and_seconds(overtime_seconds)
                overtime_data.append((date, exit_time, hours, minutes, seconds, formatted_overtime))
    
    total_overtime_formatted = format_hours_minutes_and_seconds(total_overtime_seconds)
    overtime_df = pd.DataFrame(overtime_data, columns=[
        "Date", "Exit Time", "Hours", "Minutes", "Seconds", "Overtime (h:m:s)"
    ])
    return overtime_df, total_overtime_formatted

# Interface utilisateur avec Streamlit
st.title("Calcul des Heures Supplémentaires")
st.write("Chargez un fichier `.dat` et saisissez un matricule pour calculer les heures supplémentaires après 17h.")

# Chargement du fichier
uploaded_file = st.file_uploader("Téléchargez votre fichier .dat", type="dat")

if uploaded_file is not None:
    try:
        # Lire le fichier
        data = pd.read_csv(uploaded_file, delimiter="\t", header=None)
        data.columns = ["Matricule", "DateTime", "Col3", "Col4", "Col5", "Col6"]

        # Saisir le matricule
        matricule = st.text_input("Entrez le matricule à analyser (par exemple : 50040)")
        
        if matricule:
            overtime_df, total_overtime = calculate_overtime(data, matricule)
            if overtime_df is not None:
                st.success(f"Somme totale des heures supplémentaires : {total_overtime}")
                st.write("Détails des heures supplémentaires :")
                st.dataframe(overtime_df)
                
                # Télécharger le fichier CSV
                csv = overtime_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Télécharger les heures supplémentaires en CSV",
                    data=csv,
                    file_name=f"overtime_{matricule}.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"Aucune donnée trouvée pour le matricule {matricule}.")
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier : {e}")
