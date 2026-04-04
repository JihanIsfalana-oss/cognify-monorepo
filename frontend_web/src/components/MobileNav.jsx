import React from 'react';
import { LayoutDashboard, Cpu, Plus, Radar, TrendingUp, ShoppingBag, LogOut } from 'lucide-react';

const MobileNav = ({ role, setRole, view, setView }) => {
    if (!role) return null; // Jika belum login, jangan tampilkan

    return (
    <div style={{
      position:'fixed', bottom:16, left:'50%', transform:'translateX(-50%)',
      width:'calc(100% - 32px)', maxWidth:360,
      background:'rgba(255,255,255,0.92)', backdropFilter:'blur(20px)',
      border:'1.5px solid var(--green-100)',
      padding:'10px 14px', borderRadius:60,
      display:'flex', justifyContent:'space-between', alignItems:'center',
      zIndex:200, boxShadow:'0 8px 32px rgba(0,0,0,0.1)'
    }}>
      {role === 'farmer' ? (<>
        {[
          { v:'dashboard', Icon: LayoutDashboard },
          { v:'doctor', Icon: Cpu },
        ].map(({ v, Icon }) => (
          <button key={v} onClick={() => setView(v)} style={{
            padding:'10px', borderRadius:'50%', border:'none', cursor:'pointer',
            background: view===v ? 'var(--green-950)' : 'transparent',
            color: view===v ? 'white' : 'var(--green-400)',
            transition:'all 0.2s ease', fontFamily:'inherit'
          }}><Icon size={20} /></button>
        ))}

        <button onClick={() => setView('input')} style={{
          padding:'13px', borderRadius:'50%', border:'none', cursor:'pointer',
          background: view==='input' ? 'var(--green-500)' : 'var(--green-600)',
          color:'white', transition:'all 0.2s ease',
          boxShadow:'0 4px 14px rgba(22,163,74,0.4)', fontFamily:'inherit'
        }}><Plus size={22} strokeWidth={3} /></button>

        {[
          { v:'radar', Icon: Radar },
          { v:'market', Icon: TrendingUp },
        ].map(({ v, Icon }) => (
          <button key={v} onClick={() => setView(v)} style={{
            padding:'10px', borderRadius:'50%', border:'none', cursor:'pointer',
            background: view===v ? 'var(--green-950)' : 'transparent',
            color: view===v ? 'white' : 'var(--green-400)',
            transition:'all 0.2s ease', fontFamily:'inherit'
          }}><Icon size={20} /></button>
        ))}
      </>) : (<>
        <button onClick={() => setView('buyer_market')} style={{ padding:'10px 24px', borderRadius:50, border:'none', cursor:'pointer', background: view==='buyer_market' ? 'var(--green-600)' : 'transparent', color: view==='buyer_market' ? 'white' : 'var(--green-500)', fontFamily:'inherit', fontWeight:600, fontSize:13 }}>
          <ShoppingBag size={20} />
        </button>
        <button onClick={() => { setRole(null); setView('landing'); }} style={{ padding:'10px 24px', borderRadius:50, border:'none', cursor:'pointer', background:'transparent', color:'#ef4444', fontFamily:'inherit' }}>
          <LogOut size={20} />
        </button>
      </>)}
    </div>
  );
};

export default MobileNav;