
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.diagnostic import lilliefors

# ==========================================
# KONFIGURASI
# ==========================================

st.set_page_config(
    page_title="SportMetrics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SportMetrics")
st.caption("Statistical Analysis for Sports Research")

# ==========================================
# FUNGSI BANTU
# ==========================================

def p_value_text(p):
    return "< 0.001" if p < 0.001 else f"{p:.4f}"


def keputusan_normalitas(p):
    return "Normal" if p > 0.05 else "Tidak normal"


def keputusan_signifikansi(p):
    return "Signifikan" if p < 0.05 else "Tidak signifikan"


def tampilkan_tabel(data):
    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title(" SportMetrics")

menu = st.sidebar.radio(
    "Pilih Analisis",
    [
        "Dashboard",
        "Data View",
        "Statistik Deskriptif",
        "Uji Normalitas",
        "Uji Homogenitas",
        "Paired Sample T-Test",
        "Independent Sample T-Test",
        "One-Way ANOVA",
        "Mann-Whitney",
        "Wilcoxon",
        "Korelasi",
        "Uji Reliabilitas"
    ]
)

st.sidebar.divider()

file = st.sidebar.file_uploader(
    "Import Excel / CSV",
    type=["xlsx", "csv"]
)

df = None

if file is not None:
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as e:
        st.sidebar.error(f"Gagal membaca file: {e}")

# ==========================================
# DATA SIMULASI JIKA BELUM ADA FILE
# ==========================================

if df is None:
    data = {
        "ID": [f"S{i:02d}" for i in range(1, 21)],
        "Jenis_Kelamin": [
            "L", "P", "L", "P", "L", "P", "L", "P", "L", "P",
            "L", "P", "L", "P", "L", "P", "L", "P", "L", "P"
        ],
        "Pretest_Dribbling": [
            45, 52, 48, 50, 55, 47, 60, 53, 49, 51,
            44, 56, 58, 46, 54, 50, 47, 59, 52, 48
        ],
        "Posttest_Dribbling": [
            62, 68, 64, 66, 70, 63, 76, 69, 65, 67,
            61, 72, 74, 62, 71, 66, 64, 75, 69, 65
        ],
        "Kelompok": ["Eksperimen"] * 10 + ["Kontrol"] * 10
    }

    df = pd.DataFrame(data)

    st.sidebar.info("Menggunakan data simulasi.")

# ==========================================
# PILIH KOLOM NUMERIK
# ==========================================

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

categorical_columns = df.select_dtypes(
    exclude="number"
).columns.tolist()

if not numeric_columns:
    st.error("Data tidak memiliki kolom numerik.")
    st.stop()

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.subheader("Dashboard Analisis Data")

    col1, col2, col3 = st.columns(3)

    col1.metric("Jumlah Responden", len(df))
    col2.metric("Variabel Numerik", len(numeric_columns))
    col3.metric("Total Variabel", len(df.columns))

    st.subheader("Pratinjau Data")
    st.dataframe(df, use_container_width=True)

    st.subheader("Ringkasan Statistik")

    st.dataframe(
        df[numeric_columns].describe().T.round(3),
        use_container_width=True
    )

# ==========================================
# DATA VIEW
# ==========================================

elif menu == "Data View":

    st.subheader("Data View")

    st.write("Seluruh data penelitian yang diimpor.")

    st.dataframe(
        df,
        use_container_width=True,
        height=450
    )

    st.download_button(
        "Unduh Data CSV",
        df.to_csv(index=False).encode("utf-8"),
        "data_penelitian.csv",
        "text/csv"
    )

# ==========================================
# STATISTIK DESKRIPTIF
# ==========================================

