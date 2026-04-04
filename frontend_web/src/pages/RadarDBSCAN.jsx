import React from 'react';
import { Radar } from 'lucide-react';

const RadarDBSCAN = ({ isRadarInitialized, setView }) => {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      <header className="anim-fadeInUp" style={{ display:'flex', justifyContent:'space-between', alignItems:'center', background:'var(--green-50)', padding:'24px 28px', borderRadius:24, border:'1.5px solid var(--green-100)', flexWrap:'wrap', gap:12 }}>
        <div>
          <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}>
            <Radar size={24} style={{ color:'var(--green-600)' }} />
            <h2 style={{ fontSize:'clamp(20px, 3vw, 28px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-0.5px' }}>Geospatial Radar</h2>
          </div>
          <p style={{ fontSize:13, color:'#6b7280', fontWeight:500 }}>
            Mitigasi kolektif berbasis <strong style={{ color:'var(--green-800)' }}>DBSCAN Clustering</strong> radius 5 KM.
          </p>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:12 }}>
          {isRadarInitialized && (
            <div className="anim-fadeIn" style={{ background:'#fff5f5', padding:'10px 16px', borderRadius:12, display:'flex', alignItems:'center', gap:10, border:'1px solid #fecaca' }}>
              <span className="font-display" style={{ fontSize:24, fontWeight:900, color:'#dc2626' }}>2</span>
              <span style={{ fontSize:10, fontWeight:700, color:'#991b1b', textTransform:'uppercase', letterSpacing:'0.1em', lineHeight:1.3 }}>Titik<br/>Kritis</span>
            </div>
          )}
          <button onClick={() => setView('dashboard')} className="btn-outline" style={{ padding:'10px 18px', borderRadius:12, fontWeight:700, fontSize:12, fontFamily:'inherit' }}>
            Tutup Radar
          </button>
        </div>
      </header>

      <div className="anim-fadeInUp delay-100" style={{ background:'var(--green-950)', height:520, borderRadius:32, position:'relative', overflow:'hidden', boxShadow:'0 12px 48px rgba(5,46,22,0.4)' }}>
        {/* Radar rings */}
        {[560, 420, 280, 140].map((size, idx) => (
          <div key={size} style={{
            position:'absolute', top:'50%', left:'50%',
            width:size, height:size,
            transform:'translate(-50%, -50%)',
            border:'1px solid rgba(34,197,94,0.12)',
            borderRadius:'50%',
            pointerEvents:'none'
          }}>
            {idx === 0 && (
              <span style={{
                position:'absolute', top:8, left:'50%', transform:'translateX(-50%)',
                color:'rgba(34,197,94,0.4)', fontSize:10, fontWeight:700, letterSpacing:'0.1em',
                textTransform:'uppercase', background:'var(--green-950)', padding:'2px 10px', borderRadius:20
              }}>Radius 5 KM</span>
            )}
          </div>
        ))}

        {/* Cross lines */}
        <div style={{ position:'absolute', top:'50%', left:0, right:0, height:1, background:'rgba(34,197,94,0.07)', pointerEvents:'none' }} />
        <div style={{ position:'absolute', top:0, bottom:0, left:'50%', width:1, background:'rgba(34,197,94,0.07)', pointerEvents:'none' }} />

        {/* Sweep */}
        <div style={{
          position:'absolute', bottom:'50%', left:'50%',
          width:1, height:260,
          transformOrigin:'bottom center',
          background:'linear-gradient(to top, rgba(34,197,94,0.5), transparent)',
          animation:'radar-sweep 6s linear infinite'
        }} />

        {/* Center dot */}
        <div style={{
          position:'absolute', top:'50%', left:'50%',
          transform:'translate(-50%, -50%)',
          width:16, height:16, background:'var(--green-400)', borderRadius:'50%',
          border:'3px solid white', zIndex:10,
          boxShadow:'0 0 0 4px rgba(34,197,94,0.3)'
        }} className="pulse-ring" />

        {/* Cluster Nodes */}
        {isRadarInitialized && (<>
          {/* Cluster 1 */}
          <div style={{ position:'absolute', top:'28%', left:'35%', zIndex:20 }} className="anim-fadeIn">
            <div style={{ position:'relative' }}>
              <div style={{
                width:20, height:20, background:'#ef4444', borderRadius:'50%',
                border:'2.5px solid white', cursor:'pointer',
                boxShadow:'0 0 16px rgba(239,68,68,0.6)'
              }}
              onMouseEnter={e => e.currentTarget.nextSibling.style.display='block'}
              onMouseLeave={e => e.currentTarget.nextSibling.style.display='none'}
              />
              <div style={{
                display:'none', position:'absolute', top:26, left:0,
                background:'white', padding:'12px 16px', borderRadius:14,
                boxShadow:'0 8px 32px rgba(0,0,0,0.15)', zIndex:50,
                width:220, border:'1px solid var(--green-100)'
              }}>
                <p style={{ fontSize:10, fontWeight:700, color:'#dc2626', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:4 }}>DBSCAN Cluster_01</p>
                <p style={{ fontSize:12, color:'var(--green-900)', fontWeight:500, lineHeight:1.5 }}>Wabah WBC terdeteksi massif. Jarak: 1.2 KM. Risiko: Tinggi.</p>
              </div>
            </div>
          </div>

          {/* Cluster 2 */}
          <div style={{ position:'absolute', top:'62%', right:'28%', zIndex:20 }} className="anim-fadeIn delay-200">
            <div style={{ position:'relative' }}>
              <div style={{
                width:14, height:14, background:'#f97316', borderRadius:'50%',
                border:'2px solid white', cursor:'pointer',
                boxShadow:'0 0 12px rgba(249,115,22,0.5)'
              }}
              onMouseEnter={e => e.currentTarget.nextSibling.style.display='block'}
              onMouseLeave={e => e.currentTarget.nextSibling.style.display='none'}
              />
              <div style={{
                display:'none', position:'absolute', bottom:20, right:0,
                background:'white', padding:'12px 16px', borderRadius:14,
                boxShadow:'0 8px 32px rgba(0,0,0,0.15)', zIndex:50,
                width:220, border:'1px solid var(--green-100)'
              }}>
                <p style={{ fontSize:10, fontWeight:700, color:'#c2410c', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:4 }}>DBSCAN Cluster_02</p>
                <p style={{ fontSize:12, color:'var(--green-900)', fontWeight:500, lineHeight:1.5 }}>Gejala Antraknosa. Jarak: 3.5 KM. Risiko: Menengah.</p>
              </div>
            </div>
          </div>
        </>)}

        {/* Legend */}
        <div style={{ position:'absolute', bottom:20, left:20, display:'flex', gap:12, flexWrap:'wrap' }}>
          {[
            { color:'var(--green-400)', label:'Node Anda' },
            { color:'#ef4444', label:'Risiko Tinggi' },
            { color:'#f97316', label:'Risiko Menengah' },
          ].map(({ color, label }) => (
            <div key={label} style={{ display:'flex', alignItems:'center', gap:6, background:'rgba(0,0,0,0.4)', padding:'6px 12px', borderRadius:20, backdropFilter:'blur(8px)' }}>
              <div style={{ width:8, height:8, borderRadius:'50%', background:color }} />
              <span style={{ fontSize:10, fontWeight:600, color:'rgba(255,255,255,0.7)' }}>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RadarDBSCAN;