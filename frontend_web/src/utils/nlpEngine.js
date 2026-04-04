// src/utils/nlpEngine.js
export const extractEntities = (text) => {
  const lower = text.toLowerCase();
  let komoditas = "Tidak Terdeteksi";
  let luas = "Tidak Terdeteksi";
  let lokasi = "Tidak Terdeteksi";

  if (lower.includes("padi") || lower.includes("beras")) komoditas = "Padi";
  if (lower.includes("cabe") || lower.includes("cabai")) komoditas = "Cabai Rawit";
  if (lower.includes("jagung")) komoditas = "Jagung";
  if (lower.includes("tomat")) komoditas = "Tomat";
  if (lower.includes("bawang")) komoditas = "Bawang Merah";

  const luasMatch = lower.match(/(\d+(?:\.\d+)?)\s*(hektar|ha|meter|m2|bata)/);
  if (luasMatch) luas = `${luasMatch[1]} ${luasMatch[2].toUpperCase()}`;

  const lokasiRegex = /(?:di|daerah|desa|kecamatan|kec|kabupaten|kab|kota|wilayah)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})/i;
  const matchLokasi = text.match(lokasiRegex);
  if (matchLokasi && matchLokasi[1]) {
    lokasi = matchLokasi[1].split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
  }

  if (lower.includes("kandanghaur")) lokasi = "Kec. Kandanghaur";
  else if (lower.includes("sukahaji")) lokasi = "Kec. Sukahaji";
  else if (lower.includes("indramayu") && lokasi === "Tidak Terdeteksi") lokasi = "Indramayu";
  else if (lower.includes("bandung") && lokasi === "Tidak Terdeteksi") lokasi = "Bandung";
  else if (lower.includes("malang") && lokasi === "Tidak Terdeteksi") lokasi = "Malang";
  else if (lower.includes("bogor") && lokasi === "Tidak Terdeteksi") lokasi = "Bogor";

  return { komoditas, luas, lokasi };
};