elif menu == "Statistik Deskriptif":

    st.subheader("Statistik Deskriptif")

    hasil = df[numeric_columns].describe().T

    hasil = hasil.rename(columns={
        "count": "N",
        "mean": "Mean",
        "std": "Std. Deviation",
        "min": "Minimum",
        "max": "Maximum"
    })

    st.dataframe(
        hasil.round(3),
        use_container_width=True
    )

    variabel = st.selectbox(
        "Pilih variabel grafik",
        numeric_columns
    )

    fig, ax = plt.subplots()

    ax.hist(df[variabel].dropna(), bins=10)
    ax.set_title(f"Distribusi {variabel}")
    ax.set_xlabel(variabel)
    ax.set_ylabel("Frekuensi")

    st.pyplot(fig)

# ==========================================
# UJI NORMALITAS
# ==========================================

elif menu == "Uji Normalitas":

    st.subheader("Uji Normalitas")

    variabel = st.selectbox(
        "Pilih variabel",
        numeric_columns
    )

    nilai = df[variabel].dropna()

    if len(nilai) < 3:
        st.warning("Minimal diperlukan 3 data.")
    else:
        shapiro = stats.shapiro(nilai)

        ks_stat, ks_p = lilliefors(nilai)

        tampilkan_tabel([
            {
                "Metode": "Shapiro-Wilk",
                "Statistic": round(shapiro.statistic, 4),
                "Sig.": p_value_text(shapiro.pvalue),
                "Keputusan": keputusan_normalitas(shapiro.pvalue)
            },
            {
                "Metode": "Kolmogorov-Smirnov (Lilliefors)",
                "Statistic": round(ks_stat, 4),
                "Sig.": p_value_text(ks_p),
                "Keputusan": keputusan_normalitas(ks_p)
            }
        ])

        st.info(
            "Kriteria: Sig. > 0,05 berarti tidak terdapat bukti "
            "yang cukup untuk menolak asumsi normalitas."
        )

# ==========================================
# UJI HOMOGENITAS
# ==========================================

elif menu == "Uji Homogenitas":

    st.subheader("Uji Homogenitas Levene")

    if not categorical_columns:
        st.warning("Tidak ada variabel kelompok.")
    else:
        kelompok = st.selectbox(
            "Pilih variabel kelompok",
            categorical_columns
        )

        variabel = st.selectbox(
            "Pilih nilai yang diuji",
            numeric_columns
        )

        grup_data = [
            grup[variabel].dropna().values
            for _, grup in df.groupby(kelompok)
        ]

        grup_data = [g for g in grup_data if len(g) > 0]

        if len(grup_data) < 2:
            st.warning("Diperlukan minimal dua kelompok.")
        else:
            hasil = stats.levene(*grup_data)

            tampilkan_tabel([{
                "Metode": "Levene",
                "Statistic": round(hasil.statistic, 4),
                "Sig.": p_value_text(hasil.pvalue),
                "Keputusan": "Homogen" if hasil.pvalue > 0.05 else "Tidak homogen"
            }])

# ==========================================
# PAIRED SAMPLE T-TEST
# ==========================================

elif menu == "Paired Sample T-Test":

    st.subheader("Paired Sample T-Test")

    pre = st.selectbox(
        "Variabel Pretest",
        numeric_columns
    )

    post = st.selectbox(
        "Variabel Posttest",
        [c for c in numeric_columns if c != pre]
    )

    data_pair = df[[pre, post]].dropna()

    if len(data_pair) < 2:
        st.warning("Data berpasangan tidak mencukupi.")
    else:
        hasil = stats.ttest_rel(
            data_pair[pre],
            data_pair[post]
        )

        tampilkan_tabel([{
            "N": len(data_pair),
            "Mean Pretest": round(data_pair[pre].mean(), 3),
            "Mean Posttest": round(data_pair[post].mean(), 3),
            "Mean Difference": round(
                (data_pair[post] - data_pair[pre]).mean(), 3
            ),
            "t": round(hasil.statistic, 4),
            "Sig. (2-tailed)": p_value_text(hasil.pvalue),
            "Keputusan": keputusan_signifikansi(hasil.pvalue)
        }])

        st.info(
            "Uji ini membandingkan dua pengukuran berpasangan "
            "pada subjek yang sama."
        )

