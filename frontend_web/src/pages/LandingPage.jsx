// src/pages/LandingPage.jsx
import React from 'react';
import { Leaf, Target, ShoppingBag } from 'lucide-react';

 const LandingPage = ({ handleRoleSelection }) => (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #dcfce7 100%)',
      display: 'flex', flexDirection: 'column',
      padding: '32px 48px',
      position: 'relative', overflow: 'hidden',
      fontFamily: "'DM Sans', sans-serif"
    }}>
      {/* Decorative blobs */}
      <div style={{ position:'absolute', top:-100, right:-100, width:500, height:500, background:'radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%)', borderRadius:'50%', pointerEvents:'none' }} />
      <div style={{ position:'absolute', bottom:-80, left:-80, width:400, height:400, background:'radial-gradient(circle, rgba(22,163,74,0.08) 0%, transparent 70%)', borderRadius:'50%', pointerEvents:'none' }} />
      <div style={{ position:'absolute', top:'40%', left:'30%', width:300, height:300, background:'radial-gradient(circle, rgba(134,239,172,0.1) 0%, transparent 70%)', borderRadius:'50%', pointerEvents:'none' }} />

      {/* Nav */}
      <nav className="anim-slideTop" style={{ display:'flex', justifyContent:'space-between', alignItems:'center', position:'relative', zIndex:10 }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{ width:36, height:36, background:'var(--green-600)', borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <Leaf size={18} color="white" />
          </div>
          <span className="font-display" style={{ fontWeight:800, fontSize:18, color:'var(--green-800)', letterSpacing:'-0.5px' }}>cognify</span>
        </div>
        <span style={{ fontSize:12, fontWeight:600, color:'var(--green-600)', letterSpacing:'0.1em', textTransform:'uppercase' }}>Pioneer in Agritech</span>
      </nav>

      {/* Hero */}
      <div style={{ flex:1, display:'flex', flexDirection:'column', justifyContent:'center', maxWidth:1100, margin:'0 auto', width:'100%', paddingTop:60, paddingBottom:40, position:'relative', zIndex:10 }}>
        <div className="anim-fadeInUp delay-100">
          <span style={{ display:'inline-block', background:'var(--green-100)', color:'var(--green-700)', fontSize:11, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase', padding:'6px 14px', borderRadius:50, border:'1px solid var(--green-200)', marginBottom:24 }}>
            Hybrid Edge-Cloud Platform
          </span>
        </div>

        <h1 className="font-display anim-fadeInUp delay-200" style={{
          fontSize: 'clamp(60px, 10vw, 110px)',
          fontWeight: 900,
          lineHeight: 0.9,
          letterSpacing: '-3px',
          color: 'var(--green-950)',
          marginBottom: 28
        }}>
          cognify<span style={{ color:'var(--green-500)' }}>.</span>
        </h1>

        <p className="anim-fadeInUp delay-300" style={{ fontSize:'clamp(16px, 2vw, 22px)', color:'#4b5563', fontWeight:400, maxWidth:520, lineHeight:1.6, marginBottom:56 }}>
          Precision Agriculture powered by local intelligence.<br/>
          <span style={{ color:'var(--green-700)', fontWeight:600 }}>Empowering Indonesian farmers</span> through AI.
        </p>

        {/* Role Cards */}
        <div className="anim-fadeInUp delay-400" style={{ display:'flex', gap:20, flexWrap:'wrap' }}>
          <button
            onClick={() => handleRoleSelection('farmer')}
            className="card-hover"
            style={{
              display:'flex', flexDirection:'column', justifyContent:'space-between',
              padding:'36px', width:280, height:220,
              background:'white', borderRadius:28,
              border:'1.5px solid var(--green-100)',
              boxShadow:'0 4px 24px rgba(0,0,0,0.06)',
              textAlign:'left', cursor:'pointer',
              transition:'all 0.25s ease'
            }}
          >
            <div style={{ width:52, height:52, background:'var(--green-600)', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <Target size={22} color="white" />
            </div>
            <div>
              <h3 style={{ fontSize:24, fontWeight:800, color:'var(--green-950)', letterSpacing:'-0.5px', marginBottom:8 }}>Petani.</h3>
              <p style={{ fontSize:13, color:'#6b7280', lineHeight:1.5 }}>Akses sensor Edge, Irigasi FAO-56, dan mitigasi hama real-time.</p>
            </div>
          </button>

          <button
            onClick={() => handleRoleSelection('buyer')}
            className="card-hover"
            style={{
              display:'flex', flexDirection:'column', justifyContent:'space-between',
              padding:'36px', width:280, height:220,
              background:'var(--green-950)', borderRadius:28,
              border:'1.5px solid var(--green-800)',
              boxShadow:'0 4px 24px rgba(5,46,22,0.25)',
              textAlign:'left', cursor:'pointer',
              transition:'all 0.25s ease'
            }}
          >
            <div style={{ width:52, height:52, background:'var(--green-500)', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
              <ShoppingBag size={22} color="white" />
            </div>
            <div>
              <h3 style={{ fontSize:24, fontWeight:800, color:'white', letterSpacing:'-0.5px', marginBottom:8 }}>Pembeli.</h3>
              <p style={{ fontSize:13, color:'var(--green-300)', lineHeight:1.5 }}>Akses pasar komoditas premium dengan verifikasi skor AI.</p>
            </div>
          </button>
        </div>

        {/* Stats */}
        <div className="anim-fadeInUp delay-600" style={{ display:'flex', gap:40, marginTop:56, flexWrap:'wrap' }}>
          {[['2,400+', 'Petani Aktif'], ['98.7%', 'Akurasi AI'], ['< 50ms', 'Latensi Edge']].map(([val, label]) => (
            <div key={label}>
              <div className="font-display" style={{ fontSize:28, fontWeight:800, color:'var(--green-700)', letterSpacing:'-1px' }}>{val}</div>
              <div style={{ fontSize:12, color:'#9ca3af', fontWeight:500, marginTop:2 }}>{label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

export default LandingPage;