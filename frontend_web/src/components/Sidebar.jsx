import React from 'react';
import { Leaf, LayoutDashboard, Stethoscope, Radar, TrendingUp, ShoppingBag, Plus, LogOut } from 'lucide-react';

const Sidebar = ({ role, setRole, view, setView }) => {
  return (
    <div style={{
      width:80, minHeight:'100%',
      display:'flex', flexDirection:'column',
      alignItems:'center', padding:'20px 0 24px',
      justifyContent:'space-between', flexShrink:0
    }} className="anim-slideLeft">
      {/* Logo */}
      <div style={{ width:48, height:48, background:'white', borderRadius:14, display:'flex', alignItems:'center', justifyContent:'center', boxShadow:'0 4px 16px rgba(22,163,74,0.2)', marginBottom:8, cursor:'default' }}>
        <Leaf size={22} style={{ color:'var(--green-600)' }} />
      </div>

      {/* Nav Items */}
      <nav style={{ display:'flex', flexDirection:'column', gap:8, alignItems:'center', flex:1, marginTop:16 }}>
        {role === 'farmer' ? (<>
          {[
            { v:'dashboard', Icon: LayoutDashboard, label:'Dashboard' },
            { v:'doctor',    Icon: Stethoscope,     label:'AI Doctor' },
            { v:'radar',     Icon: Radar,           label:'Spatial Radar' },
            { v:'market',    Icon: TrendingUp,      label:'Pasar Premium' },
          ].map(({ v, Icon, label }) => (
            <button key={v} onClick={() => setView(v)} className={`sidebar-btn ${view === v ? 'active' : ''}`}>
              <Icon size={20} />
              <span className="sidebar-tooltip">{label}</span>
            </button>
          ))}

          <div style={{ width:32, height:1.5, background:'rgba(22,163,74,0.15)', margin:'8px 0', borderRadius:4 }} />

          <button onClick={() => setView('input')} className={`sidebar-btn ${view === 'input' ? 'active' : ''}`} style={{
            border: view === 'input' ? 'none' : '1.5px dashed var(--green-300)',
            background: view === 'input' ? 'var(--green-600)' : 'transparent',
            color: view === 'input' ? 'white' : 'var(--green-500)'
          }}>
            <Plus size={20} />
            <span className="sidebar-tooltip">Tambah Lahan</span>
          </button>
        </>) : (
          <button onClick={() => setView('buyer_market')} className={`sidebar-btn ${view === 'buyer_market' ? 'active' : ''}`}>
            <ShoppingBag size={20} />
            <span className="sidebar-tooltip">Matchmaking</span>
          </button>
        )}
      </nav>

      <button
        onClick={() => { setRole(null); setView('landing'); }}
        className="sidebar-btn"
        style={{ color:'#ef4444' }}
      >
        <LogOut size={20} />
        <span className="sidebar-tooltip" style={{ background:'#7f1d1d', color:'#fca5a5' }}>Keluar</span>
      </button>
    </div>
  );
};

export default Sidebar;