# ==========================================
# INDEPENDENT SAMPLE T-TEST
# ==========================================

elif menu == "Independent Sample T-Test":

    st.subheader("Independent Sample T-Test")

    if not categorical_columns:
        st.warning("Variabel kelompok tidak tersedia.")
    else:
        kelompok = st.selectbox(
            "Variabel kelompok",
            categorical_columns
        )

        variabel = st.selectbox(
            "Variabel nilai",
            numeric_columns
        )

        nama_grup = df[kelompok].dropna().unique()

        if len(nama_grup) != 2:
            st.warning("Pilih data yang memiliki tepat dua kelompok.")
        else:
            g1 = df.loc[
                df[kelompok] == nama_grup[0], variabel
            ].dropna()

            g2 = df.loc[
                df[kelompok] == nama_grup[1], variabel
            ].dropna()

            if len(g1) < 2 or len(g2) < 2:
                st.warning("Setiap kelompok membutuhkan minimal dua data.")
            else:
                levene = stats.levene(g1, g2)

                hasil = stats.ttest_ind(
                    g1, g2,
                    equal_var=levene.pvalue > 0.05
                )

                tampilkan_tabel([{
                    "Kelompok 1": nama_grup[0],
                    "Mean 1": round(g1.mean(), 3),
                    "Kelompok 2": nama_grup[1],
                    "Mean 2": round(g2.mean(), 3),
                    "Levene Sig.": p_value_text(levene.pvalue),
                    "t": round(hasil.statistic, 4),
                    "Sig. (2-tailed)": p_value_text(hasil.pvalue),
                    "Keputusan": keputusan_signifikansi(hasil.pvalue)
                }])

# ==========================================
# ONE-WAY ANOVA
# ==========================================

elif menu == "One-Way ANOVA":

    st.subheader("One-Way ANOVA")

    if not categorical_columns:
        st.warning("Variabel kelompok tidak tersedia.")
    else:
        kelompok = st.selectbox(
            "Variabel kelompok",
            categorical_columns
        )

        variabel = st.selectbox(
            "Variabel numerik",
            numeric_columns
        )

        grup_data = [
            grup[variabel].dropna().values
            for _, grup in df.groupby(kelompok)
        ]

        grup_data = [g for g in grup_data if len(g) > 0]

        if len(grup_data) < 2 or any(len(g) < 2 for g in grup_data):
            st.warning("Minimal dua kelompok, masing-masing dua data.")
        else:
            hasil = stats.f_oneway(*grup_data)

            tampilkan_tabel([{
                "F": round(hasil.statistic, 4),
                "Sig.": p_value_text(hasil.pvalue),
                "Keputusan": keputusan_signifikansi(hasil.pvalue)
            }])

            if hasil.pvalue < 0.05:
                st.write("Uji lanjut Tukey HSD:")

                tukey = pairwise_tukeyhsd(
                    endog=df[variabel].dropna(),
                    groups=df.loc[df[variabel].notna(), kelompok],
                    alpha=0.05
                )

                st.text(str(tukey))

# ==========================================
# MANN-WHITNEY
# ==========================================

elif menu == "Mann-Whitney":

    st.subheader("Mann-Whitney U Test")

    if not categorical_columns:
        st.warning("Variabel kelompok tidak tersedia.")
    else:
        kelompok = st.selectbox("Variabel kelompok", categorical_columns)
        variabel = st.selectbox("Variabel nilai", numeric_columns)

        nama = df[kelompok].dropna().unique()

        if len(nama) != 2:
            st.warning("Diperlukan tepat dua kelompok.")
        else:
            g1 = df.loc[df[kelompok] == nama[0], variabel].dropna()
            g2 = df.loc[df[kelompok] == nama[1], variabel].dropna()

            if len(g1) == 0 or len(g2) == 0:
                st.warning("Data kelompok tidak mencukupi.")
            else:
                hasil = stats.mannwhitneyu(
                    g1, g2,
                    alternative="two-sided"
                )

                tampilkan_tabel([{
                    "U": round(hasil.statistic, 4),
                    "Sig.": p_value_text(hasil.pvalue),
                    "Keputusan": keputusan_signifikansi(hasil.pvalue)
                }])

