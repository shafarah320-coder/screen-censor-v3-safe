# Screen Censor 3.0 — Safe Preview

Versi ini menghapus overlay fullscreen transparan yang menyebabkan black screen.

- Menangkap monitor utama.
- Mendeteksi semua wajah dengan OpenCV.
- Mendeteksi hanya kelas NudeNet `FEMALE_BREAST_EXPOSED`.
- Menggambar kotak hitam di preview dalam jendela aplikasi.

**Batasan:** ini mode preview. Tidak menutupi video langsung pada jendela browser/TikTok. Ini untuk menguji deteksi dengan aman sebelum membuat overlay desktop baru. Deteksi dapat salah atau terlewat.

Workflow memeriksa file `320n.onnx` sebelum dan sesudah PyInstaller. Build akan gagal dengan pesan jelas jika model tidak ikut terpaket.

Artifact: `ScreenCensor-3-SafePreview-Installer`
Installer: `ScreenCensor_3_Safe_Setup.exe`

Jangan gunakan installer Screen Censor versi sebelumnya.
