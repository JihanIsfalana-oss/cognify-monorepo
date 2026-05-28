<div align="center">
<h1>🌾 Cognify</h1>
<p><strong>Platform Web Pertanian Presisi Berbasis AI untuk Petani Indonesia</strong></p>
<p>
  <img src="https://img.shields.io/badge/status-active_development-yellow?style=flat-square" />
  <img src="https://img.shields.io/badge/backend-65%25-3b82f6?style=flat-square" />
  <img src="https://img.shields.io/badge/frontend-30%25-f97316?style=flat-square" />
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/fastapi-0.109-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/react-18-61dafb?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" />
</p>
<p>
  Platform web yang mengintegrasikan <strong>NLP berbasis Transformer (NER)</strong>,
  <strong>Geospatial Analytics (DBSCAN)</strong>, dan <strong>kalkulasi irigasi standar FAO-56</strong>
  — dirancang untuk memberdayakan petani mengambil keputusan berbasis data, bukan insting.
</p>
</div>
---
 
## ⚠️ Status Proyek
 
> **Proyek ini dalam tahap pengembangan aktif.** Arsitektur, API contract, dan fitur dapat berubah sewaktu-waktu.
 
| Komponen | Lokasi | Status | Progress |
|---|---|---|---|
| Backend API (FastAPI) | `cloud_backend/` | 🟡 In Progress | ~65% |
| NLP / NER Pipeline (spaCy + Transformer) | `cloud_backend/app/services/nlp/` | 🟡 Baseline Ready | ~40% |
| Geospatial Engine (DBSCAN) | `cloud_backend/app/services/geospatial/` | 🟡 In Progress | ~45% |
| Dataset Agronomi (Komoditas & Hama) | `cloud_backend/app/data/` | 🟢 Done | ~100% |
| AI Training Pipeline (MLOps) | `ai_engine/` | 🟠 Eksperimental | ~30% |
| Frontend UI (React) | `frontend_web/` | 🟠 Early Stage | ~30% |
| Autentikasi & User Management | `cloud_backend/` | 🟡 In Progress | ~50% |
| CI/CD Pipeline | `.github/workflows/` | 🟡 Parsial | ~60% |
| Docker / Deployment | — | 🔴 Belum dimulai | 0% |
 
### Catatan Pivot Arsitektur
 
Proyek ini awalnya dikonsepkan dengan arsitektur **hybrid IoT** (ESP32 + LattePanda V1, OpenVINO INT8, off-grid solar). Setelah evaluasi sumber daya, proyek **dipivot sepenuhnya ke platform web** tanpa ketergantungan perangkat keras fisik.
 
**Implikasinya pada repo saat ini:**
 
- Folder `edge_runtime/` dan workflow `esp32-build.yml` adalah **legacy** — tidak aktif digunakan dan sedang dalam proses cleanup
- Schema IoT (`TelemetryPayload`, `BioPhysicalData`, `DeviceStatus`) di `schemas.py` akan direfaktor pada iterasi berikutnya
- Akuisisi data kini sepenuhnya melalui **input manual petani**, **API cuaca pihak ketiga (Open-Meteo / BMKG)**, dan **upload data**
---
 
## 🎯 Masalah yang Dipecahkan
 
Kabupaten Indramayu sebagai lumbung padi nasional mencatat **gagal panen (puso) pada 154 hektar** di Kecamatan Kandanghaur akibat kekeringan dan distribusi air yang tidak terkelola *(Dinas Pertanian Indramayu, 2023)*.
 
Akar masalahnya bukan hanya teknis — melainkan **absennya sistem pendukung keputusan berbasis data** di tingkat petani:
 
- **68%** populasi petani berada dalam kategori ekonomi rentan *(BPS, 2023)*
- Kerugian margin **30–40%** akibat ketergantungan pada metode "insting" tanpa standarisasi irigasi
- Tingkat mortalitas komoditas mencapai **10–76,1%** saat serangan Wereng Batang Coklat menyebar tanpa sistem peringatan komunal
- Mayoritas petani berusia **di atas 40 tahun**, dengan minat generasi muda yang terus menurun
---
 
## ✨ Fitur Inti
 
### 🧠 NLP Agronomis (NER)
Mengekstrak parameter agronomi dari teks bebas bahasa Indonesia yang ditulis petani, mengonversinya ke parameter digital standar FAO-56.
 
```
Input  : "tanah saya kering banget udah 3 hari gak hujan, padi inpari 32 umur 45 hari di kandanghaur"
Output : { komoditas: "Padi", lokasi: "Kandanghaur", luas_lahan_ha: ..., confidence: 0.94 }
```
 
**Model saat ini:** spaCy `id_core_web_sm` + rule-based NER (baseline). Transformer fine-tuning dalam pengerjaan.
 
**Komoditas yang didukung:** Padi, Jagung, Kedelai, Bawang Merah, Cabai Merah, Cabai Rawit, Tomat, Kentang — dengan data Kc FAO-56 per fase tumbuh.
 
### 💧 Rekomendasi Irigasi (FAO-56 Penman-Monteith)
Kalkulasi kebutuhan air harian mempertimbangkan:
- Evapotranspirasi referensi (ET₀) dari data cuaca lokal
- Koefisien tanaman (Kc) per fase pertumbuhan: Awal → Vegetatif Aktif → Pematangan
- Kompensasi defisit jadwal irigasi sebelumnya
### 🗺️ Geospatial Radar Hama (DBSCAN)
Deteksi dan visualisasi penyebaran hama berbasis **Density-Based Spatial Clustering**:
- Radius bahaya terkonfigurasi per jenis hama (1–10 km)
- Ambang batas laporan komunal (`min_pts`) untuk aktivasi early warning
- 10 jenis hama/patogen tercakup, termasuk WBC (Wereng Batang Coklat), Tikus Sawah, dan Penyakit Tungro
### 🤝 Predictive Matchmaking & Sertifikat Lahan
- Skor reputasi budidaya berdasarkan kepatuhan irigasi dan riwayat kesehatan lahan
- Penghubung petani dengan pembeli/koperasi terverifikasi
- Penerbitan **Sertifikat Digital Kesehatan Lahan** *(planned)*
---
