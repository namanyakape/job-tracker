import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import date

# ── KONEKSI ──────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["GOOGLE_CREDENTIALS"],
    scopes=SCOPES
)
client = gspread.authorize(creds)

SHEET_ID = "1q4SUC84NpabBQtvMddbouVqwzSUMg7m_r-P48D2Xbn8"  # ← jangan lupa ganti!
sheet = client.open_by_key(SHEET_ID).sheet1

# ── FUNGSI ────────────────────────────────────────
def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def add_row(no, perusahaan, posisi, tanggal, status, notes):
    sheet.append_row([no, perusahaan, posisi, str(tanggal), status, notes])

def update_status(no, new_status):
    # Cari baris berdasarkan No (row 1 = header, jadi +1)
    cell = sheet.find(str(no))
    if cell:
        sheet.update_cell(cell.row, 5, new_status)  # kolom 5 = Status

# ── TAMPILAN ──────────────────────────────────────
st.set_page_config(page_title="Job Tracker", page_icon="💼", layout="wide")
st.title("💼 Job Application Tracker")
st.markdown("---")

# Tab biar lebih rapi
tab1, tab2 = st.tabs(["➕ Tambah Lamaran", "✏️ Update Status"])

# ── TAB 1: TAMBAH LAMARAN ─────────────────────────
with tab1:
    st.subheader("➕ Tambah Lamaran Baru")
    col1, col2 = st.columns(2)

    with col1:
        perusahaan = st.text_input("Nama Perusahaan")
        posisi = st.text_input("Posisi / Jabatan")
        tanggal = st.date_input("Tanggal Daftar", value=date.today())

    with col2:
        status = st.selectbox("Status", [
            "Sent", "On Review", "Interview", "Approved", "Rejected"
        ])
        notes = st.text_area("Notes (opsional)")

    if st.button("➕ Tambah Lamaran", use_container_width=True):
        if perusahaan and posisi:
            df = get_data()
            no = len(df) + 1
            add_row(no, perusahaan, posisi, tanggal, status, notes)
            st.success(f"✅ Lamaran ke **{perusahaan}** berhasil ditambahkan!")
            st.rerun()
        else:
            st.error("❌ Nama Perusahaan dan Posisi wajib diisi!")

# ── TAB 2: UPDATE STATUS ──────────────────────────
with tab2:
    st.subheader("✏️ Update Status Lamaran")

    df = get_data()

    if not df.empty:
        # Dropdown pilih perusahaan
        df["label"] = df["No"].astype(str) + " - " + df["Perusahaan"] + " (" + df["Posisi"] + ")"
        pilihan = st.selectbox("Pilih Lamaran:", df["label"].tolist())

        # Ambil No dari pilihan
        no_dipilih = int(pilihan.split(" - ")[0])
        row_dipilih = df[df["No"] == no_dipilih].iloc[0]

        st.info(f"Status sekarang: **{row_dipilih['Status']}**")

        status_baru = st.selectbox("Ganti Status ke:", [
            "Sent", "On Review", "Interview", "Approved", "Rejected"
        ])

        if st.button("✅ Update Status", use_container_width=True):
            update_status(no_dipilih, status_baru)
            st.success(f"✅ Status **{row_dipilih['Perusahaan']}** berhasil diubah ke **{status_baru}**!")
            st.rerun()
    else:
        st.info("Belum ada data lamaran.")

# ── TABEL DATA ────────────────────────────────────
st.markdown("---")
st.subheader("📊 Data Lamaran Kerja")

df = get_data()

if not df.empty:
    filter_status = st.multiselect(
        "Filter by Status:",
        ["Sent", "On Review", "Interview", "Approved", "Rejected"],
        default=["Sent", "On Review", "Interview", "Approved", "Rejected"]
    )
    df_filtered = df[df["Status"].isin(filter_status)]

    def color_status(val):
        colors = {
            "Sent": "background-color: #3d85c8; color: white",
            "On Review": "background-color: #e69138; color: white",
            "Interview": "background-color: #9900ff; color: white",
            "Approved": "background-color: #38761d; color: white",
            "Rejected": "background-color: #cc0000; color: white"
        }
        return colors.get(val, "")

    st.dataframe(
        df_filtered.style.map(color_status, subset=["Status"]),
        use_container_width=True
    )
    st.caption(f"Total: {len(df_filtered)} lamaran")
else:
    st.info("Belum ada data lamaran. Tambahkan lamaran pertamamu!")