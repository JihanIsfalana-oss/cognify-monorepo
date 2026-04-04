import React from 'react';
import { Leaf, X } from 'lucide-react';

const NotificationCenter = ({ notifications, setNotifications }) => {
  return (
    <div style={{ position:'fixed', top:20, right:20, zIndex:500, display:'flex', flexDirection:'column', gap:10, pointerEvents:'none' }}>
      {notifications.slice(0, 3).map((n, i) => (
        <div key={n.id} className="notif-enter" style={{
          background: 'white',
          border: '1.5px solid var(--green-200)',
          borderLeft: '4px solid var(--green-500)',
          padding: '12px 16px',
          borderRadius: 14,
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
          display: 'flex', alignItems: 'center', gap: 10,
          pointerEvents: 'auto',
          maxWidth: 340,
          animationDelay: `${i * 0.05}s`
        }}>
          <Leaf size={16} style={{ color: 'var(--green-500)', flexShrink: 0 }} />
          <p style={{ fontSize: 13, fontWeight: 600, color: '#1f2937', flex: 1, margin: 0 }}>{n.text}</p>
          <button
            onClick={() => setNotifications(prev => prev.filter(x => x.id !== n.id))}
            style={{ background:'none', border:'none', cursor:'pointer', color:'#9ca3af', padding:2, flexShrink:0 }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationCenter;