import os
import random
from itertools import zip_longest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMA_FILE = ["Dataset Kamus.xlsx"]


def cari_file_dataset():
    for nama in NAMA_FILE:
        path = os.path.join(BASE_DIR, nama)
        if os.path.isfile(path):
            return path
    for nama in os.listdir(BASE_DIR):
        if nama.lower().endswith(".xlsx") and "kamus" in nama.lower():
            return os.path.join(BASE_DIR, nama)
    raise FileNotFoundError(f"File dataset kamus (.xlsx) tidak ditemukan di: {BASE_DIR}")


def muat_kamus():
    df = pd.read_excel(cari_file_dataset(), header=1)
    df.columns = [str(c).strip() for c in df.columns]
    kamus = []
    for i, row in df.iterrows():
        indo, konjo, no = row.get("Bahasa Indonesia"), row.get("Bahasa Konjo"), row.get("No")
        if pd.isna(indo) or pd.isna(konjo):
            continue
        kamus.append({"no": int(no) if not pd.isna(no) else i + 1,
                       "indonesia": str(indo).strip(), "konjo": str(konjo).strip()})
    return kamus


KAMUS = muat_kamus()
ALPHABET = sorted(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ").union(*[set(k["konjo"].upper()) for k in KAMUS]))

STATE = {"jalan": False, "target": None, "arti": None, "populasi": [], "asal": [],
          "fit_awal": [], "prob": [], "kumulatif": [], "roulette": [], "parents": [],
          "cross": [], "anak_mentah": [], "mutasi": [], "populasi_baru": [],
          "fit_baru": [], "mutation_rate": 0.1}


def cetak_tabel(header, baris):
    kolom = list(zip(*([header] + baris))) if baris else [[h] for h in header]
    lebar = [max(len(str(s)) for s in kol) + 2 for kol in kolom]
    garis = "+" + "+".join("-" * w for w in lebar) + "+"
    fmt = lambda sel: "|" + "|".join(f" {str(v):<{w-2}} " for v, w in zip(sel, lebar)) + "|"
    print(garis); print(fmt(header)); print(garis)
    for b in baris:
        print(fmt(b))
    print(garis)


def judul(teks, karakter="=", lebar=68):
    print("\n" + karakter * lebar); print(teks.center(lebar)); print(karakter * lebar)


def baca_pilihan_menu(pesan, valid):
    while True:
        t = input(pesan).strip()
        if t in valid:
            return t
        print(f"Pilihan tidak dikenali. Masukkan salah satu: {', '.join(valid)}\n")


def input_angka(pesan, default, tipe=float, minimum=None, maksimum=None):
    while True:
        m = input(f"{pesan} (default {default}): ").strip()
        if m == "":
            return default
        try:
            nilai = tipe(m.replace(",", "."))
        except ValueError:
            print("Input harus berupa angka. Silakan coba lagi.\n"); continue
        if minimum is not None and nilai < minimum:
            print(f"Nilai minimal adalah {minimum}.\n"); continue
        if maksimum is not None and nilai > maksimum:
            print(f"Nilai maksimal adalah {maksimum}.\n"); continue
        return nilai


def hitung_fitness(individu, target):
    penyebut = max(len(individu), len(target))
    return sum(a == b for a, b in zip(individu, target)) / penyebut if penyebut else 0.0


def seleksi_roulette_wheel(populasi, fitness_list, n):
    total = sum(fitness_list)
    prob = [1 / len(populasi)] * len(populasi) if total == 0 else [f / total for f in fitness_list]
    kumulatif, acc = [], 0
    for p in prob:
        acc += p; kumulatif.append(acc)
    kumulatif[-1] = 1.0
    hasil = []
    for _ in range(n):
        r = random.random()
        for i, batas in enumerate(kumulatif):
            if r <= batas:
                hasil.append((r, populasi[i], i)); break
        else:
            hasil.append((r, populasi[-1], len(populasi) - 1))
    return prob, kumulatif, hasil


def crossover(p1, p2):
    m = min(len(p1), len(p2))
    titik = random.randint(1, m - 1) if m > 1 else 1
    return p1[:titik] + p2[titik:], p2[:titik] + p1[titik:], titik


def mutasi(individu, rate, alphabet):
    baru, detail = list(individu), []
    for i in range(len(baru)):
        if random.random() < rate:
            lama = baru[i]
            baru[i] = random.choice(alphabet)
            detail.append((i + 1, lama, baru[i]))
    return "".join(baru), detail


def baris_perbandingan(individu, target):
    pasangan = list(zip_longest(target, individu, fillvalue="_"))
    tgt = " ".join(t for t, _ in pasangan)
    ind = " ".join(i for _, i in pasangan)
    tanda = " ".join("v" if t == i and t != "_" else "." for t, i in pasangan)
    return tgt, ind, tanda


def tampilkan_kamus():
    judul("DAFTAR KAMUS BAHASA DAERAH (BAHASA KONJO)")
    cetak_tabel(["No", "Bahasa Indonesia", "Bahasa Konjo"],
                [[k["no"], k["indonesia"], k["konjo"]] for k in KAMUS])
    print(f"\nTotal data: {len(KAMUS)} kata\n")


def cari_kata():
    kunci = input("Masukkan kata (Bahasa Indonesia atau Bahasa Konjo): ").strip().lower()
    if not kunci:
        print("\nKata tidak boleh kosong.\n"); return
    for k in KAMUS:
        if kunci in (k["indonesia"].strip().lower(), k["konjo"].strip().lower()):
            print(f"\nDitemukan! '{k['indonesia']}' <-> '{k['konjo']}'\n"); return
    mirip = [k for k in KAMUS if kunci in k["indonesia"].lower() or kunci in k["konjo"].lower()]
    if mirip:
        print("\nTidak ada kecocokan persis, tapi ditemukan kata yang mirip:")
        for k in mirip:
            print(f"  - '{k['indonesia']}' <-> '{k['konjo']}'")
        print()
    else:
        print("\nKata tidak ditemukan dalam kamus.\n")


def pilih_target():
    print("\n===== PILIH TARGET KATA KONJO =====")
    for k in KAMUS:
        print(f"{k['no']}. {k['konjo']}  =  {k['indonesia']}")
    print("\nKetik NOMOR data di atas, atau ketik langsung katanya (Bahasa Indonesia / Bahasa Konjo).")
    while True:
        teks = input("Pilihan target: ").strip()
        if not teks:
            print("Input tidak boleh kosong. Coba lagi.\n"); continue
        if teks.isdigit():
            cocok = [k for k in KAMUS if k["no"] == int(teks)]
            if cocok:
                return cocok[0]["konjo"].upper(), cocok[0]["indonesia"]
            print(f"Nomor {teks} tidak ada dalam daftar kamus. Coba lagi.\n"); continue
        tl = teks.lower()
        cocok = [k for k in KAMUS if k["indonesia"].lower() == tl or k["konjo"].lower() == tl]
        if cocok:
            return cocok[0]["konjo"].upper(), cocok[0]["indonesia"]
        print("Kata/nomor tersebut tidak ditemukan dalam kamus. Coba lagi.\n")


def _pastikan_jalan():
    if not STATE["jalan"]:
        print("\nBelum ada proses GA yang dijalankan. Silakan pilih menu 3 terlebih dahulu.\n")
        return False
    return True


def _cetak_individu(label, ind, target, arti=None):
    tgt, ii, tanda = baris_perbandingan(ind, target)
    penyebut = max(len(ind), len(target))
    fit = hitung_fitness(ind, target)
    benar = round(fit * penyebut)
    ket = f"  (artinya '{arti}')" if arti else ""
    print(f"{label}: {ind}{ket}")
    print(f"  Target   : {tgt}")
    print(f"  Individu : {ii}")
    print(f"  Cocok?   : {tanda}")
    print(f"  -> Huruf benar = {benar}/{penyebut}  =>  Fitness = {fit:.3f}\n")


def jalankan_algoritma_genetika():
    target, arti = pilih_target()
    rate = input_angka("Peluang mutasi tiap gen (0-1)", 0.1, float, 0.0, 1.0)

    populasi = [k["konjo"].upper() for k in KAMUS]
    asal = [k["indonesia"] for k in KAMUS]
    n = len(populasi)
    fit_awal = [hitung_fitness(ind, target) for ind in populasi]
    prob, kumulatif, roulette = seleksi_roulette_wheel(populasi, fit_awal, n)
    parents = [r[1] for r in roulette]

    cross, anak_mentah = [], []
    for i in range(0, n, 2):
        p1, p2 = parents[i], parents[i + 1] if i + 1 < n else parents[0]
        c1, c2, titik = crossover(p1, p2)
        cross.append((p1, p2, titik, c1, c2))
        anak_mentah.extend([c1, c2])
    anak_mentah = anak_mentah[:n]

    mutasi_result, populasi_baru = [], []
    for anak in anak_mentah:
        baru, detail = mutasi(anak, rate, ALPHABET)
        mutasi_result.append((anak, baru, detail))
        populasi_baru.append(baru)

    fit_baru = [hitung_fitness(ind, target) for ind in populasi_baru]

    STATE.update(jalan=True, target=target, arti=arti, populasi=populasi, asal=asal,
                 fit_awal=fit_awal, prob=prob, kumulatif=kumulatif, roulette=roulette,
                 parents=parents, cross=cross, anak_mentah=anak_mentah, mutasi=mutasi_result,
                 populasi_baru=populasi_baru, fit_baru=fit_baru, mutation_rate=rate)

    judul("GENETIC ALGORITHM - PROSES 1 GENERASI PENUH")
    print(f"Target Konjo : {target}\nTarget Indo  : {arti}")
    tampilkan_populasi(); hasil_fitness(); seleksi_roulette_menu()
    cross_over_menu(); mutasi_menu(); generasi_baru_menu()
    judul("PROSES GENERASI KE-1 SELESAI")
    print("(Menu 4-9 bisa dipakai kapan saja untuk melihat ulang tiap tahap)\n")


def tampilkan_populasi():
    if not _pastikan_jalan():
        return
    judul(f"POPULASI AWAL (dari KAMUS)  |  Target: {STATE['target']} <- '{STATE['arti']}'", "-")
    baris = [[i, ind, arti, f"{fit:.3f}"] for i, (ind, arti, fit) in
             enumerate(zip(STATE["populasi"], STATE["asal"], STATE["fit_awal"]), 1)]
    cetak_tabel(["No", "Individu (Konjo)", "Arti (Indonesia)", "Fitness"], baris)
    print(f"\nTotal fitness awal : {sum(STATE['fit_awal']):.3f}\n")


def hasil_fitness():
    if not _pastikan_jalan():
        return
    target = STATE["target"]
    judul("PERHITUNGAN FITNESS", "-")
    print(f"Populasi = kata-kata KAMUS, dicocokkan ke target: '{STATE['arti']}' -> '{target}'")
    print("Rumus : Fitness_i = huruf cocok posisi sama / MAX(panjang individu, panjang target)\n")
    for i, (ind, arti, _) in enumerate(zip(STATE["populasi"], STATE["asal"], STATE["fit_awal"]), 1):
        _cetak_individu(f"Individu I{i}", ind, target, arti)
    print(f"Total fitness populasi = {sum(STATE['fit_awal']):.3f}")
    print(f"Fitness rata-rata      = {sum(STATE['fit_awal']) / len(STATE['fit_awal']):.3f}\n")


def seleksi_roulette_menu():
    if not _pastikan_jalan():
        return
    judul("TABEL PROBABILITAS & INTERVAL (ROULETTE WHEEL)", "-")
    baris, bawah = [], 0.0
    for i, (fit, p, c) in enumerate(zip(STATE["fit_awal"], STATE["prob"], STATE["kumulatif"]), 1):
        baris.append([f"I{i}", f"{fit:.3f}", f"{p:.3f}", f"{bawah:.3f} - {c:.3f}"]); bawah = c
    cetak_tabel(["Individu", "Fitness", "Probabilitas", "Interval"], baris)
    print("\nProses penarikan bilangan acak r (dibangkitkan otomatis, 0-1):")
    baris2 = [[idx, f"{r:.4f}", f"I{i+1}", ind, f"Parent {idx}"]
              for idx, (r, ind, i) in enumerate(STATE["roulette"], 1)]
    cetak_tabel(["#", "r", "Interval Terpilih", "Individu Terpilih", "Sebagai"], baris2)
    print()


def cross_over_menu():
    if not _pastikan_jalan():
        return
    judul("PROSES CROSS OVER (Single-Point)", "-")
    for idx, (p1, p2, titik, c1, c2) in enumerate(STATE["cross"], 1):
        print(f"\nPasangan {idx}:")
        print(f"  Parent 1        : {p1}\n  Parent 2        : {p2}")
        print(f"  Titik potong    : setelah gen ke-{titik}")
        print(f"  {p1[:titik]}|{p1[titik:]}   (Parent 1)")
        print(f"  {p2[:titik]}|{p2[titik:]}   (Parent 2)")
        print(f"  Child 1 = {p1[:titik]}|{p2[titik:]} = {c1}")
        print(f"  Child 2 = {p2[:titik]}|{p1[titik:]} = {c2}")
    print()


def mutasi_menu():
    if not _pastikan_jalan():
        return
    judul(f"PROSES MUTASI (peluang mutasi tiap gen = {STATE['mutation_rate']})", "-")
    for idx, (sebelum, sesudah, detail) in enumerate(STATE["mutasi"], 1):
        print(f"\nAnak {idx} sebelum mutasi : {sebelum}")
        if detail:
            for posisi, lama, baru in detail:
                print(f"  -> Gen posisi ke-{posisi} dimutasi: '{lama}' menjadi '{baru}'")
        else:
            print("  -> Tidak ada gen yang termutasi pada individu ini.")
        print(f"Anak {idx} sesudah mutasi  : {sesudah}")
    print()


def generasi_baru_menu():
    if not _pastikan_jalan():
        return
    target = STATE["target"]
    judul(f"HASIL GENERASI KE-1  |  Target: {target} <- '{STATE['arti']}'", "-")
    for i, ind in enumerate(STATE["populasi_baru"], 1):
        _cetak_individu(f"Individu I{i}", ind, target)

    total_awal, total_baru = sum(STATE["fit_awal"]), sum(STATE["fit_baru"])
    print(f"Total fitness populasi awal   : {total_awal:.3f}")
    print(f"Total fitness populasi baru   : {total_baru:.3f}")
    if total_baru > total_awal:
        print("=> Rata-rata kualitas populasi MENINGKAT setelah 1 generasi.")
    elif total_baru < total_awal:
        print("=> Rata-rata kualitas populasi MENURUN setelah 1 generasi (bisa terjadi karena mutasi acak).")
    else:
        print("=> Rata-rata kualitas populasi TETAP setelah 1 generasi.")

    if max(STATE["fit_baru"]) == 1.0:
        pemenang = STATE["populasi_baru"][STATE["fit_baru"].index(1.0)]
        print(f"\n>>> Solusi ditemukan: '{pemenang}' sama persis dengan target '{target}' "
              f"(kata '{STATE['arti']}' dalam Bahasa Konjo)!")
    else:
        print("\n>>> Target belum ditemukan persis pada generasi ke-1 (wajar, GA dapat "
              "dilanjutkan ke generasi berikutnya dengan menjalankan menu 3 lagi).")
    print()


def tampilkan_menu():
    judul("KAMUS BAHASA DAERAH (KONJO) - ALGORITMA GENETIKA")
    for nomor, teks in [("1", "Tampilkan Kamus"), ("2", "Cari Kata"),
                        ("3", "Jalankan Algoritma Genetika"),
                        ("4", "Tampilkan Populasi"), ("5", "Hasil Fitness"),
                        ("6", "Seleksi Roulette"), ("7", "Cross Over"), ("8", "Mutasi"),
                        ("9", "Generasi Baru"), ("10", "Keluar")]:
        print(f"{nomor:>2}. {teks}")


def main():
    aksi = {"1": tampilkan_kamus, "2": cari_kata, "3": jalankan_algoritma_genetika,
            "4": tampilkan_populasi, "5": hasil_fitness, "6": seleksi_roulette_menu,
            "7": cross_over_menu, "8": mutasi_menu, "9": generasi_baru_menu}
    valid = list(aksi.keys()) + ["10"]
    while True:
        tampilkan_menu()
        pilihan = baca_pilihan_menu("Pilih menu (1-10): ", valid)
        if pilihan == "10":
            print("\nTerima kasih. Program selesai."); break
        aksi[pilihan]()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan oleh pengguna. Sampai jumpa!")