# ==========================================
# WILCOXON
# ==========================================

elif menu == "Wilcoxon":

    st.subheader("Wilcoxon Signed-Rank Test")

    pre = st.selectbox("Pretest", numeric_columns)
    post = st.selectbox(
        "Posttest",
        [c for c in numeric_columns if c != pre]
    )

    pasangan = df[[pre, post]].dropna()

    if len(pasangan) == 0:
        st.warning("Data tidak tersedia.")
    elif (pasangan[pre] != pasangan[post]).sum() == 0:
        st.warning("Semua selisih bernilai nol.")
    else:
        hasil = stats.wilcoxon(
            pasangan[pre],
            pasangan[post]
        )

        tampilkan_tabel([{
            "N": len(pasangan),
            "W": round(hasil.statistic, 4),
            "Sig.": p_value_text(hasil.pvalue),
            "Keputusan": keputusan_signifikansi(hasil.pvalue)
        }])

# ==========================================
# KORELASI
# ==========================================

elif menu == "Korelasi":

    st.subheader("Correlation Analysis")

    x = st.selectbox("Variabel X", numeric_columns)
    y = st.selectbox(
        "Variabel Y",
        [c for c in numeric_columns if c != x]
    )

    metode = st.radio(
        "Metode korelasi",
        ["Pearson", "Spearman"],
        horizontal=True
    )

    pasangan = df[[x, y]].dropna()

    if len(pasangan) < 3:
        st.warning("Diperlukan minimal tiga pasangan data.")
    else:
        if metode == "Pearson":
            hasil = stats.pearsonr(pasangan[x], pasangan[y])
        else:
            hasil = stats.spearmanr(pasangan[x], pasangan[y])

        tampilkan_tabel([{
            "Metode": metode,
            "N": len(pasangan),
            "Correlation": round(hasil.statistic, 4),
            "Sig.": p_value_text(hasil.pvalue),
            "Keputusan": keputusan_signifikansi(hasil.pvalue)
        }])

        fig, ax = plt.subplots()
        ax.scatter(pasangan[x], pasangan[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{metode} Correlation")
        st.pyplot(fig)

# ==========================================
# RELIABILITAS CRONBACH ALPHA
# ==========================================

elif menu == "Uji Reliabilitas":

    st.subheader("Uji Reliabilitas Cronbach's Alpha")

    st.write(
        "Pilih kolom butir instrumen. "
        "Gunakan data respons item, bukan skor total."
    )

    items = st.multiselect(
        "Pilih butir pertanyaan",
        numeric_columns
    )

    if len(items) < 2:
        st.info("Pilih minimal dua butir instrumen.")
    else:
        item_data = df[items].dropna()

        if len(item_data) < 2:
            st.warning("Data responden tidak mencukupi.")
        elif (item_data.sum(axis=1).var(ddof=1) == 0):
            st.warning("Varians skor total nol.")
        else:
            jumlah_item = len(items)

            varians_item = item_data.var(ddof=1).sum()
            varians_total = item_data.sum(axis=1).var(ddof=1)

            alpha = (
                jumlah_item / (jumlah_item - 1)
            ) * (
                1 - varians_item / varians_total
            )

            tampilkan_tabel([{
                "Jumlah Item": jumlah_item,
                "Responden": len(item_data),
                "Cronbach's Alpha": round(alpha, 4)
            }])

            st.info(
                "Interpretasikan nilai alpha dengan mempertimbangkan "
                "konteks instrumen dan standar penelitian yang digunakan."
            )

# ==========================================
# FOOTER
# ==========================================

st.sidebar.caption("SportMetrics v1.0")
st.sidebar.caption("Educational Research Tool")
