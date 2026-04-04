import React from 'react';
import { TrendingUp, TrendingDown, UserCheck, MapPin, CheckCircle2 } from 'lucide-react';

const FarmerMarket = ({ regionalPrices, inboundRequests, approvePO, rejectPO }) => {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      <header className="anim-fadeInUp" style={{ background:'var(--green-50)', padding:'28px 32px', borderRadius:28, border:'1.5px solid var(--green-100)' }}>
        <h2 style={{ fontSize:'clamp(20px, 3vw, 30px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-0.5px', marginBottom:8 }}>Pasar Premium</h2>
        <p style={{ color:'#6b7280', fontWeight:500, fontSize:14, lineHeight:1.6 }}>Kelola permintaan Pre-Order dan pantau fluktuasi harga tanpa intervensi perantara.</p>
      </header>

      {/* Price Cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))', gap:16 }}>
        {regionalPrices.map((p, i) => (
          <div key={i} className={`card-hover anim-fadeInUp delay-${(i+1)*100}`} style={{ background:'white', padding:24, borderRadius:24, border:'1.5px solid var(--green-100)', boxShadow:'0 2px 12px rgba(0,0,0,0.04)', display:'flex', flexDirection:'column', gap:16 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
              <p style={{ fontWeight:800, color:'var(--green-900)', fontSize:16 }}>{p.crop}</p>
              {p.trend==='up' ? <TrendingUp size={18} style={{ color:'var(--green-500)' }}/> :
               p.trend==='down' ? <TrendingDown size={18} style={{ color:'#ef4444' }}/> :
               <div style={{ width:18, height:2, background:'var(--green-200)', borderRadius:2, marginTop:8 }}/>}
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                <span style={{ fontSize:12, color:'#9ca3af' }}>Harga Pasar</span>
                <span style={{ fontWeight:900, fontSize:18, color:'var(--green-800)', letterSpacing:'-0.5px' }}>Rp {p.marketPrice.toLocaleString('id-ID')}</span>
              </div>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', background:'var(--green-50)', padding:'10px 12px', borderRadius:12 }}>
                <span style={{ fontSize:10, fontWeight:700, color:'#9ca3af', textTransform:'uppercase', letterSpacing:'0.08em' }}>Tengkulak</span>
                <span style={{ fontWeight:700, color:'#6b7280', fontSize:14 }}>Rp {p.middlemanPrice.toLocaleString('id-ID')}</span>
              </div>
            </div>
            <p style={{ fontSize:11, color:'var(--green-600)', lineHeight:1.5 }}>{p.info}</p>
          </div>
        ))}
      </div>

      {/* Inbound PO */}
      <div className="anim-fadeInUp delay-400" style={{ background:'white', padding:28, borderRadius:28, border:'1.5px solid var(--green-100)', boxShadow:'0 2px 12px rgba(0,0,0,0.04)' }}>
        <h3 style={{ fontWeight:800, color:'var(--green-900)', fontSize:16, marginBottom:20 }}>Inbound Pre-Orders</h3>
        <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
          {inboundRequests.length === 0 ? (
            <div style={{ textAlign:'center', padding:'40px 20px', color:'#9ca3af', fontSize:13, background:'var(--green-50)', borderRadius:16 }}>
              Belum ada permintaan PO yang masuk.
            </div>
          ) : inboundRequests.map(req => (
            <div key={req.id} style={{
              display:'flex', flexWrap:'wrap', justifyContent:'space-between', alignItems:'center',
              padding:'18px 20px', background:'var(--green-50)', borderRadius:20,
              border: req.status==='approved' ? '1.5px solid var(--green-300)' : req.status==='rejected' ? '1.5px solid #fecaca' : '1.5px solid var(--green-100)',
              gap:12, transition:'all 0.2s ease'
            }}>
              <div style={{ display:'flex', alignItems:'center', gap:14 }}>
                <div style={{ width:44, height:44, background: req.status==='approved' ? 'var(--green-100)' : 'white', borderRadius:12, display:'flex', alignItems:'center', justifyContent:'center', border:'1px solid var(--green-200)', flexShrink:0 }}>
                  <UserCheck size={18} style={{ color:'var(--green-600)' }} />
                </div>
                <div>
                  <h4 style={{ fontWeight:800, fontSize:15, color:'var(--green-900)' }}>{req.buyerName}</h4>
                  <p style={{ fontSize:11, color:'#9ca3af', marginTop:3, display:'flex', alignItems:'center', gap:6 }}>
                    <MapPin size={12} style={{ color:'var(--green-400)' }} />
                    {req.location} ({req.distance} km) · Trust: {req.reqScore}
                  </p>
                </div>
              </div>

              <div style={{ display:'flex', alignItems:'center', gap:16, flexWrap:'wrap' }}>
                <div>
                  <p style={{ fontSize:10, fontWeight:700, color:'#9ca3af', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:4 }}>{req.crop} · {req.quantity}</p>
                  <p style={{ fontWeight:900, fontSize:20, color:'var(--green-600)', letterSpacing:'-0.5px' }}>
                    Rp {req.price.toLocaleString('id-ID')}<span style={{ fontSize:11, color:'#9ca3af', fontWeight:500 }}>/kg</span>
                  </p>
                </div>

                {req.status === 'pending' ? (
                  <div style={{ display:'flex', gap:8 }}>
                    <button onClick={() => approvePO(req.id)} className="btn-primary" style={{ padding:'10px 20px', borderRadius:12, fontWeight:700, fontSize:12, fontFamily:'inherit' }}>
                      Setujui PO
                    </button>
                    <button onClick={() => rejectPO(req.id)} style={{ padding:'10px 14px', borderRadius:12, fontWeight:700, fontSize:12, background:'#fee2e2', color:'#dc2626', border:'none', cursor:'pointer', fontFamily:'inherit' }}>
                      Tolak
                    </button>
                  </div>
                ) : req.status === 'approved' ? (
                  <div style={{ background:'var(--green-100)', color:'var(--green-700)', padding:'10px 16px', borderRadius:12, fontWeight:700, fontSize:12, display:'flex', alignItems:'center', gap:6 }}>
                    <CheckCircle2 size={14} /> Disetujui
                  </div>
                ) : (
                  <div style={{ background:'#fee2e2', color:'#dc2626', padding:'10px 16px', borderRadius:12, fontWeight:700, fontSize:12 }}>
                    Ditolak
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FarmerMarket;