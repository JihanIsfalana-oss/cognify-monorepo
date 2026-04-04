// src/data/mockData.js
export const initialRegionalPrices = [
  { crop: "Padi GKG", marketPrice: 7200, middlemanPrice: 6100, trend: "stable", info: "Harga stabil di tingkat penggilingan lokal Indramayu." },
  { crop: "Cabai Rawit", marketPrice: 45000, middlemanPrice: 32000, trend: "up", info: "Pasokan berkurang akibat gagal panen di beberapa kecamatan." },
  { crop: "Jagung Pipil", marketPrice: 5400, middlemanPrice: 4200, trend: "down", info: "Panen raya serentak di wilayah sekitar Kandanghaur." },
];

export const initialLands = [
  { 
    id: 1, name: "Lahan Utama Sukahaji", crop: "Padi", area: "2 Hektar", location: "Kec. Sukahaji, Indramayu", 
    budget: 15000000, realSpending: 12150000, currentDayIdx: 45, revenue: 42000000,
    reputationScore: 98,
    sensorData: { ph: 6.4, soilMoisture: 38, battery: 85, connection: 'Edge Offline Mode' },
    progress: new Array(10).fill(100).map((_, i) => i < 5 ? 100 : (i === 5 ? 45 : 0)),
    tasks: [
      { id: 12, title: 'Pemupukan NPK', type: 'Nutrient', time: '08:00', status: 'pending', priority: 'Medium' },
      { id: 13, title: 'Pengecekan Drainase', type: 'Water', time: '10:00', status: 'pending', priority: 'Low' },
    ]
  },
  { 
    id: 2, name: "Petak B Kandanghaur", crop: "Cabai Rawit", area: "0.5 Hektar", location: "Kec. Kandanghaur", 
    budget: 4000000, realSpending: 1200000, currentDayIdx: 12, revenue: 0,
    reputationScore: 85,
    sensorData: { ph: 5.8, soilMoisture: 22, battery: 42, connection: 'Cloud Sync' },
    progress: new Array(10).fill(100).map((_, i) => i < 1 ? 100 : (i === 1 ? 12 : 0)),
    tasks: [
      { id: 21, title: 'Pemasangan Lanjaran', type: 'Support', time: '07:00', status: 'pending', priority: 'High' },
    ]
  }
];

export const initialInboundRequests = [
  { id: 501, buyerName: "Koperasi Pangan Jabar", crop: "Padi GKG", quantity: "5 Ton", price: 7500, status: "pending", location: "Bandung", distance: 120.2, reqScore: 90 },
  { id: 502, buyerName: "Grosir Sayur Ciawi", crop: "Cabai Rawit", quantity: "500kg", price: 43000, status: "pending", location: "Ciawi", distance: 12.8, reqScore: 80 },
];