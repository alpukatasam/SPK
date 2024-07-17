# Author: Muhamad Rizky Kholba

import streamlit as st
import numpy as np
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.figure_factory as ff


class WASPASDecision:
    def __init__(self, data, bobot, tipeKriteria, namaAlternatif):
        self.data = data
        self.bobot = bobot
        self.tipeKriteria = tipeKriteria
        self.namaAlternatif = namaAlternatif
        self.dataTernormalisasi = self.normalisasiData()
        self.nilaiQi = self.hitung_nilaiQi()

    def normalisasiData(self):
        dataTernormalisasi = np.zeros_like(self.data, dtype=np.float64)

        for j in range(self.data.shape[1]):
            if self.tipeKriteria[j] == "benefit":
                max_value = np.max(self.data[:, j])
                dataTernormalisasi[:, j] = self.data[:, j] / max_value
            elif self.tipeKriteria[j] == "cost":
                min_value = np.min(self.data[:, j])
                dataTernormalisasi[:, j] = min_value / self.data[:, j]

        return dataTernormalisasi

    def hitung_nilaiQi(self):
        nilaiQi = np.zeros(self.dataTernormalisasi.shape[0])

        for i in range(self.dataTernormalisasi.shape[0]):
            sum_term = (0.5) * (np.sum(self.dataTernormalisasi[i, :] * self.bobot))
            prod_term = (0.5) * (np.prod(self.dataTernormalisasi[i, :] ** self.bobot))

            nilaiQi[i] = sum_term + prod_term

        return nilaiQi

    def tampilanOutput(self):
        # Menampilkan label C1, C2, dll., untuk kolom
        column_labels = [f"C{i+1}" for i in range(self.data.shape[1])]
        # Menampilkan label A1, A2, dll., untuk baris
        row_labels = [f"A{i+1}" for i in range(self.data.shape[0])]

        # Menampilkan matriks keputusan dengan label yang sudah dimodifikasi
        st.subheader("Matriks Keputusan:")
        st.table(pd.DataFrame(self.data, columns=column_labels, index=row_labels))

        # Menampilkan bobot
        st.subheader("\nBobot Kriteria:")
        bobot_df = pd.DataFrame(
            {
                "Persentase": [f"{weight * 100:.0f}%" for weight in self.bobot],
                "Desimal": self.bobot,
            },
            index=column_labels,
        )
        st.table(bobot_df)

        # Menampilkan matriks ternormalisasi dengan label yang sudah dimodifikasi
        st.subheader("\nMatriks Ternormalisasi:")
        st.table(
            pd.DataFrame(
                self.dataTernormalisasi, columns=column_labels, index=row_labels
            )
        )

        # Menampilkan nilai aletrnatif terbaik
        best_alternative_index = np.argmax(self.nilaiQi) + 1

        st.subheader("\nNilai Q:")
        for i, value in enumerate(self.nilaiQi, start=1):
            st.write(f"(Q{i}) {self.namaAlternatif[i-1]}: {value}")

        st.markdown(
            f"\nNilai :red[Q{best_alternative_index}] memiliki nilai paling besar, sehingga :red[(A{best_alternative_index}) {self.namaAlternatif[best_alternative_index-1]}] terpilih sebagai alternatif terbaik."
        )


# Aplikasi Streamlit
def main():
    st.title("Pembuatan Keputusan dengan WASPAS\n")

    # Input jumlah kriteria dan alternatif
    st.subheader("Jumlah Kriteria dan Alternatif")

    num_criteria = st.number_input("Jumlah Kriteria", min_value=1, step=1)
    num_alternatives = st.number_input("Jumlah Alternatif", min_value=1, step=1)

    # Pendefinisian kriteria
    st.subheader("Pendefinisian Kriteria")

    criteria_names = []
    tipeKriteria = []
    bobot = []

    col1, col2, col3 = st.columns(3)

    with col1:
        # Input nama kriteria
        for i in range(num_criteria):
            criteria_names.append(st.text_input(f"Nama Kriteria {i+1}"))

    with col2:
        # Input bobot kriteria sebagai persentase
        for i in range(num_criteria):
            tipeKriteria.append(
                st.selectbox(
                    f"Jenis Kriteria {criteria_names[i]}",
                    ["benefit", "cost"],
                    key=f"selectbox_{i}",
                )
            )

    with col3:
        # Input kriteria dan jenis kriteria (benefit atau cost)
        for i in range(num_criteria):
            bobot.append(
                st.number_input(
                    f"Bobot Kriteria {criteria_names[i]} (%)",
                    min_value=0,
                    max_value=100,
                    step=1,
                    key=f"weight_{i}",
                )
                / 100.0
            )

    # Validasi total bobot kriteria
    if sum(bobot) != 1.0:
        st.error("Total bobot kriteria harus sama dengan 100%.")
        return

    # Pendefinisian alternatif
    st.subheader("Pendefinisian Alternatif")

    # Input nama alternatif
    namaAlternatif = []
    for i in range(num_alternatives):
        namaAlternatif.append(st.text_input(f"Nama Alternatif {i+1}"))

    # Nilai matriks
    st.subheader("Nilai Matriks")

    # Input matriks keputusan
    data = np.zeros((num_alternatives, num_criteria))
    for i in range(num_alternatives):
        for j in range(num_criteria):
            data[i, j] = st.number_input(
                f"(A{i+1}) Alternatif {namaAlternatif[i]} - (C{j+1}) Kriteria {criteria_names[j]}",
                min_value=0,
                step=1,
                key=f"input_{i}_{j}",
            )

    # Membuat objek WASPASDecision
    waspas_model = WASPASDecision(data, np.array(bobot), tipeKriteria, namaAlternatif)

    # ...

    # Tombol Hitung
    if st.button("Hitung"):
        waspas_model.tampilanOutput()


if __name__ == "__main__":
    main()
