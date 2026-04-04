import React from 'react';
import { Search, MapPin, Waves, ShieldCheck, ArrowRight } from 'lucide-react';

const BuyerMarket = ({ lands, searchTerm, setSearchTerm, handlePreOrder }) => {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:24 }}>
      <header className="anim-fadeInUp" style={{ display:'flex', justifyContent:'space-between', alignItems:'center', background:'var(--green-50)', padding:'28px 32px', borderRadius:28, border:'1.5px solid var(--green-100)', flexWrap:'wrap', gap:16 }}>
        <div>
          <h2 style={{ fontSize:'clamp(20px, 3vw, 30px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-0.5px', marginBottom:8 }}>Matchmaking</h2>
          <p style={{ color:'#6b7280', fontWeight:500, fontSize:14, lineHeight:1.6 }}>
            Pencarian komoditas cerdas berdasarkan <strong style={{ color:'var(--green-800)' }}>Skor Integritas AI</strong>.
          </p>
        </div>
        <div style={{ position:'relative', width:280 }}>
          <Search size={16} style={{ position:'absolute', left:14, top:'50%', transform:'translateY(-50%)', color:'var(--green-400)' }} />
          <input
            type="text"
            placeholder="Cari padi, jagung, cabai..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{
              width:'100%', padding:'12px 16px 12px 40px',
              border:'1.5px solid var(--green-200)', borderRadius:14,
              fontSize:13, fontWeight:500, color:'var(--green-900)',
              background:'white', fontFamily:'inherit',
              boxShadow:'0 2px 8px rgba(0,0,0,0.04)'
            }}
          />
        </div>
      </header>

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(300px, 1fr))', gap:20 }}>
        {lands
          .filter(l => l.crop.toLowerCase().includes(searchTerm.toLowerCase()) || l.location.toLowerCase().includes(searchTerm.toLowerCase()))
          .map((land, i) => (
            <div key={land.id} className={`card-hover anim-fadeInUp delay-${(i+1)*100}`} style={{
              background:'white', padding:28, borderRadius:28,
              border:'1.5px solid var(--green-100)',
              boxShadow:'0 2px 12px rgba(0,0,0,0.04)',
              display:'flex', flexDirection:'column', gap:16
            }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                <span className="tag-green" style={{ padding:'6px 14px', borderRadius:50, fontSize:11, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em' }}>
                  {land.crop}
                </span>
                <div style={{ background:'var(--green-950)', color:'white', padding:'8px 12px', borderRadius:12, textAlign:'center' }}>
                  <p style={{ fontSize:9, fontWeight:700, color:'var(--green-400)', letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:2 }}>AI Score</p>
                  <p style={{ fontSize:20, fontWeight:900, lineHeight:1 }}>{land.reputationScore}</p>
                </div>
              </div>
              <div>
                <h4 style={{ fontSize:20, fontWeight:800, color:'var(--green-950)', letterSpacing:'-0.5px', marginBottom:6 }}>{land.name}</h4>
                <p style={{ fontSize:12, color:'#9ca3af', display:'flex', alignItems:'center', gap:5 }}>
                  <MapPin size={13} style={{ color:'var(--green-400)' }} /> {land.location}
                </p>
              </div>
              <div style={{ background:'var(--green-50)', padding:'14px 16px', borderRadius:14, border:'1px solid var(--green-100)' }}>
                <p style={{ fontSize:10, fontWeight:700, color:'var(--green-500)', textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>Kondisi Lahan Terverifikasi</p>
                <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
                  {[
                    { icon: <Waves size={12} style={{ color:'#3b82f6' }}/>, text:'Air Optimal' },
                    { icon: <ShieldCheck size={12} style={{ color:'var(--green-500)' }}/>, text:'Bebas Hama' },
                  ].map(({ icon, text }) => (
                    <div key={text} style={{ display:'flex', alignItems:'center', gap:6, background:'white', padding:'5px 10px', borderRadius:8, border:'1px solid var(--green-200)', fontSize:11, fontWeight:700, color:'var(--green-700)' }}>
                      {icon} {text}
                    </div>
                  ))}
                </div>
              </div>
              <button
                onClick={() => handlePreOrder(land)}
                className="btn-primary"
                style={{ padding:'14px', borderRadius:14, fontWeight:700, fontSize:13, display:'flex', alignItems:'center', justifyContent:'center', gap:8, fontFamily:'inherit' }}
              >
                Ajukan Pre-Order <ArrowRight size={14} />
              </button>
            </div>
        ))}
        {lands.filter(l => l.crop.toLowerCase().includes(searchTerm.toLowerCase()) || l.location.toLowerCase().includes(searchTerm.toLowerCase())).length === 0 && (
          <div style={{ gridColumn:'1/-1', textAlign:'center', padding:'48px 20px', color:'#9ca3af', fontSize:14, background:'var(--green-50)', borderRadius:20 }}>
            Tidak ada hasil untuk "{searchTerm}"
          </div>
        )}
      </div>
    </div>
  );
};

export default BuyerMarket;