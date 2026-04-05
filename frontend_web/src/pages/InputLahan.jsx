import React from 'react';
import { MessageSquare, ArrowRight, Cpu, Database } from 'lucide-react';

const InputLahan = ({ inputPlanText, setInputPlanText, addNewLand, isProcessing}) => {
    const hasInput = inputPlanText.length > 5;

    return (
      <div style={{ maxWidth:900, margin:'0 auto' }}>
        <header className="anim-fadeInUp" style={{ marginBottom:28 }}>
          <h2 style={{ fontSize:'clamp(22px, 4vw, 32px)', fontWeight:800, color:'var(--green-950)', letterSpacing:'-1px', marginBottom:6 }}>
            Registrasi Inklusif
          </h2>
          <p style={{ color:'#6b7280', fontWeight:500, fontSize:13, lineHeight:1.6 }}>
            Input deskripsi bebas. <strong style={{ color:'var(--green-800)' }}>Transformer NER</strong> mengekstrak data Anda secara real-time.
          </p>
        </header>

        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
          {/* Input */}
          <div style={{ background:'white', borderRadius:20, padding:24, border:'1.5px solid var(--green-100)', boxShadow:'0 2px 8px rgba(0,0,0,0.04)', display:'flex', flexDirection:'column', minHeight:380 }}>
            <div style={{ display:'flex', gap:10, alignItems:'flex-start', background:'var(--green-50)', padding:'12px 14px', borderRadius:12, border:'1px solid var(--green-100)', marginBottom:16 }}>
              <MessageSquare size={16} style={{ color:'var(--green-500)', flexShrink:0, marginTop:2 }} />
              <p style={{ fontSize:12, color:'var(--green-700)', fontWeight:500, lineHeight:1.6, margin:0 }}>Ceritakan kondisi lahan Anda secara natural. AI akan menerjemahkannya menjadi format terstruktur.</p>
            </div>
            <textarea
              value={inputPlanText}
              onChange={e => setInputPlanText(e.target.value)}
              placeholder="Contoh: Saya menanam padi di daerah Malang seluas 2 hektar..."
              style={{
                flex:1, minHeight:140,
                padding:'4px 0',
                border:'none', outline:'none', resize:'none',
                fontSize:15, fontWeight:500, color:'var(--green-900)',
                lineHeight:1.7,
                fontFamily:"'Inter', -apple-system, sans-serif",
                background:'transparent',
                caretColor:'var(--green-600)',
                display:'block', width:'100%'
              }}
            />
            <button
              onClick={addNewLand}
              disabled={!hasInput || isProcessing}
              style={{
                width:'100%', padding:'13px', borderRadius:12,
                fontWeight:700, fontSize:13, marginTop:16,
                display:'flex', alignItems:'center', justifyContent:'center', gap:8,
                fontFamily:"'Inter', -apple-system, sans-serif",
                background: !hasInput || isProcessing ? '#e5e7eb' : 'var(--green-600)',
                color: !hasInput || isProcessing ? '#9ca3af' : 'white',
                border: 'none',
                cursor: !hasInput || isProcessing ? 'not-allowed' : 'pointer',
                transition:'all 0.2s ease'
              }}
            >
              {isProcessing ? (
                <><div style={{ width:13, height:13, borderRadius:'50%', border:'2px solid white', borderTopColor:'transparent', animation:'radar-sweep 0.6s linear infinite' }} /> Mengekstrak...</>
              ) : (
                <>Daftarkan Sistem <ArrowRight size={14} /></>
              )}
            </button>
          </div>

          {/* Entity Output */}
          <div style={{ background:'var(--green-950)', borderRadius:20, padding:24, color:'white', position:'relative', overflow:'hidden', display:'flex', flexDirection:'column', minHeight:380 }}>
            <div style={{ position:'absolute', top:-50, right:-50, width:180, height:180, background:'radial-gradient(circle, rgba(34,197,94,0.12) 0%, transparent 70%)', borderRadius:'50%', pointerEvents:'none' }} />

            <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:20, borderBottom:'1px solid rgba(255,255,255,0.06)', paddingBottom:16, position:'relative', zIndex:1 }}>
              <div style={{ width:36, height:36, background:'rgba(255,255,255,0.06)', borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center', border:'1px solid rgba(255,255,255,0.08)', flexShrink:0 }}>
                <Cpu size={15} style={{ color:'var(--green-400)' }} />
              </div>
              <div>
                <h3 style={{ fontWeight:700, fontSize:14, margin:0 }}>Entity Output</h3>
                <p style={{ fontSize:9, color:'var(--green-400)', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.12em', marginTop:2, marginBottom:0 }}>NLP Extraction Active</p>
              </div>
            </div>

            {hasInput ? (
              <div style={{ display:'flex', flexDirection:'column', gap:10, flex:1, position:'relative', zIndex:1 }}>
            
              </div>
            ) : (
              <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', opacity:0.25, position:'relative', zIndex:1 }}>
                <Database size={40} style={{ color:'var(--green-400)', marginBottom:10 }} />
                <p style={{ fontWeight:700, fontSize:14, color:'var(--green-300)', margin:0 }}>Menunggu Teks</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

export default InputLahan;