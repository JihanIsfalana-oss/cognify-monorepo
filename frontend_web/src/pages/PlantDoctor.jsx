import React from 'react';
import { Camera, Zap, Cpu, Crosshair, Database, ShieldCheck, Plus, Radar } from 'lucide-react';

const PlantDoctor = ({ scanState, setScanState, scanResult, setScanResult, startPlantScan, injectDoctorTask, reportToRadar }) => {
  return (
    <div style={{ maxWidth:900, margin:'0 auto' }}>
      <header className="anim-fadeInUp" style={{ marginBottom:36 }}>
        <h2 style={{ fontSize:'clamp(22px, 4vw, 34px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-1px', marginBottom:8 }}>
          Edge AI Doctor
        </h2>
        <p style={{ color:'#6b7280', fontWeight:500, fontSize:14, lineHeight:1.6 }}>
          Diagnosa instan secara offline didukung oleh komputasi <strong style={{ color:'var(--green-800)' }}>Intel® OpenVINO™</strong>.
        </p>
      </header>

      <div className="anim-fadeInUp delay-100" style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:20, background:'var(--green-50)', borderRadius:32, border:'1.5px solid var(--green-100)', overflow:'hidden', minHeight:480 }}>
        {/* Left: Camera */}
        <div style={{ padding:'32px', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', borderRight:'1.5px solid var(--green-100)' }}>
          {scanState === 'idle' && (
            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20 }}>
              <button
                onClick={startPlantScan}
                style={{
                  width:200, height:200, background:'white', border:'2px dashed var(--green-300)',
                  borderRadius:28, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
                  gap:12, cursor:'pointer', transition:'all 0.2s ease', fontFamily:'inherit'
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor='var(--green-500)'; e.currentTarget.style.background='var(--green-50)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor='var(--green-300)'; e.currentTarget.style.background='white'; }}
              >
                <Camera size={52} style={{ color:'var(--green-300)' }} />
                <p style={{ fontSize:12, color:'var(--green-400)', fontWeight:600 }}>Ambil gambar sampel</p>
              </button>
              <button onClick={startPlantScan} className="btn-primary" style={{ padding:'14px 32px', borderRadius:14, fontWeight:700, fontSize:13, display:'flex', alignItems:'center', gap:8, fontFamily:'inherit' }}>
                <Zap size={15} /> Run Inference
              </button>
            </div>
          )}

          {scanState === 'scanning' && (
            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:20 }} className="anim-fadeIn">
              <div style={{ position:'relative', width:80, height:80 }}>
                <div style={{
                  position:'absolute', inset:0,
                  border:'3px solid var(--green-100)',
                  borderTopColor:'var(--green-600)',
                  borderRadius:'50%',
                  animation:'radar-sweep 0.8s linear infinite'
                }} />
                <Cpu style={{ position:'absolute', inset:0, margin:'auto', color:'var(--green-600)' }} size={24} />
              </div>
              <div style={{ textAlign:'center' }}>
                <p className="font-display" style={{ fontWeight:800, fontSize:20, color:'var(--green-900)', letterSpacing:'-0.5px' }}>Quantization Mode</p>
                <p style={{ fontSize:12, color:'var(--green-500)', marginTop:4 }}>FP32 → INT8 Edge Optimization</p>
              </div>
            </div>
          )}

          {scanState === 'result' && scanResult && (
            <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }} className="anim-fadeIn">
              <div style={{
                width:200, height:200, background:'#fff5f5', border:'2px solid #fecaca',
                borderRadius:28, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
                position:'relative', overflow:'hidden'
              }}>
                <Crosshair size={100} style={{ color:'#fca5a5', position:'absolute' }} />
                <p className="font-display" style={{ fontWeight:900, fontSize:24, color:'#dc2626', position:'relative', zIndex:1 }}>WARNING</p>
                <p style={{ fontWeight:700, fontSize:13, color:'#ef4444', position:'relative', zIndex:1, textAlign:'center', padding:'0 16px' }}>{scanResult.disease}</p>
              </div>
              <button
                onClick={() => { setScanState('idle'); setScanResult(null); }}
                className="btn-outline"
                style={{ padding:'8px 20px', borderRadius:10, fontWeight:600, fontSize:12, fontFamily:'inherit' }}
              >
                Scan Ulang
              </button>
            </div>
          )}
        </div>

        {/* Right: Output */}
        <div style={{ padding:'32px', background:'white', display:'flex', flexDirection:'column', justifyContent:'center' }}>
          {scanState !== 'result' ? (
            <div style={{ textAlign:'center', opacity:0.35 }}>
              <Database size={44} style={{ color:'var(--green-300)', marginBottom:12 }} />
              <p style={{ fontWeight:800, fontSize:18, color:'var(--green-400)', letterSpacing:'-0.5px', marginBottom:4 }}>Menunggu Data</p>
              <p style={{ fontSize:13, color:'var(--green-400)' }}>Sistem siap melakukan pemrosesan lokal.</p>
            </div>
          ) : (
            <div className="anim-slideRight" style={{ display:'flex', flexDirection:'column', gap:16 }}>
              <div style={{ background:'var(--green-950)', color:'white', padding:20, borderRadius:20 }}>
                <p style={{ fontSize:10, fontWeight:700, color:'var(--green-400)', textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:16 }}>Diagnostics Report</p>
                {[
                  { label:'Akurasi AI', val: scanResult.accuracy, icon: <ShieldCheck size={16} style={{ color:'var(--green-400)' }}/> },
                  { label:'Latensi Inferensi', val: scanResult.latency, color:'var(--green-400)' },
                ].map(({ label, val, icon, color }, i) => (
                  <div key={i} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', borderTop: i>0 ? '1px solid rgba(255,255,255,0.06)' : 'none', paddingTop: i>0 ? 12 : 0, marginTop: i>0 ? 12 : 0 }}>
                    <span style={{ color:'rgba(255,255,255,0.5)', fontSize:13 }}>{label}</span>
                    <span style={{ fontWeight:900, fontSize:16, display:'flex', alignItems:'center', gap:6, color: color || 'white' }}>{icon}{val}</span>
                  </div>
                ))}
              </div>

              <div style={{ background:'var(--green-50)', padding:18, borderRadius:18, border:'1px solid var(--green-100)' }}>
                <p style={{ fontSize:10, fontWeight:700, color:'var(--green-500)', textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:8 }}>Protokol Penanganan</p>
                <p style={{ fontSize:13, color:'var(--green-900)', fontWeight:500, lineHeight:1.6 }}>{scanResult.solution}</p>
              </div>

              <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                <button onClick={injectDoctorTask} className="btn-primary" style={{ padding:'14px', borderRadius:14, fontWeight:700, fontSize:13, display:'flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:'inherit' }}>
                  <Plus size={14} /> Tambah ke Agenda
                </button>
                <button onClick={reportToRadar} style={{ padding:'14px', borderRadius:14, fontWeight:700, fontSize:13, background:'#fff5f5', color:'#dc2626', border:'1px solid #fecaca', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:'inherit', transition:'all 0.2s ease' }}>
                  <Radar size={14} /> Siarkan ke Radar DBSCAN
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlantDoctor;