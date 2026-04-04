import React from 'react';
import { Target, MapPin, WifiOff, Cpu, ThermometerSun, Waves, BatteryMedium, Droplets, Activity, CheckCircle2, Clock, ArrowUpRight, ChevronRight } from 'lucide-react';

const Dashboard = ({ lands, activeLand,activeLandId, setActiveLandId, toggleTask, irrigationStatus, executeIrrigation, setView }) => {
  if (!activeLand) return null;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      {/* Header */}
      <header className="anim-fadeInUp" style={{ display:'flex', flexWrap:'wrap', justifyContent:'space-between', alignItems:'flex-end', gap:16 }}>
        <div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:8, marginBottom:12 }}>
            <select
              value={activeLandId}
              onChange={(e) => setActiveLandId(Number(e.target.value))}
              style={{
                background:'var(--green-100)', color:'var(--green-800)',
                border:'1px solid var(--green-200)', padding:'6px 32px 6px 12px',
                borderRadius:50, fontSize:11, fontWeight:700, letterSpacing:'0.08em',
                textTransform:'uppercase', cursor:'pointer', appearance:'none',
                backgroundImage:`url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2315803d' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
                backgroundRepeat:'no-repeat', backgroundPosition:'right 8px center',
                fontFamily:'inherit'
              }}
            >
              {lands.map(l => <option key={l.id} value={l.id}>{l.name} — {l.crop}</option>)}
            </select>
            <span className="tag-green" style={{ padding:'6px 12px', borderRadius:50, fontSize:11, fontWeight:700, display:'flex', alignItems:'center', gap:6 }}>
              <Target size={11} /> Skor AI: {activeLand.reputationScore}
            </span>
          </div>
          <h2 style={{ fontSize:'clamp(22px, 3vw, 34px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-1px', lineHeight:1.1 }}>
            {activeLand.name}
          </h2>
          <p style={{ color:'#6b7280', fontWeight:500, marginTop:8, fontSize:13, display:'flex', alignItems:'center', gap:6 }}>
            <MapPin size={14} style={{ color:'var(--green-500)' }} /> {activeLand.location} · {activeLand.area}
          </p>
        </div>

        <div style={{ background:'var(--green-950)', color:'white', padding:'14px 20px', borderRadius:20, display:'flex', alignItems:'center', gap:12 }}>
          <div style={{ width:44, height:44, background:'rgba(255,255,255,0.08)', borderRadius:12, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <WifiOff size={16} style={{ color:'var(--green-400)' }} />
          </div>
          <div>
            <p style={{ fontWeight:700, fontSize:13 }}>{activeLand.sensorData.connection}</p>
            <p style={{ fontSize:11, color:'var(--green-400)', marginTop:2 }}>Logging to Flash Memory</p>
          </div>
        </div>
      </header>

      {/* Telemetry + FAO Grid */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))', gap:20 }}>
        {/* Sensor Card */}
        <div className="anim-fadeInUp delay-100" style={{ background:'white', padding:28, borderRadius:28, border:'1.5px solid var(--green-100)', boxShadow:'0 2px 12px rgba(0,0,0,0.04)' }}>
          <h3 style={{ fontWeight:800, color:'var(--green-900)', display:'flex', alignItems:'center', gap:8, fontSize:15, marginBottom:20 }}>
            <Cpu size={18} style={{ color:'var(--green-400)' }} /> Sensor Data
          </h3>
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            {[
              { icon: <ThermometerSun size={16} style={{ color:'#f97316' }}/>, label:'pH Tanah', value: activeLand.sensorData.ph, color: activeLand.sensorData.ph < 6 ? '#ef4444' : 'var(--green-900)' },
              { icon: <Waves size={16} style={{ color: irrigationStatus==='done' ? '#3b82f6' : 'var(--green-400)' }}/>, label:'Kelembapan', value: `${activeLand.sensorData.soilMoisture}%`, color: irrigationStatus==='done' ? '#2563eb' : 'var(--green-900)' },
              { icon: <BatteryMedium size={16} style={{ color:'var(--green-500)' }}/>, label:'Daya Surya', value: `${activeLand.sensorData.battery}%`, color: 'var(--green-600)' },
            ].map(({ icon, label, value, color }) => (
              <div key={label} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'12px 16px', background:'var(--green-50)', borderRadius:14, border:'1px solid var(--green-100)' }}>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  {icon}
                  <span style={{ fontSize:13, fontWeight:600, color:'#374151' }}>{label}</span>
                </div>
                <span style={{ fontWeight:900, fontSize:18, letterSpacing:'-0.5px', color }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* FAO-56 Engine */}
        <div className="anim-fadeInUp delay-200" style={{ background:'var(--green-950)', padding:28, borderRadius:28, color:'white', position:'relative', overflow:'hidden', boxShadow:'0 8px 32px rgba(5,46,22,0.3)', gridColumn:'span 2' }}>
          <div style={{ position:'absolute', top:-60, right:-60, width:240, height:240, background:'radial-gradient(circle, rgba(34,197,94,0.15) 0%, transparent 70%)', borderRadius:'50%', pointerEvents:'none' }} />

          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:24, position:'relative', zIndex:1 }}>
            <div>
              <h3 style={{ fontWeight:800, display:'flex', alignItems:'center', gap:8, fontSize:16 }}>
                <Droplets size={18} style={{ color:'var(--green-400)' }} /> FAO-56 Engine
              </h3>
              <p style={{ fontSize:11, color:'var(--green-400)', marginTop:4 }}>Penman-Monteith Microclimate Control</p>
            </div>
            <div style={{ background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.08)', padding:'6px 12px', borderRadius:10, fontSize:10, fontWeight:700, letterSpacing:'0.1em', display:'flex', alignItems:'center', gap:6, color:'var(--green-300)' }}>
              <Activity size={11} style={{ animation: irrigationStatus==='watering' ? 'blink 1s ease infinite' : 'none' }} />
              LIVE
            </div>
          </div>

          <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:10, marginBottom:24, position:'relative', zIndex:1 }}>
            {[
              ['Radiasi Neto', '18.2', 'MJ'],
              ['Suhu Udara', '32.5', '°C'],
              ['Kec. Angin', '2.1', 'm/s'],
              ['Defisit Uap', '1.4', 'kPa'],
            ].map(([label, val, unit]) => (
              <div key={label} style={{ background:'rgba(255,255,255,0.05)', padding:'14px', borderRadius:16, border:'1px solid rgba(255,255,255,0.06)' }}>
                <p style={{ fontSize:10, color:'var(--green-400)', fontWeight:600, marginBottom:6, textTransform:'uppercase', letterSpacing:'0.08em' }}>{label}</p>
                <p style={{ fontWeight:900, fontSize:20, letterSpacing:'-0.5px' }}>{val} <span style={{ fontSize:11, fontWeight:500, color:'var(--green-500)' }}>{unit}</span></p>
              </div>
            ))}
          </div>

          <div style={{ background:'var(--green-700)', borderRadius:20, padding:'20px 24px', display:'flex', justifyContent:'space-between', alignItems:'center', gap:16, position:'relative', zIndex:1, overflow:'hidden', flexWrap:'wrap' }}>
            {/* Progress bar */}
            <div style={{
              position:'absolute', inset:0,
              background:'var(--green-500)',
              transform: irrigationStatus==='watering' ? 'translateX(0)' : 'translateX(-100%)',
              transition:'transform 3s linear',
              borderRadius:20
            }} />
            <div style={{ position:'relative', zIndex:1 }}>
              <p style={{ fontSize:11, fontWeight:600, color:'rgba(255,255,255,0.7)', marginBottom:4 }}>Instruksi Aktuator Air</p>
              <p style={{ fontSize:32, fontWeight:900, letterSpacing:'-1px' }}>4.2 <span style={{ fontSize:14, fontWeight:500 }}>L/m²</span></p>
            </div>
            <button
              onClick={executeIrrigation}
              disabled={irrigationStatus !== 'idle'}
              style={{
                position:'relative', zIndex:1,
                padding:'12px 24px', borderRadius:14, fontWeight:700, fontSize:13,
                cursor: irrigationStatus !== 'idle' ? 'not-allowed' : 'pointer',
                border:'none', display:'flex', alignItems:'center', gap:8,
                background: irrigationStatus==='done' ? 'var(--green-300)' : irrigationStatus==='watering' ? 'rgba(255,255,255,0.3)' : 'white',
                color: irrigationStatus==='done' ? 'var(--green-900)' : irrigationStatus==='watering' ? 'white' : 'var(--green-800)',
                transition:'all 0.2s ease',
                fontFamily:'inherit'
              }}
            >
              {irrigationStatus==='watering' ? <><Waves size={15} /> Menyiram...</> :
               irrigationStatus==='done' ? <><CheckCircle2 size={15} /> Selesai</> :
               'Eksekusi Irigasi'}
            </button>
          </div>
        </div>
      </div>

      {/* Tasks + Margin */}
      <div style={{ display:'grid', gridTemplateColumns:'2fr 1fr', gap:20 }}>
        {/* Tasks */}
        <div className="anim-fadeInUp delay-300" style={{ background:'white', padding:28, borderRadius:28, border:'1.5px solid var(--green-100)', boxShadow:'0 2px 12px rgba(0,0,0,0.04)' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
            <h3 style={{ fontWeight:800, color:'var(--green-900)', fontSize:16 }}>Tugas Agronomis</h3>
            <div style={{ background:'var(--green-50)', border:'1px solid var(--green-200)', color:'var(--green-700)', padding:'4px 12px', borderRadius:8, fontSize:12, fontWeight:700 }}>
              {activeLand.tasks.filter(t => t.status === 'done').length}/{activeLand.tasks.length} Selesai
            </div>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(220px, 1fr))', gap:12 }}>
            {activeLand.tasks.map(t => (
              <button
                key={t.id}
                onClick={() => toggleTask(activeLand.id, t.id)}
                style={{
                  padding:'16px', borderRadius:18,
                  border: t.priority==='CRITICAL' ? '1.5px solid #fecaca' : '1.5px solid var(--green-100)',
                  background: t.status==='done' ? '#f9fafb' : t.priority==='CRITICAL' ? '#fff5f5' : 'var(--green-50)',
                  display:'flex', alignItems:'center', gap:12, textAlign:'left', cursor:'pointer',
                  transition:'all 0.2s ease', opacity: t.status==='done' ? 0.6 : 1,
                  fontFamily:'inherit'
                }}
              >
                <div style={{
                  width:44, height:44, borderRadius:12, flexShrink:0,
                  display:'flex', alignItems:'center', justifyContent:'center',
                  background: t.status==='done' ? 'var(--green-600)' : t.priority==='CRITICAL' ? '#ef4444' : 'var(--green-200)',
                  color: t.status==='done' || t.priority==='CRITICAL' ? 'white' : 'var(--green-700)'
                }}>
                  <CheckCircle2 size={18} />
                </div>
                <div style={{ flex:1, overflow:'hidden' }}>
                  <p style={{
                    fontWeight:700, fontSize:14, color: t.priority==='CRITICAL' ? '#dc2626' : 'var(--green-900)',
                    textDecoration: t.status==='done' ? 'line-through' : 'none',
                    whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'
                  }}>{t.title}</p>
                  <p style={{ fontSize:11, color:'#9ca3af', marginTop:4, display:'flex', alignItems:'center', gap:4 }}>
                    <Clock size={11} /> {t.time}
                    {t.priority==='CRITICAL' && <span style={{ color:'#ef4444', fontWeight:700 }}>· KRITIS</span>}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Margin Card */}
        <div className="anim-fadeInUp delay-400" style={{ background:'var(--green-600)', padding:28, borderRadius:28, color:'white', display:'flex', flexDirection:'column', justifyContent:'space-between', position:'relative', overflow:'hidden', boxShadow:'0 8px 32px rgba(22,163,74,0.3)' }}>
          <div style={{ position:'absolute', top:-40, right:-40, width:200, height:200, background:'rgba(255,255,255,0.08)', borderRadius:'50%', pointerEvents:'none' }} />
          <div style={{ position:'absolute', bottom:-30, left:-30, width:150, height:150, background:'rgba(255,255,255,0.05)', borderRadius:'50%', pointerEvents:'none' }} />
          <div style={{ position:'relative', zIndex:1 }}>
            <p style={{ fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.7)', letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:12 }}>Potensi Margin</p>
            <h4 style={{ fontSize:'clamp(20px, 2.5vw, 28px)', fontWeight:800, letterSpacing:'-0.5px', marginBottom:16 }}>
              Rp {(activeLand.budget * 1.8).toLocaleString('id-ID')}
            </h4>
            <span style={{ display:'inline-flex', alignItems:'center', gap:6, background:'rgba(255,255,255,0.15)', color:'white', padding:'6px 12px', borderRadius:10, fontSize:11, fontWeight:700, border:'1px solid rgba(255,255,255,0.2)' }}>
              <ArrowUpRight size={12} /> Bebas Tengkulak
            </span>
          </div>
          <button
            onClick={() => setView('market')}
            className="btn-outline"
            style={{ position:'relative', zIndex:1, marginTop:24, padding:'12px', borderRadius:14, fontWeight:700, fontSize:13, display:'flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:'inherit' }}
          >
            Akses Pasar Premium <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;