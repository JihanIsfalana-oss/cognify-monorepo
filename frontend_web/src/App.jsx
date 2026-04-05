// src/App.jsx
import React, { useState, useEffect, useMemo } from 'react';
import './assets/globals.css';

// 1. Impor Data & Logika
import { initialLands, initialRegionalPrices, initialInboundRequests } from './data/mockData';

// 2. Impor Komponen UI
import Sidebar from './components/Sidebar';
import MobileNav from './components/MobileNav';
import NotificationCenter from './components/NotificationCenter';

// 3. Impor Halaman
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import FarmerMarket from './pages/FarmerMarket';
import PlantDoctor from './pages/PlantDoctor';
import RadarDBSCAN from './pages/RadarDBSCAN';
import BuyerMarket from './pages/BuyerMarket';
import InputLahan from './pages/InputLahan';

const App = () => {
  // ─── STATE UI & NAVIGASI ──────────────────────────────────────────────────
  const [view, setView] = useState('landing'); 
  const [role, setRole] = useState(null); 
  const [activeLandId, setActiveLandId] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRadarInitialized, setIsRadarInitialized] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [inputPlanText, setInputPlanText] = useState(""); 
  const [scanState, setScanState] = useState('idle'); 
  const [scanResult, setScanResult] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [irrigationStatus, setIrrigationStatus] = useState('idle');

  // ─── STATE DATA UTAMA ─────────────────────────────────────────────────────
  const [lands, setLands] = useState(initialLands);
  const [inboundRequests, setInboundRequests] = useState(initialInboundRequests);
  const regionalPrices = initialRegionalPrices;

  // Mengambil data lahan yang sedang aktif dipilih
  const activeLand = useMemo(() => lands.find(l => l.id === activeLandId) || lands[0], [lands, activeLandId]);

  // ─── FUNGSI & LOGIKA APLIKASI ─────────────────────────────────────────────

  // Fungsi Notifikasi
  const addNotification = (msg) => setNotifications(prev => [{ id: Date.now(), text: msg }, ...prev]);

  useEffect(() => {
    if (notifications.length > 0) {
      const timer = setTimeout(() => {
        setNotifications(prev => prev.slice(0, -1));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notifications]);

  // Pilihan Role (Landing Page)
  const handleRoleSelection = (selectedRole) => {
    setRole(selectedRole);
    setView(selectedRole === 'farmer' ? 'dashboard' : 'buyer_market');
  };

  // Logika Dashboard: Toggle Tugas
  const toggleTask = (landId, taskId) => {
    setLands(prev => prev.map(land => {
      if (land.id !== landId) return land;
      const newTasks = land.tasks.map(t => t.id === taskId ? { ...t, status: t.status === 'done' ? 'pending' : 'done' } : t);
      return { ...land, tasks: newTasks };
    }));
  };

  // Logika Dashboard: Irigasi
  const executeIrrigation = () => {
    if (irrigationStatus !== 'idle') return;
    setIrrigationStatus('watering');
    addNotification("Sinyal kontrol aktuator pompa dikirim ke Edge-Node.");
    setTimeout(() => {
      setIrrigationStatus('done');
      addNotification("Irigasi presisi FAO-56 selesai dieksekusi.");
      setLands(prev => prev.map(l => l.id === activeLandId ? { ...l, sensorData: {...l.sensorData, soilMoisture: 85} } : l));
      setTimeout(() => setIrrigationStatus('idle'), 5000);
    }, 3000);
  };

  const addNewLand = async () => {
    if (!inputPlanText || inputPlanText.length <= 5) return;
    setIsProcessing(true);

    try {
      // 1. Menembak API NLP FAO-56
      const response = await fetch('http://127.0.0.1:8000/api/nlp/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ raw_text: inputPlanText })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      // 2. Menerima Balasan dari AI
      const aiData = await response.json();
      console.log("Balasan AI:", aiData);

      const newId = Date.now();
      
      // 3. Menggunakan data hasil ekstraksi SpaCy (Backend)
      const detectedCrop = aiData.komoditas !== "Tidak Diketahui" ? aiData.komoditas : "Belum Ditentukan";
      const detectedArea = aiData.luas_lahan_ha > 0 ? `${aiData.luas_lahan_ha} Hektar` : "1 Hektar";
      const detectedLocation = aiData.lokasi !== "Tidak Diketahui" ? aiData.lokasi : "Lokasi Belum Dipetakan";
      
      let dynamicName = "Lahan Baru";
      if (aiData.komoditas !== "Tidak Diketahui" && aiData.lokasi !== "Tidak Diketahui") {
        dynamicName = `Lahan ${aiData.komoditas} ${aiData.lokasi}`;
      } else if (aiData.komoditas !== "Tidak Diketahui") {
        dynamicName = `Lahan ${aiData.komoditas} Baru`;
      } else if (aiData.lokasi !== "Tidak Diketahui") {
        dynamicName = `Lahan Baru ${aiData.lokasi}`;
      }

      const newLand = {
        id: newId, name: dynamicName, 
        crop: detectedCrop, 
        area: detectedArea, 
        location: detectedLocation, 
        budget: 5000000, realSpending: 0, currentDayIdx: 0, 
        reputationScore: Math.round(aiData.confidence * 100) || 100,
        sensorData: { ph: 7.0, soilMoisture: 50, battery: 100, connection: 'Pending Setup' },
        progress: new Array(10).fill(0),
        tasks: [{ id: Date.now()+1, title: 'Instalasi Edge-Node ESP32', type: 'Hardware', time: '08:00', status: 'pending', priority: 'High' }], 
        revenue: 0
      };

      // 4. Memasukkan Lahan ke Layar
      setLands(prev => [...prev, newLand]);
      setActiveLandId(newId);
      setInputPlanText("");
      setView('dashboard');

      addNotification(aiData.message || "Lahan Baru Berhasil Ditambahkan!");

    } catch (error) {
      console.error("Gagal menambahkan lahan:", error);
      addNotification("🚨 Gagal terhubung ke Server!");
    } finally {
      setIsProcessing(false);
    }
  };
  // Logika Pasar Petani (Approve/Reject PO)
  const approvePO = (id) => {
    setInboundRequests(prev => prev.map(req => req.id === id ? { ...req, status: 'approved' } : req));
    addNotification("Kontrak PO Premium disetujui melalui Predictive Matchmaking.");
  };

  const rejectPO = (id) => {
    setInboundRequests(prev => prev.map(req => req.id === id ? { ...req, status: 'rejected' } : req));
    addNotification("Permintaan PO ditolak.");
  };

  // Logika Pasar Pembeli (Buat PO)
  const handlePreOrder = (land) => {
    const newReq = {
      id: Date.now(),
      buyerName: "Anda (Simulasi Pembeli)",
      crop: land.crop,
      quantity: "1 Ton",
      price: land.crop === "Padi" ? 7500 : land.crop === "Cabai Rawit" ? 45000 : 6000,
      status: "pending",
      location: "Lokasi Anda",
      distance: Math.floor(Math.random() * 20) + 1,
      reqScore: 95
    };
    setInboundRequests(prev => [newReq, ...prev]);
    addNotification(`PO Premium berhasil dikirim ke ${land.name}.`);
  };

  // Logika AI Doctor
  const startPlantScan = () => {
    setScanState('scanning');
    setScanResult(null);
    setTimeout(() => {
      setScanResult({ 
        disease: "Wereng Batang Coklat (WBC)", 
        accuracy: "98.7%", 
        latency: "42ms (INT8 Edge Mode)",
        solution: "Gunakan Insektisida sistemik BPMC. Isolasi radius 5 meter dari titik temuan. Sistem telah memicu Radar DBSCAN radius 5 KM." 
      });
      setScanState('result');
    }, 1800); 
  };

  const injectDoctorTask = () => {
    const newTask = { id: Date.now(), title: 'Semprot Darurat Wereng (WBC)', status: 'pending', priority: 'CRITICAL', time: 'Segera', type: 'Emergency' };
    setLands(prev => prev.map(l => l.id === activeLandId ? { ...l, tasks: [newTask, ...l.tasks] } : l));
    addNotification("Tugas intervensi agronomis ditambahkan ke antrean Edge-Node.");
    setScanState('idle');
    setView('dashboard');
  };

  const reportToRadar = () => {
    setIsRadarInitialized(true);
    addNotification("Sinyal bahaya dikirim ke algoritma DBSCAN Radar Spasial.");
    setView('radar');
  };

  // ─── ROUTER HALAMAN ───────────────────────────────────────────────────────
  const renderContent = () => {
    switch(view) {
      case 'landing':      
        return <LandingPage handleRoleSelection={handleRoleSelection} />;
      case 'dashboard':    
        return <Dashboard 
                 lands={lands} 
                 activeLand={activeLand}
                 activeLandId={activeLandId} 
                 setActiveLandId={setActiveLandId} 
                 toggleTask={toggleTask} 
                 irrigationStatus={irrigationStatus}
                 executeIrrigation={executeIrrigation}
                 setView={setView}
               />;
      case 'market':       
        return <FarmerMarket 
                 regionalPrices={regionalPrices} 
                 inboundRequests={inboundRequests} 
                 approvePO={approvePO} 
                 rejectPO={rejectPO}
               />;
      case 'doctor':       
        return <PlantDoctor 
                 scanState={scanState}
                 setScanState={setScanState}
                 scanResult={scanResult}
                 setScanResult={setScanResult}
                 startPlantScan={startPlantScan}
                 injectDoctorTask={injectDoctorTask}
                 reportToRadar={reportToRadar}
               />;
      case 'radar':        
        return <RadarDBSCAN 
                 isRadarInitialized={isRadarInitialized}
                 setView={setView}
               />;
      case 'buyer_market': 
        return <BuyerMarket 
                 lands={lands}
                 searchTerm={searchTerm}
                 setSearchTerm={setSearchTerm}
                 handlePreOrder={handlePreOrder}
               />;
      case 'input':        
        return <InputLahan 
                 inputPlanText={inputPlanText}
                 setInputPlanText={setInputPlanText}
                 addNewLand={addNewLand}
                 isProcessing={isProcessing}
               />;
      default:             
        return <LandingPage handleRoleSelection={handleRoleSelection} />;
    }
  };

  // ─── KERANGKA UTAMA ───────────────────────────────────────────────────────
  return (
    <div className="cognify-root" style={{
      minHeight:'100vh', display:'flex',
      fontFamily:"'DM Sans', sans-serif",
      background: role ? 'var(--green-100)' : 'transparent',
      padding: role ? '12px' : 0,
      overflow:'hidden'
    }}>
      <NotificationCenter notifications={notifications} setNotifications={setNotifications} />

      {role && <Sidebar role={role} setRole={setRole} view={view} setView={setView} />}

      <main style={{
        flex:1, borderRadius: role ? 28 : 0,
        background:'white',
        overflow:'hidden', display:'flex', flexDirection:'column',
        boxShadow: role ? '0 8px 48px rgba(5,46,22,0.1)' : 'none'
      }}>
        <div className="scrollbar-hide" style={{
          flex:1, overflowY:'auto', maxHeight:'100vh',
          padding: view === 'landing' ? 0 : '32px 40px 80px',
          scrollBehavior:'smooth'
        }}>
          {renderContent()}
        </div>
      </main>

      <MobileNav role={role} setRole={setRole} view={view} setView={setView} />
    </div>
  );
};

export default App;