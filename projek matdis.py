import base64
from pathlib import Path

import pandas as pd
import streamlit as st


def bersihkan(isbn: str) -> str:
    return isbn.replace("-", "").replace(" ", "").upper()


def langkah_isbn10(isbn: str):
    isbn = bersihkan(isbn)
    if len(isbn) != 10:
        return False, f"Panjangnya {len(isbn)} karakter, ISBN-10 harus 10.", None, None, None
    if not isbn[:9].isdigit() or not (isbn[9].isdigit() or isbn[9] == "X"):
        return False, "9 karakter pertama harus angka, karakter terakhir angka atau 'X'.", None, None, None

    baris, total = [], 0
    for i, ch in enumerate(isbn):
        nilai = 10 if ch == "X" else int(ch)
        bobot = 10 - i
        hasil = nilai * bobot
        total += hasil
        baris.append({"Posisi": i + 1, "Digit": ch, "Nilai": nilai, "Bobot": bobot, "Digit × Bobot": hasil})
    sisa = total % 11
    return sisa == 0, "", pd.DataFrame(baris), total, sisa


def langkah_isbn13(isbn: str):
    isbn = bersihkan(isbn)
    if len(isbn) != 13:
        return False, f"Panjangnya {len(isbn)} karakter, ISBN-13 harus 13.", None, None, None
    if not isbn.isdigit():
        return False, "ISBN-13 hanya boleh berisi angka.", None, None, None

    baris, total = [], 0
    for i, ch in enumerate(isbn):
        bobot = 1 if i % 2 == 0 else 3
        hasil = int(ch) * bobot
        total += hasil
        baris.append({"Posisi": i + 1, "Digit": ch, "Nilai": int(ch), "Bobot": bobot, "Digit × Bobot": hasil})
    sisa = total % 10
    return sisa == 0, "", pd.DataFrame(baris), total, sisa


def check_digit_isbn10(sembilan: str) -> str:
    total = sum(int(c) * (10 - i) for i, c in enumerate(sembilan))
    cek = (11 - total % 11) % 11
    return "X" if cek == 10 else str(cek)


def check_digit_isbn13(dua_belas: str) -> str:
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(dua_belas))
    return str((10 - total % 10) % 10)


def isbn10_ke_isbn13(isbn10: str) -> str:
    dua_belas = "978" + bersihkan(isbn10)[:9]
    return dua_belas + check_digit_isbn13(dua_belas)


st.set_page_config(page_title="Peta Harta ISBN", page_icon="🏴‍☠️", layout="centered")

GAYA = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pirata+One&family=IM+Fell+English:ital@0;1&display=swap');
:root{
  --buih:#f2f9ff; --buih-gelap:#d3e9f7; --tinta:#0b2a45;
  --laut:#1f6fa8; --laut-dalam:#0a3256; --pasir:#f2c45c; --merah:#c0392b; --hijau:#1e8a6e;
}
.stApp{
  background:
    radial-gradient(ellipse at top, rgba(255,255,255,.35), transparent 60%),
    linear-gradient(180deg, #8fd0f5 0%, #3d9bd6 55%, #1f6fa8 100%);
  color:var(--tinta);
}
html, body, .stApp, p, li, label, .stMarkdown, input, textarea{
  font-family:'IM Fell English', Georgia, serif !important; color:var(--tinta);
}
h1, h2, h3, h4{font-family:'Pirata One', cursive !important; color:var(--laut-dalam) !important; letter-spacing:1px;}
/* Sidebar laut dalam dengan pola ombak */
section[data-testid="stSidebar"]{
  background:
    radial-gradient(circle at 20px -8px, transparent 14px, rgba(255,255,255,.07) 15px, transparent 17px) 0 0/40px 22px,
    linear-gradient(180deg, #0f4677 0%, #0a3256 60%, #061f38 100%);
  border-right:4px solid var(--pasir);
}
section[data-testid="stSidebar"] *{color:#e6f4ff !important;}
section[data-testid="stSidebar"] strong{color:var(--pasir) !important;}
/* Judul */
.judul{text-align:center; margin:.2rem 0 1.4rem;}
.judul h1{font-size:3.4rem; margin:0; text-shadow:2px 2px 0 var(--buih-gelap), 4px 4px 0 rgba(10,50,86,.25);}
.judul p{font-style:italic; margin:0; font-size:1.15rem;}
.garis{height:3px; background:linear-gradient(90deg,transparent,var(--laut),transparent); margin:.6rem auto; width:70%;}
/* Tab */
.stTabs [data-baseweb="tab-list"]{gap:6px; border-bottom:3px solid var(--laut);}
.stTabs [data-baseweb="tab"]{
  background:var(--buih-gelap); border:2px solid var(--laut); border-bottom:none;
  border-radius:10px 10px 0 0; padding:6px 14px;
}
.stTabs [data-baseweb="tab"] p{font-family:'Pirata One',cursive !important; font-size:1.15rem; color:var(--laut-dalam);}
.stTabs [aria-selected="true"]{background:var(--laut-dalam) !important;}
.stTabs [aria-selected="true"] p{color:#ffffff !important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--pasir) !important;}
/* Input */
.stTextInput input{
  background:#ffffff !important; border:2px solid var(--laut) !important; color:var(--tinta) !important;
  border-radius:10px !important; font-size:1.25rem !important; letter-spacing:2px;
}
.stTextInput input:focus{border-color:var(--pasir) !important; box-shadow:0 0 0 3px rgba(242,196,92,.35) !important;}
.stTextInput label p, [data-testid="stWidgetLabel"] p{color:var(--tinta) !important; font-size:1.1rem;}
/* Tombol */
.stButton>button, .stFormSubmitButton>button{
  font-family:'Pirata One',cursive !important; font-size:1.25rem; letter-spacing:1px;
  background:linear-gradient(180deg,#2f8fd0,var(--laut)); color:#ffffff !important;
  border:3px solid var(--laut-dalam); border-radius:30px; padding:.3rem 1.6rem;
  box-shadow:0 4px 0 var(--laut-dalam);
}
.stButton>button p, .stFormSubmitButton>button p{color:#ffffff !important;}
.stButton>button:hover, .stFormSubmitButton>button:hover{transform:translateY(1px); box-shadow:0 3px 0 var(--laut-dalam);
  background:linear-gradient(180deg,#f7d27c,var(--pasir)); color:var(--laut-dalam) !important;}
.stButton>button:hover p, .stFormSubmitButton>button:hover p{color:var(--laut-dalam) !important;}
/* Form */
[data-testid="stForm"]{border:2px solid var(--laut) !important; border-radius:14px; background:rgba(211,233,247,.45);}
/* Kartu hasil */
.kartu{border:3px solid var(--laut); border-radius:14px; padding:1rem 1.2rem; margin:1rem 0;
  background:#ffffff; box-shadow:0 6px 0 rgba(10,50,86,.18); text-align:center;}
.kartu h2{margin:.2rem 0; font-size:2.2rem;}
.kartu .kode{font-family:'Courier New',monospace; font-size:1.5rem; font-weight:bold; letter-spacing:3px; color:var(--laut-dalam);}
.valid{border-color:var(--hijau); background:#eafaf4;} .valid h2{color:var(--hijau) !important;}
.gagal{border-color:var(--merah); background:#fdf0ee;} .gagal h2{color:var(--merah) !important;}
.rumus{background:var(--laut-dalam); border-radius:10px; padding:.7rem 1rem;
  font-family:'Courier New',monospace; font-size:1.05rem; text-align:center;}
.rumus, .rumus *{color:#e6f4ff !important;}
/* Tabel bertema (tidak ikut mode gelap) */
.tabel{width:100%; border-collapse:collapse; margin:.5rem 0 1rem; background:#ffffff;
  border:3px solid var(--laut-dalam); font-size:1.05rem;}
.tabel th{background:var(--laut-dalam); color:#ffffff !important; font-family:'Pirata One',cursive;
  font-weight:normal; letter-spacing:1px; padding:.45rem .6rem; text-align:center;}
.tabel td{color:var(--tinta) !important; padding:.35rem .6rem; text-align:center; border-top:1px solid var(--buih-gelap);}
.tabel tr:nth-child(even) td{background:var(--buih);}
/* Kotak catatan pengganti st.info */
.catatan{background:#ffffff; border:2px dashed var(--laut); border-radius:12px; padding:1rem 1.2rem;
  color:var(--tinta) !important; font-style:italic; font-size:1.1rem; text-align:center;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
</style>
"""
GAYA = "\n".join(baris for baris in GAYA.splitlines() if baris.strip())
st.markdown(GAYA, unsafe_allow_html=True)


FOLDER_APP = Path(__file__).resolve().parent
JENIS_GAMBAR = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp", ".jfif": "jpeg"}


def ke_data_uri(file: Path) -> str:
    data = base64.b64encode(file.read_bytes()).decode()
    return f"data:image/{JENIS_GAMBAR[file.suffix.lower()]};base64,{data}"


def cari_gambar(awalan: str):
    hasil = []
    for file in sorted(FOLDER_APP.iterdir(), key=lambda f: f.name.lower()):
        if file.is_file() and file.name.lower().startswith(awalan) and file.suffix.lower() in JENIS_GAMBAR:
            hasil.append((ke_data_uri(file), file.name))
    return hasil


def cari_dekorasi():
    folder = FOLDER_APP / "dekorasi"
    hasil = {}
    if folder.is_dir():
        for file in sorted(folder.rglob("*")):
            if file.is_file() and file.suffix.lower() in JENIS_GAMBAR:
                nama = file.name.lower().split(".")[0]
                hasil.setdefault(nama, ke_data_uri(file))
    return hasil


daftar_latar = cari_gambar("latar")
gambar_latar, nama_file_latar = daftar_latar[0] if daftar_latar else (None, None)
daftar_maskot = cari_gambar("maskot")
dekorasi = cari_dekorasi()

latar_css = (
    f"linear-gradient(rgba(5,30,60,.10),rgba(5,30,60,.10)), url('{gambar_latar}') center/cover no-repeat fixed"
    if gambar_latar
    else "radial-gradient(ellipse at top, rgba(255,255,255,.35), transparent 60%),"
         "linear-gradient(180deg,#8fd0f5 0%,#3d9bd6 55%,#1f6fa8 100%) fixed"
)
st.markdown(
    "<style>"
    f"html, body{{background:{latar_css} !important;}}"
    ".stApp, [data-testid='stAppViewContainer'], [data-testid='stMain'], section.main, .main"
    "{background:transparent !important;}"
    ".block-container{background:rgba(242,249,255,.94); border:4px solid #0a3256;"
    "border-radius:18px; padding:1.5rem 2.5rem 2rem !important; margin:4.5rem auto 5rem;"
    "box-shadow:0 12px 35px rgba(5,30,60,.45), inset 0 0 0 2px rgba(242,196,92,.6);}"
    "</style>",
    unsafe_allow_html=True,
)

SUSUNAN_DEKORASI = [
    ("awan",      "top:4%; left:330px; width:300px;",            "melayang-awan 26s",  False),
    ("awan",      "top:13%; right:70px; width:210px; opacity:.85;", "melayang-awan 32s", True),
    ("peta_bola", "top:30%; left:360px; width:120px;",           "putar 60s linear",   False),
    ("kompas",    "top:52%; left:520px; width:95px;",            "goyang 5s",          False),
    ("botol",     "bottom:150px; left:420px; width:62px;",        "apung 4s",           False),
    ("ombak",     "bottom:-30px; left:290px; width:520px;",       "ombak-gerak 6s",     False),
    ("ombak",     "bottom:-40px; right:-20px; width:480px;",      "ombak-gerak 7s",     True),
    ("lentera",   "top:26%; right:250px; width:80px; transform-origin:50% 0;", "ayun 3.5s", False),
    ("pedang",    "top:47%; right:110px; width:78px; --putar:-28deg;", "goyang 6s",   False),
    ("gulungan",  "top:50%; right:230px; width:46px; --putar:18deg;",  "goyang 7s",   False),
    ("koin",      "bottom:200px; right:290px; width:105px;",      "kilau 3s",           False),
]
if dekorasi:
    potongan = []
    for nama, posisi, animasi, cermin in SUSUNAN_DEKORASI:
        if nama in dekorasi:
            kelas = "dekor" + (" cermin" if cermin else "") + ("" if nama in ("awan", "ombak") else " kecil-sembunyi")
            potongan.append(
                f'<div class="{kelas}" style="{posisi} animation:{animasi} ease-in-out infinite;">'
                f'<img src="{dekorasi[nama]}"></div>'
            )
    st.markdown(
        "<style>"
        ".dekor{position:fixed; z-index:-1; pointer-events:none; filter:drop-shadow(0 6px 10px rgba(5,30,60,.35));}"
        ".dekor img{width:100%; display:block;}"
        ".cermin img{transform:scaleX(-1);}"
        "@keyframes melayang-awan{0%,100%{transform:translateX(0);}50%{transform:translateX(40px);}}"
        "@keyframes putar{to{transform:rotate(360deg);}}"
        "@keyframes goyang{0%,100%{transform:rotate(calc(var(--putar,0deg) - 6deg));}"
        "50%{transform:rotate(calc(var(--putar,0deg) + 6deg));}}"
        "@keyframes apung{0%,100%{transform:translateY(0) rotate(18deg);}50%{transform:translateY(-14px) rotate(30deg);}}"
        "@keyframes ombak-gerak{0%,100%{transform:translate(0,0);}50%{transform:translate(-14px,8px);}}"
        "@keyframes ayun{0%,100%{transform:rotate(-7deg);}50%{transform:rotate(7deg);}}"
        "@keyframes kilau{0%,100%{filter:drop-shadow(0 0 0 rgba(242,196,92,0));}"
        "50%{filter:drop-shadow(0 0 14px rgba(242,196,92,.95));}}"
        # Layar kecil: sisakan awan & ombak saja supaya tidak penuh
        "@media (max-width:1400px){.dekor.kecil-sembunyi{display:none;}}"
        "</style>" + "".join(potongan),
        unsafe_allow_html=True,
    )

MASKOT_CSS = """
<style>
.jangkar{position:relative; height:0;}
/* Maskot 1: mengintip dari jendela kapal (tingkap bulat) di pojok kiri bawah panel */
.tingkap{position:absolute; left:-150px; top:-60px; width:150px; height:150px; border-radius:50%;
  border:9px solid #c9962b; outline:4px solid #0a3256; box-shadow:0 10px 24px rgba(5,30,60,.5), inset 0 0 0 4px #0a3256;
  overflow:hidden; background:#0a3256; z-index:5; animation:intip 4s ease-in-out infinite;}
.tingkap img{width:100%; height:100%; object-fit:cover;}
.tingkap .baut{position:absolute; width:9px; height:9px; border-radius:50%; background:#f2c45c; box-shadow:0 0 0 2px #0a3256;}
.gelembung-kecil{position:absolute; left:-150px; top:-112px; background:#fff; color:#0b2a45; border:3px solid #0a3256;
  border-radius:16px; padding:2px 10px; font-family:'Pirata One',cursive; font-size:1.1rem; z-index:6;
  opacity:0; transition:opacity .3s; white-space:nowrap;}
.tingkap-bungkus:hover .gelembung-kecil{opacity:1;}
@keyframes intip{0%,100%{transform:translateY(0) rotate(-4deg);}50%{transform:translateY(-10px) rotate(3deg);}}
/* Maskot 2: duduk di atas sudut kanan panel sambil berbicara */
.penjaga{position:absolute; right:-112px; top:-58px; width:150px; z-index:5; transform:rotate(7deg);
  animation:jaga 3.6s ease-in-out infinite; transform-origin:50% 100%;}
.penjaga img{width:100%; border:4px solid #0a3256; border-radius:18px; background:#f2f9ff; padding:3px;
  box-shadow:0 10px 22px rgba(5,30,60,.45), inset 0 0 0 2px #f2c45c;}
.gelembung{position:absolute; right:160px; top:6px; width:220px; background:#ffffff; color:#0b2a45;
  border:3px solid #0a3256; border-radius:18px; padding:.5rem .8rem; font-family:'Pirata One',cursive;
  font-size:1.15rem; line-height:1.25; text-align:center; box-shadow:0 6px 14px rgba(5,30,60,.3); z-index:6;}
.gelembung:after{content:""; position:absolute; right:-16px; top:26px; border:9px solid transparent; border-left:14px solid #0a3256;}
.gelembung:before{content:""; position:absolute; right:-10px; top:28px; border:7px solid transparent; border-left:11px solid #fff; z-index:1;}
@keyframes jaga{0%,100%{transform:rotate(7deg) translateY(0);}50%{transform:rotate(3deg) translateY(-6px);}}
/* Maskot tambahan (maskot3 dst.) melayang di pojok kanan bawah */
.maskot-lain{position:fixed; right:22px; bottom:22px; display:flex; gap:12px; z-index:5;}
.maskot-lain img{width:110px; border:4px solid #0a3256; border-radius:18px; background:#f2f9ff; padding:3px;
  animation:intip 4s ease-in-out infinite;}
@media (max-width:1250px){
  .penjaga{right:-30px; top:-50px; width:105px;} .gelembung{width:170px; right:115px; font-size:1rem;}
  .tingkap{left:-40px; width:105px; height:105px;}
}
</style>
"""
MASKOT_CSS = "\n".join(b for b in MASKOT_CSS.splitlines() if b.strip())


def gambar_maskot(nomor: int):
    return daftar_maskot[nomor][0] if len(daftar_maskot) > nomor else None


slot_penjaga = st.empty()

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []


def catat(isbn, jenis, hasil):
    st.session_state.riwayat.insert(0, {"ISBN": isbn, "Jenis": jenis, "Hasil": hasil})


def tampil_tabel(df: pd.DataFrame):
    """Tampilkan tabel sebagai HTML bertema agar selalu terbaca."""
    st.markdown(df.to_html(index=False, classes="tabel", border=0), unsafe_allow_html=True)


def catatan(teks: str):
    st.markdown(f'<div class="catatan">{teks}</div>', unsafe_allow_html=True)


PESAN_MASKOT = {
    "💰 Harta Asli!": "Hartanya ASLI! Ayo angkat sauh, Kapten! ⛵",
    "☠️ Peta Palsu!": "Awas! Peta palsu! Jangan sampai tertipu! ⚔️",
    "💰 Digit Ditemukan!": "Digit terakhirnya ketemu! Hebat! 🧭",
    "☠️ Salah Arah!": "Eh, kita salah arah... coba cek lagi angkanya!",
    "💰 Peta Baru Siap!": "Peta lama jadi baru! Berlayar lagi! ⚓",
    "☠️ Peta Lama Rusak!": "Peta lamanya rusak, tidak bisa diubah!",
}


def kartu(valid: bool, judul: str, isi: str):
    st.session_state.pesan_maskot = PESAN_MASKOT.get(judul, "Siap, Kapten!")
    kelas = "valid" if valid else "gagal"
    st.markdown(f'<div class="kartu {kelas}"><h2>{judul}</h2>{isi}</div>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## ⚓ Buku Panduan Kapten")
    st.markdown(
        """
**ISBN-10**
Bobot 10, 9, 8, … 1
Jumlah harus habis dibagi **11**.
Digit akhir boleh **X** (= 10).

**ISBN-13**
Bobot bergantian 1, 3, 1, 3, …
Jumlah harus habis dibagi **10**.
"""
    )
    st.markdown("---")
    if gambar_latar:
        st.caption(f"🖼️ Gambar latar: {nama_file_latar}")
    else:
        st.caption(
            "🖼️ Gambar latar belum ditemukan. Simpan gambar bernama **latar.jpg** "
            f"di folder ini:\n\n`{FOLDER_APP}`"
        )
    st.caption(f"🗺️ Dekorasi: {len(dekorasi)} gambar" if dekorasi else "🗺️ Dekorasi: belum ada (folder 'dekorasi' tidak ditemukan)")
    st.caption(f"🐾 Maskot: {', '.join(n for _, n in daftar_maskot) or 'belum ada (beri nama maskot…)'}")

st.markdown(
    """
<div class="judul">
  <div style="font-size:3rem">🏴‍☠️</div>
  <h1>Peta Harta ISBN</h1>
  <div class="garis"></div>
  <p>Periksa apakah kode buku itu harta asli... atau peta palsu!</p>
</div>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Periksa", "🧭 Cari Digit", "⚓ Ubah 10→13", "💰 Peti Riwayat"])

with tab1:
    st.markdown("### Periksa Keaslian Peta")
    with st.form("form_validasi"):
        isbn = st.text_input("Masukkan ISBN-10 atau ISBN-13", placeholder="contoh: 978-0-306-40615-7")
        kirim = st.form_submit_button("🔍 Periksa Peta!")

    if kirim and isbn.strip():
        bersih = bersihkan(isbn)
        if len(bersih) == 10:
            jenis, fungsi, m = "ISBN-10", langkah_isbn10, 11
        elif len(bersih) == 13:
            jenis, fungsi, m = "ISBN-13", langkah_isbn13, 10
        else:
            jenis, fungsi, m = None, None, None

        if jenis is None:
            kartu(False, "☠️ Peta Palsu!", f"<p>Panjangnya {len(bersih)} karakter. ISBN harus 10 atau 13 digit.</p>")
            catat(isbn, "?", "Tidak valid")
        else:
            valid, pesan, tabel, total, sisa = fungsi(bersih)
            if tabel is None:
                kartu(False, "☠️ Peta Palsu!", f"<p>{pesan}</p>")
            else:
                if valid:
                    kartu(True, "💰 Harta Asli!", f'<div class="kode">{bersih}</div><p>{jenis} ini <b>VALID</b>.</p>')
                else:
                    kartu(False, "☠️ Peta Palsu!", f'<div class="kode">{bersih}</div><p>{jenis} ini <b>TIDAK VALID</b>.</p>')

                st.markdown("#### 📜 Catatan Perhitungan Navigator")
                tampil_tabel(tabel)
                st.markdown(
                    f'<div class="rumus">Jumlah = {total} &nbsp;|&nbsp; {total} mod {m} = {sisa} '
                    f'&nbsp;→&nbsp; {"sisa 0, VALID ✔" if sisa == 0 else "sisa bukan 0, TIDAK VALID ✘"}</div>',
                    unsafe_allow_html=True,
                )
            catat(isbn, jenis, "Valid" if valid else "Tidak valid")

with tab2:
    st.markdown("### Temukan Digit Terakhir yang Hilang")
    st.write("Masukkan 9 digit (untuk ISBN-10) atau 12 digit (untuk ISBN-13). Navigator akan menghitung digit pemeriksanya.")
    with st.form("form_cek"):
        awal = st.text_input("Digit awal", placeholder="contoh: 030640615 atau 978030640615")
        cari = st.form_submit_button("🧭 Hitung Digit!")

    if cari and awal.strip():
        d = bersihkan(awal)
        if not d.isdigit():
            kartu(False, "☠️ Salah Arah!", "<p>Hanya boleh berisi angka.</p>")
        elif len(d) == 9:
            cek = check_digit_isbn10(d)
            kartu(True, "💰 Digit Ditemukan!",
                  f'<p>Digit pemeriksa: <b style="font-size:1.6rem">{cek}</b></p><div class="kode">{d}{cek}</div><p>ISBN-10 lengkap</p>')
            catat(d + cek, "ISBN-10", "Digit dihitung")
        elif len(d) == 12:
            cek = check_digit_isbn13(d)
            kartu(True, "💰 Digit Ditemukan!",
                  f'<p>Digit pemeriksa: <b style="font-size:1.6rem">{cek}</b></p><div class="kode">{d}{cek}</div><p>ISBN-13 lengkap</p>')
            catat(d + cek, "ISBN-13", "Digit dihitung")
        else:
            kartu(False, "☠️ Salah Arah!", f"<p>Panjangnya {len(d)} digit. Masukkan 9 atau 12 digit.</p>")

with tab3:
    st.markdown("### Ubah Peta Lama Menjadi Peta Baru")
    st.write("ISBN-10 diubah menjadi ISBN-13 dengan menambahkan awalan **978** lalu menghitung ulang digit pemeriksa.")
    with st.form("form_konversi"):
        lama = st.text_input("ISBN-10", placeholder="contoh: 0-306-40615-2")
        ubah = st.form_submit_button("⚓ Ubah Peta!")

    if ubah and lama.strip():
        valid, pesan, *_ = langkah_isbn10(lama)
        if not valid:
            kartu(False, "☠️ Peta Lama Rusak!", f"<p>{pesan or 'ISBN-10 tidak valid, tidak bisa diubah.'}</p>")
        else:
            baru = isbn10_ke_isbn13(lama)
            kartu(True, "💰 Peta Baru Siap!",
                  f'<p>{bersihkan(lama)}</p><p style="font-size:1.6rem">⬇</p><div class="kode">{baru}</div>')
            catat(baru, "ISBN-13", "Hasil konversi")

with tab4:
    st.markdown("### Isi Peti Harta Karun")
    if st.session_state.riwayat:
        tampil_tabel(pd.DataFrame(st.session_state.riwayat))
        if st.button("🗑️ Kosongkan Peti"):
            st.session_state.riwayat = []
            st.rerun()
    else:
        catatan("Peti masih kosong. Periksa beberapa ISBN dulu, Kapten!")

st.markdown('<div class="garis"></div><p style="text-align:center;font-style:italic">⚓ Berlayar dengan aritmetika modulo ⚓</p>',
            unsafe_allow_html=True)

st.markdown(MASKOT_CSS, unsafe_allow_html=True)

penjaga = gambar_maskot(1) or (gambar_maskot(0) if len(daftar_maskot) == 1 else None)
if penjaga:
    pesan = st.session_state.get("pesan_maskot", "Ahoy, Kapten! Coba periksa satu ISBN!")
    slot_penjaga.markdown(
        f'<div class="jangkar"><div class="penjaga"><div class="gelembung">{pesan}</div>'
        f'<img src="{penjaga}"></div></div>',
        unsafe_allow_html=True,
    )

if len(daftar_maskot) >= 2:
    baut = "".join(
        f'<span class="baut" style="left:{x}%; top:{y}%;"></span>'
        for x, y in [(46, 2), (46, 90), (2, 46), (90, 46)]
    )
    st.markdown(
        f'<div class="jangkar tingkap-bungkus"><div class="gelembung-kecil">...meong.</div>'
        f'<div class="tingkap"><img src="{gambar_maskot(0)}">{baut}</div></div>',
        unsafe_allow_html=True,
    )

if len(daftar_maskot) > 2:
    st.markdown(
        '<div class="maskot-lain">' + "".join(f'<img src="{u}">' for u, _ in daftar_maskot[2:]) + "</div>",
        unsafe_allow_html=True,
    )