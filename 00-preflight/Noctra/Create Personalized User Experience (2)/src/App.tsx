import { useState, useEffect, useRef, useCallback } from 'react'

/* ═══════════════════════════════════════════════════════════════════
   NOCTRA — Cinematic Investigation Landing
═══════════════════════════════════════════════════════════════════ */

const GOLD    = '#c9a84c'
const CRIMSON = '#7a1a1a'

/* ─── RAIN ─────────────────────────────────────────────────────────── */
const RAIN_DROPS = Array.from({ length: 120 }, (_, i) => ({
  id: i,
  left: `${(i * 7.3 + Math.sin(i) * 40) % 100}%`,
  height: `${14 + (i % 8) * 3}px`,
  duration: `${0.55 + (i % 9) * 0.08}s`,
  delay: `${(i * 0.13) % 2}s`,
  opacity: 0.12 + (i % 5) * 0.055,
}))

function Rain() {
  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 5 }}>
      {RAIN_DROPS.map(d => (
        <div key={d.id} className="rain-drop" style={{ left: d.left, height: d.height, opacity: d.opacity, animationDuration: d.duration, animationDelay: d.delay }} />
      ))}
    </div>
  )
}

/* ─── DUST MOTES ────────────────────────────────────────────────────── */
const MOTES = Array.from({ length: 28 }, (_, i) => ({
  id: i,
  left: `${28 + (i * 11.7 + Math.cos(i) * 20) % 45}%`,
  bottom: `${20 + (i * 8.3) % 50}%`,
  size: `${1.5 + (i % 4) * 0.8}px`,
  duration: `${6 + (i % 7) * 2}s`,
  delay: `${(i * 0.7) % 5}s`,
}))

function Dust() {
  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 6 }}>
      {MOTES.map(m => (
        <div key={m.id} className="dust-mote" style={{ left: m.left, bottom: m.bottom, width: m.size, height: m.size, animationDuration: m.duration, animationDelay: m.delay }} />
      ))}
    </div>
  )
}

/* ─── LIGHTNING ─────────────────────────────────────────────────────── */
function Lightning({ active }: { active: boolean }) {
  if (!active) return null
  return <div className="lightning-overlay" />
}

/* ─── PERSON PORTRAIT (sepia mugshot style) ─────────────────────────── */
type PersonStyle = 'suit_m' | 'hat_m' | 'hair_f' | 'glasses_m' | 'hood_m' | 'bun_f' | 'tie_m' | 'beard_m'

function PersonPortrait({ x, y, w, h, style: pStyle, name, label }: {
  x: number; y: number; w: number; h: number
  style: PersonStyle; name: string; label?: string
}) {
  const cx = x + w / 2
  const faceY = y + h * 0.28
  const r = w * 0.22

  const skinTones: Record<PersonStyle, string> = {
    suit_m: '#9a7858', hat_m: '#8a6848', hair_f: '#b08868',
    glasses_m: '#7a5838', hood_m: '#a08060', bun_f: '#c09878',
    tie_m: '#8a6848', beard_m: '#7a5838',
  }
  const skin = skinTones[pStyle]

  return (
    <g>
      {/* Photo border & bg */}
      <rect x={x} y={y} width={w} height={h} fill="#c8b898" stroke="#a89878" strokeWidth="1.5" rx="1"/>
      {/* Sepia photo background */}
      <rect x={x+2} y={y+2} width={w-4} height={h-4} fill="#b8a880"/>
      {/* Photo caption strip at bottom */}
      <rect x={x} y={y+h-14} width={w} height={14} fill="#a89870"/>
      <text x={cx} y={y+h-4} textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1a08" letterSpacing="0.5">{name}</text>

      {/* Body / shoulders */}
      <ellipse cx={cx} cy={y+h*0.78} rx={w*0.38} ry={h*0.28} fill={pStyle==='suit_m'||pStyle==='tie_m' ? '#2a2a2a' : pStyle==='hood_m' ? '#333' : '#3a2810'}/>

      {/* Neck */}
      <rect x={cx-r*0.3} y={faceY+r*0.85} width={r*0.6} height={h*0.12} fill={skin}/>

      {/* Head */}
      <ellipse cx={cx} cy={faceY} rx={r} ry={r*1.1} fill={skin}/>

      {/* Hair */}
      {pStyle === 'hat_m' && (
        <>
          <rect x={cx-r-2} y={faceY-r*1.1-8} width={r*2+4} height={8} fill="#3a2810" rx="1"/>
          <rect x={cx-r*0.8} y={faceY-r*1.1-22} width={r*1.6} height={18} fill="#4a3018" rx="2"/>
        </>
      )}
      {pStyle === 'hair_f' && (
        <>
          <ellipse cx={cx} cy={faceY-r*0.7} rx={r*1.1} ry={r*0.7} fill="#2a1808"/>
          <rect x={cx-r*1.1} y={faceY-r*0.5} width={r*0.4} height={r*1.2} fill="#2a1808"/>
          <rect x={cx+r*0.7} y={faceY-r*0.5} width={r*0.4} height={r*1.2} fill="#2a1808"/>
        </>
      )}
      {pStyle === 'bun_f' && (
        <>
          <ellipse cx={cx} cy={faceY-r*0.9} rx={r*1.05} ry={r*0.55} fill="#1a1008"/>
          <circle cx={cx+r*0.3} cy={faceY-r*1.2} r={r*0.3} fill="#2a1808"/>
        </>
      )}
      {(pStyle === 'suit_m' || pStyle === 'glasses_m' || pStyle === 'tie_m') && (
        <ellipse cx={cx} cy={faceY-r*0.95} rx={r*0.9} ry={r*0.45} fill="#1a1008"/>
      )}
      {pStyle === 'beard_m' && (
        <>
          <ellipse cx={cx} cy={faceY-r*0.95} rx={r*0.9} ry={r*0.45} fill="#3a2810"/>
          <ellipse cx={cx} cy={faceY+r*0.55} rx={r*0.75} ry={r*0.45} fill="#3a2810" opacity="0.9"/>
        </>
      )}
      {pStyle === 'hood_m' && (
        <>
          <path d={`M ${cx-r-4} ${faceY-r*0.3} Q ${cx-r*0.8} ${faceY-r*1.5} ${cx} ${faceY-r*1.3} Q ${cx+r*0.8} ${faceY-r*1.5} ${cx+r+4} ${faceY-r*0.3}`} fill="#333"/>
        </>
      )}

      {/* Eyes */}
      <ellipse cx={cx-r*0.35} cy={faceY-r*0.05} rx={r*0.18} ry={r*0.12} fill="#1a1008"/>
      <ellipse cx={cx+r*0.35} cy={faceY-r*0.05} rx={r*0.18} ry={r*0.12} fill="#1a1008"/>
      <circle cx={cx-r*0.35} cy={faceY-r*0.05} r={r*0.07} fill="#8a6040" opacity="0.7"/>
      <circle cx={cx+r*0.35} cy={faceY-r*0.05} r={r*0.07} fill="#8a6040" opacity="0.7"/>

      {/* Glasses */}
      {pStyle === 'glasses_m' && (
        <>
          <circle cx={cx-r*0.35} cy={faceY-r*0.05} r={r*0.22} fill="none" stroke="#4a3010" strokeWidth="1.2"/>
          <circle cx={cx+r*0.35} cy={faceY-r*0.05} r={r*0.22} fill="none" stroke="#4a3010" strokeWidth="1.2"/>
          <line x1={cx-r*0.13} y1={faceY-r*0.05} x2={cx+r*0.13} y2={faceY-r*0.05} stroke="#4a3010" strokeWidth="1.2"/>
        </>
      )}

      {/* Nose */}
      <ellipse cx={cx} cy={faceY+r*0.2} rx={r*0.1} ry={r*0.08} fill="rgba(0,0,0,0.18)"/>

      {/* Mouth */}
      <path d={`M ${cx-r*0.2} ${faceY+r*0.45} Q ${cx} ${faceY+r*0.55} ${cx+r*0.2} ${faceY+r*0.45}`} stroke="#5a3828" strokeWidth="1" fill="none"/>

      {/* Tie for suit/tie */}
      {(pStyle === 'tie_m') && (
        <path d={`M ${cx-3} ${faceY+r*0.85} L ${cx} ${faceY+r*1.1} L ${cx+3} ${faceY+r*0.85} L ${cx} ${faceY+r*0.75} Z`} fill="#5a1010" opacity="0.8"/>
      )}

      {/* Label if marked */}
      {label && (
        <>
          <line x1={x} y1={y} x2={x+w} y2={y+h} stroke="#cc2020" strokeWidth="1.5" opacity="0.6"/>
          <line x1={x+w} y1={y} x2={x} y2={y+h} stroke="#cc2020" strokeWidth="1.5" opacity="0.6"/>
          <text x={cx} y={y+h*0.55} textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="9" fill="#cc2020" fontWeight="700" opacity="0.9">{label}</text>
        </>
      )}

      {/* Sepia overlay */}
      <rect x={x} y={y} width={w} height={h} fill="rgba(120,80,20,0.22)" rx="1"/>

      {/* Film grain */}
      <rect x={x} y={y} width={w} height={h} fill="rgba(0,0,0,0.08)" rx="1"/>
    </g>
  )
}

/* ─── INVESTIGATION BOARD ────────────────────────────────────────── */
function InvestigationBoard() {
  return (
    <g>
      {/* ── Board frame ── */}
      <rect x="460" y="60" width="740" height="610" rx="4" fill="#2a1808" stroke="#3d2510" strokeWidth="8"/>
      {/* Cork surface */}
      <rect x="470" y="70" width="720" height="590" rx="2" fill="#7a5830"/>
      {/* Cork texture */}
      <rect x="470" y="70" width="720" height="590" rx="2" fill="rgba(100,60,20,0.3)"/>
      {Array.from({length:60}).map((_,i)=>(
        <circle key={i} cx={480+(i*83)%700} cy={80+(i*61)%570} r={1.5+i%3} fill="rgba(0,0,0,0.1)" opacity="0.5"/>
      ))}
      {/* Board tack holes */}
      {Array.from({length:20}).map((_,i)=>(
        <circle key={i} cx={490+(i*127)%690} cy={85+(i*97)%560} r="1.5" fill="rgba(0,0,0,0.15)"/>
      ))}

      {/* ══════════════════════════════════
          NEWSPAPER CLIPPINGS
      ══════════════════════════════════ */}

      {/* Clipping 1 — Main headline */}
      <g transform="rotate(-2, 510, 95)">
        <rect x="472" y="80" width="200" height="155" fill="#f0e8d0" stroke="#c8b890" strokeWidth="0.5"/>
        <rect x="472" y="80" width="200" height="20" fill="#1a1008"/>
        <text x="572" y="93" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8" fill="#d4b870" letterSpacing="2">THE HERALD GAZETTE</text>
        <text x="572" y="103" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="6" fill="#9a7850" letterSpacing="1">Est. 1908 · Investigative Edition</text>
        <line x1="472" y1="108" x2="672" y2="108" stroke="#c8b890" strokeWidth="0.5"/>
        <text x="572" y="120" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="10" fill="#1a1008" fontWeight="700">CORPORATE FRAUD</text>
        <text x="572" y="132" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="10" fill="#1a1008" fontWeight="700">SCANDAL EXPOSED</text>
        <line x1="480" y1="136" x2="664" y2="136" stroke="#2a1808" strokeWidth="0.5"/>
        <text x="572" y="147" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2810">Billions siphoned through offshore shell</text>
        <text x="572" y="157" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2810">corporations linked to Voss Holdings.</text>
        <text x="572" y="169" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2810">Three arrested. CEO whereabouts unknown.</text>
        <text x="572" y="181" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2810">Investigation continues.</text>
        <text x="480" y="226" fontFamily="'Courier Prime', monospace" fontSize="5.5" fill="#8a6840" letterSpacing="0.5">14 OCTOBER 2026 · PAGE 1</text>
        <circle cx="571" cy="80" r="5" fill="#8b1a1a"/>
        <circle cx="571" cy="80" r="3.5" fill="#aa2020"/>
      </g>

      {/* Clipping 2 — second article */}
      <g transform="rotate(1.5, 700, 88)">
        <rect x="696" y="75" width="175" height="128" fill="#ede5c8" stroke="#c8b890" strokeWidth="0.5"/>
        <rect x="696" y="75" width="175" height="16" fill="#2a1808"/>
        <text x="783" y="86" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="7" fill="#c4a860" letterSpacing="1.5">FINANCIAL TIMES</text>
        <text x="783" y="98" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8.5" fill="#1a1008" fontWeight="700">$2.3B LAUNDERED</text>
        <text x="783" y="110" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8.5" fill="#1a1008" fontWeight="700">VIA CAYMAN TRUST</text>
        <line x1="702" y1="114" x2="864" y2="114" stroke="#a89870" strokeWidth="0.5"/>
        {[0,1,2,3,4].map(l=>(
          <rect key={l} x="704" y={120+l*10} width={l%2===0 ? 148 : 120} height="3" rx="1" fill="#5a3810" opacity="0.4"/>
        ))}
        <text x="704" y="198" fontFamily="'Courier Prime', monospace" fontSize="5" fill="#8a6840">Oct 12, 2026</text>
        <circle cx="783" cy="75" r="5" fill="#1a3a8b"/>
        <circle cx="783" cy="75" r="3" fill="#2a4a9b"/>
      </g>

      {/* Clipping 3 */}
      <g transform="rotate(-1, 890, 80)">
        <rect x="880" y="70" width="150" height="110" fill="#f5edd5" stroke="#c8b890" strokeWidth="0.5"/>
        <rect x="880" y="70" width="150" height="14" fill="#3a1808"/>
        <text x="955" y="80" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="6.5" fill="#c4a860" letterSpacing="1">CITY TRIBUNE</text>
        <text x="955" y="93" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8" fill="#1a1008" fontWeight="700">SHELL CORPS</text>
        <text x="955" y="104" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8" fill="#1a1008" fontWeight="700">TRACED BACK</text>
        {[0,1,2,3].map(l=>(
          <rect key={l} x="888" y={112+l*10} width={l%2===0 ? 126 : 100} height="3" rx="1" fill="#5a3810" opacity="0.35"/>
        ))}
        <text x="888" y="175" fontFamily="'Courier Prime', monospace" fontSize="5" fill="#8a6840">Sept 28, 2026</text>
        <circle cx="954" cy="70" r="4.5" fill="#2a7a2a"/>
        <circle cx="954" cy="70" r="3" fill="#3a8a3a"/>
      </g>

      {/* Clipping 4 — bottom left area */}
      <g transform="rotate(2, 490, 430)">
        <rect x="472" y="430" width="180" height="130" fill="#f0e8cc" stroke="#c8b890" strokeWidth="0.5"/>
        <rect x="472" y="430" width="180" height="14" fill="#2a1808"/>
        <text x="562" y="440" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="6.5" fill="#c4a860" letterSpacing="1">INVESTIGATIVE POST</text>
        <text x="562" y="452" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8" fill="#1a1008" fontWeight="700">CEO MARCUS VOSS</text>
        <text x="562" y="463" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="8" fill="#1a1008" fontWeight="700">MISSING SINCE OCT 14</text>
        {[0,1,2,3,4].map(l=>(
          <rect key={l} x="480" y={472+l*10} width={l%2===0 ? 158 : 130} height="3" rx="1" fill="#5a3810" opacity="0.35"/>
        ))}
        <circle cx="562" cy="430" r="5" fill="#8b6a1a"/>
        <circle cx="562" cy="430" r="3.5" fill="#aa8020"/>
      </g>

      {/* ══════════════════════════════════
          STICKY NOTES with actual text
      ══════════════════════════════════ */}

      {/* Note 1 */}
      <g transform="rotate(-3, 700, 275)">
        <rect x="684" y="265" width="105" height="90" fill="#e8dc6a" stroke="rgba(0,0,0,0.1)" strokeWidth="0.5"/>
        <line x1="692" y1="282" x2="780" y2="282" stroke="rgba(0,0,0,0.15)" strokeWidth="0.7"/>
        <line x1="692" y1="294" x2="780" y2="294" stroke="rgba(0,0,0,0.15)" strokeWidth="0.7"/>
        <line x1="692" y1="306" x2="780" y2="306" stroke="rgba(0,0,0,0.15)" strokeWidth="0.7"/>
        <line x1="692" y1="318" x2="780" y2="318" stroke="rgba(0,0,0,0.15)" strokeWidth="0.7"/>
        <text x="696" y="279" fontFamily="'Courier Prime', monospace" fontSize="8" fill="#1a1008" fontWeight="700">FOLLOW THE</text>
        <text x="696" y="291" fontFamily="'Courier Prime', monospace" fontSize="8" fill="#1a1008" fontWeight="700">MONEY →</text>
        <text x="696" y="305" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#3a2010">Voss → shell co.</text>
        <text x="696" y="317" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#3a2010">→ Cayman #44</text>
        <text x="696" y="347" fontFamily="'Courier Prime', monospace" fontSize="6" fill="#8a6840" fontStyle="italic">check bank rec.</text>
        <circle cx="736" cy="265" r="4.5" fill="#8b1a1a"/>
      </g>

      {/* Note 2 */}
      <g transform="rotate(2, 890, 300)">
        <rect x="874" y="286" width="112" height="95" fill="#e0e870" stroke="rgba(0,0,0,0.1)" strokeWidth="0.5"/>
        <text x="880" y="303" fontFamily="'Courier Prime', monospace" fontSize="8" fill="#1a1008" fontWeight="700">ALIBI CHECK</text>
        <line x1="880" y1="308" x2="976" y2="308" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="880" y="320" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#2a1008">Hotel Meridian</text>
        <text x="880" y="331" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#2a1008">11PM — Oct 13</text>
        <line x1="880" y1="335" x2="976" y2="335" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="880" y="347" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#8a1a1a">UNVERIFIED ✗</text>
        <line x1="880" y1="351" x2="976" y2="351" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="880" y="366" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#5a3010" fontStyle="italic">3 witnesses</text>
        <text x="880" y="375" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#5a3010" fontStyle="italic">contradicted</text>
        <circle cx="930" cy="286" r="4.5" fill="#1a3a8b"/>
      </g>

      {/* Note 3 */}
      <g transform="rotate(-1.5, 1040, 240)">
        <rect x="1025" y="228" width="108" height="88" fill="#e8dc6a" stroke="rgba(0,0,0,0.1)" strokeWidth="0.5"/>
        <text x="1031" y="244" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#8b1a1a" fontWeight="700">⚠ WIRE TRANSFER</text>
        <line x1="1031" y1="249" x2="1123" y2="249" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="1031" y="261" fontFamily="'Courier Prime', monospace" fontSize="8" fill="#1a1008">$2,340,000</text>
        <text x="1031" y="273" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#3a2010">Oct 10 · 02:14 AM</text>
        <line x1="1031" y1="278" x2="1123" y2="278" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="1031" y="290" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#3a2010">Cayman Natl. Bk</text>
        <text x="1031" y="302" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#3a2010">Acct: ****7294</text>
        <circle cx="1079" cy="228" r="4.5" fill="#8b1a1a"/>
      </g>

      {/* Note 4 */}
      <g transform="rotate(1, 1080, 420)">
        <rect x="1065" y="408" width="95" height="80" fill="#f0e890" stroke="rgba(0,0,0,0.1)" strokeWidth="0.5"/>
        <text x="1071" y="423" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#1a1008" fontWeight="700">ACCOMPLICE?</text>
        <line x1="1071" y1="428" x2="1150" y2="428" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="1071" y="440" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">R. Hartmann</text>
        <text x="1071" y="451" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">CFO · Voss Holdings</text>
        <line x1="1071" y1="456" x2="1150" y2="456" stroke="rgba(0,0,0,0.12)" strokeWidth="0.7"/>
        <text x="1071" y="468" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#8a1a1a">signed transfer</text>
        <text x="1071" y="479" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#8a1a1a">documents → ?</text>
        <circle cx="1112" cy="408" r="4.5" fill="#2a7a2a"/>
      </g>

      {/* Note 5 — handwritten style */}
      <g transform="rotate(-2, 700, 490)">
        <rect x="680" y="475" width="115" height="85" fill="#e8d870" stroke="rgba(0,0,0,0.1)" strokeWidth="0.5"/>
        <text x="686" y="491" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#1a1008" fontWeight="700">SHELL CORPS:</text>
        <text x="686" y="503" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">• NovexTrade Ltd</text>
        <text x="686" y="514" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">• BlueHaven Corp</text>
        <text x="686" y="525" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">• ArcLight Holdings</text>
        <text x="686" y="536" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1008">• Meridian Trust</text>
        <text x="686" y="549" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#8a1a1a" fontStyle="italic">all registered 2024</text>
        <circle cx="737" cy="475" r="4.5" fill="#8b6a1a"/>
      </g>

      {/* ══════════════════════════════════
          PERSON PORTRAITS (mugshots)
      ══════════════════════════════════ */}

      {/* Row 1 portraits */}
      <PersonPortrait x={472} y={240} w={110} h={108} style="suit_m" name="MARCUS VOSS" label="SUSPECT #1"/>
      <PersonPortrait x={590} y={235} w={92} h={98} style="glasses_m" name="DR. R. HARTMANN"/>
      <PersonPortrait x={1010} y={78} w={88} h={105} style="hair_f" name="S. CHEN"/>
      <PersonPortrait x={1106} y={82} w={82} h={100} style="tie_m" name="P. LORENZ" label="FLED"/>

      {/* Row 2 portraits */}
      <PersonPortrait x={830} y={210} w={95} h={105} style="hat_m" name="UNKNOWN #3"/>
      <PersonPortrait x={933} y={205} w={88} h={100} style="bun_f" name="L. MOREIRA"/>
      <PersonPortrait x={472} y={356} w={88} h={100} style="hood_m" name="UNKNOWN #7"/>
      <PersonPortrait x={1010} y={350} w={95} h={105} style="beard_m" name="T. BLACKWOOD"/>
      <PersonPortrait x={1113} y={355} w={80} h={95} style="suit_m" name="ANALYST X"/>

      {/* Bottom row */}
      <PersonPortrait x={800} y={480} w={88} h={100} style="tie_m" name="J. WHITMORE"/>
      <PersonPortrait x={896} y={475} w={82} h={95} style="glasses_m" name="INFORMANT A"/>

      {/* ══════════════════════════════════
          RED STRING CONNECTIONS
          (thick, bright, very visible)
      ══════════════════════════════════ */}

      {/* Main suspect connections - thick bright red */}
      <line x1="527" y1="240" x2="636" y2="235" stroke="#dd1010" strokeWidth="2.5" opacity="0.9"/>
      <line x1="527" y1="240" x2="877" y2="210" stroke="#cc1818" strokeWidth="2.2" opacity="0.85"/>
      <line x1="636" y1="235" x2="877" y2="210" stroke="#cc1818" strokeWidth="2" opacity="0.8"/>
      <line x1="877" y1="210" x2="977" y2="205" stroke="#dd1010" strokeWidth="2.3" opacity="0.88"/>
      <line x1="877" y1="210" x2="1054" y2="78" stroke="#cc1818" strokeWidth="2" opacity="0.82"/>
      <line x1="977" y1="205" x2="1054" y2="78" stroke="#dd1010" strokeWidth="2.2" opacity="0.87"/>
      <line x1="1054" y1="78" x2="1147" y2="82" stroke="#cc1818" strokeWidth="2.5" opacity="0.9"/>

      {/* Cross-connections */}
      <line x1="527" y1="356" x2="527" y2="240" stroke="#bb0a0a" strokeWidth="2" opacity="0.8"/>
      <line x1="527" y1="356" x2="636" y2="235" stroke="#cc1818" strokeWidth="2" opacity="0.75"/>
      <line x1="877" y1="315" x2="736" y2="265" stroke="#dd1010" strokeWidth="2.2" opacity="0.85"/>
      <line x1="877" y1="315" x2="1079" y2="228" stroke="#cc1818" strokeWidth="2" opacity="0.8"/>
      <line x1="977" y1="205" x2="1112" y2="408" stroke="#dd1010" strokeWidth="2" opacity="0.78"/>
      <line x1="1147" y1="82" x2="1057" y2="350" stroke="#cc1818" strokeWidth="2.2" opacity="0.82"/>
      <line x1="844" y1="530" x2="736" y2="475" stroke="#dd1010" strokeWidth="2" opacity="0.8"/>
      <line x1="844" y1="530" x2="940" y2="475" stroke="#cc1818" strokeWidth="2" opacity="0.75"/>
      <line x1="527" y1="356" x2="737" y2="475" stroke="#dd1010" strokeWidth="2.2" opacity="0.85"/>
      <line x1="1057" y1="350" x2="940" y2="475" stroke="#cc1818" strokeWidth="2" opacity="0.8"/>
      <line x1="736" y1="265" x2="527" y2="240" stroke="#ee1212" strokeWidth="2.5" opacity="0.88"/>
      <line x1="930" y1="286" x2="977" y2="205" stroke="#dd1010" strokeWidth="2.2" opacity="0.85"/>
      <line x1="930" y1="286" x2="844" y2="530" stroke="#cc1818" strokeWidth="2" opacity="0.75"/>

      {/* String over note to photo connections */}
      <line x1="737" y1="315" x2="736" y2="475" stroke="#dd1010" strokeWidth="1.8" opacity="0.75"/>
      <line x1="1112" y1="408" x2="1057" y2="350" stroke="#cc1818" strokeWidth="2" opacity="0.82"/>
      <line x1="1079" y1="228" x2="1147" y2="82" stroke="#dd1818" strokeWidth="2.3" opacity="0.88"/>

      {/* Pushpins at string endpoints for realism */}
      {[
        [527, 240, '#8b1a1a'], [636, 235, '#8b6a1a'], [877, 210, '#8b1a1a'],
        [977, 205, '#1a3a8b'], [1054, 78, '#8b1a1a'], [1147, 82, '#8b1a1a'],
        [527, 356, '#2a7a2a'], [736, 265, '#8b1a1a'], [930, 286, '#1a3a8b'],
        [1079, 228, '#8b1a1a'], [1112, 408, '#2a7a2a'], [1057, 350, '#8b1a1a'],
        [844, 530, '#8b6a1a'], [940, 475, '#8b1a1a'],
      ].map(([px,py,pc],i)=>(
        <g key={i}>
          <circle cx={px} cy={py} r="6" fill={pc as string}/>
          <circle cx={px as number - 1.5} cy={py as number - 1.5} r="2.5" fill="rgba(255,255,255,0.3)"/>
        </g>
      ))}
    </g>
  )
}

/* ─── DESK SCENE SVG ──────────────────────────────────────────────── */
function DeskScene() {
  return (
    <svg
      viewBox="0 0 1920 1080"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient id="roomBg" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#030201"/>
          <stop offset="40%" stopColor="#080503"/>
          <stop offset="80%" stopColor="#110904"/>
          <stop offset="100%" stopColor="#1e1208"/>
        </linearGradient>
        <linearGradient id="deskSurface" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#2a1a08"/>
          <stop offset="15%" stopColor="#3d2610"/>
          <stop offset="35%" stopColor="#5c3a18"/>
          <stop offset="50%" stopColor="#6a4420"/>
          <stop offset="65%" stopColor="#5c3a18"/>
          <stop offset="85%" stopColor="#3d2610"/>
          <stop offset="100%" stopColor="#2a1a08"/>
        </linearGradient>
        <linearGradient id="deskFront" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#3d2610"/>
          <stop offset="100%" stopColor="#1e1208"/>
        </linearGradient>
        <radialGradient id="lampCone" cx="50%" cy="0%" r="100%">
          <stop offset="0%" stopColor="rgba(220,160,60,0.28)"/>
          <stop offset="40%" stopColor="rgba(200,130,40,0.12)"/>
          <stop offset="80%" stopColor="rgba(180,110,20,0.04)"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
        <radialGradient id="lampGlow" cx="50%" cy="0%" r="80%">
          <stop offset="0%" stopColor="rgba(255,200,80,0.55)"/>
          <stop offset="30%" stopColor="rgba(230,160,60,0.2)"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
        <radialGradient id="deskLampPool" cx="50%" cy="0%" r="60%">
          <stop offset="0%" stopColor="rgba(220,150,50,0.22)"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
        <radialGradient id="moonGlow" cx="50%" cy="30%" r="70%">
          <stop offset="0%" stopColor="rgba(140,170,210,0.18)"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
        <radialGradient id="vignette" cx="50%" cy="45%" r="70%">
          <stop offset="0%" stopColor="transparent"/>
          <stop offset="65%" stopColor="rgba(2,1,0,0.4)"/>
          <stop offset="100%" stopColor="rgba(2,1,0,0.88)"/>
        </radialGradient>
        <linearGradient id="book1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#3a2010"/><stop offset="100%" stopColor="#2a1408"/>
        </linearGradient>
        <linearGradient id="book2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#4a1818"/><stop offset="100%" stopColor="#350f0f"/>
        </linearGradient>
        <linearGradient id="book3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#1a2a1a"/><stop offset="100%" stopColor="#101a10"/>
        </linearGradient>
      </defs>

      {/* ── Room background ── */}
      <rect x="0" y="0" width="1920" height="1080" fill="url(#roomBg)"/>
      <rect x="0" y="0" width="1920" height="220" fill="#020100"/>

      {/* Wall panels */}
      {[0,1,2,3].map(i => (
        <rect key={i} x={60+i*460} y={180} width={400} height={480} fill="none" stroke="rgba(60,35,15,0.2)" strokeWidth="2" rx="3"/>
      ))}

      {/* ── Window (left) ── */}
      <rect x="60" y="130" width="340" height="460" fill="#0a0806" rx="4"/>
      <rect x="72" y="145" width="316" height="432" fill="#050302" stroke="#3a2510" strokeWidth="10" rx="2"/>
      <rect x="77" y="150" width="306" height="422" fill="#0d1520"/>
      <rect x="77" y="150" width="306" height="422" fill="url(#moonGlow)"/>
      <line x1="230" y1="150" x2="230" y2="572" stroke="#3a2510" strokeWidth="8"/>
      <line x1="77" y1="360" x2="383" y2="360" stroke="#3a2510" strokeWidth="8"/>
      <line x1="154" y1="150" x2="154" y2="360" stroke="#2a1808" strokeWidth="4"/>
      <line x1="307" y1="150" x2="307" y2="360" stroke="#2a1808" strokeWidth="4"/>
      <line x1="77" y1="254" x2="383" y2="254" stroke="#2a1808" strokeWidth="4"/>
      <line x1="77" y1="468" x2="383" y2="468" stroke="#2a1808" strokeWidth="4"/>
      <rect x="60" y="575" width="360" height="22" fill="#3a2510"/>
      {/* Curtains */}
      <path d="M 60 130 C 52 200, 48 300, 52 440 C 55 520, 50 560, 54 590" stroke="#2a1808" strokeWidth="48" strokeLinecap="butt" fill="none"/>
      <path d="M 60 130 C 52 200, 48 300, 52 440 C 55 520, 50 560, 54 590" stroke="#1e1208" strokeWidth="32" strokeLinecap="butt" fill="none"/>
      <path d="M 400 130 C 408 200, 412 300, 408 440 C 405 520, 410 560, 406 590" stroke="#2a1808" strokeWidth="48" strokeLinecap="butt" fill="none"/>
      <path d="M 400 130 C 408 200, 412 300, 408 440 C 405 520, 410 560, 406 590" stroke="#1e1208" strokeWidth="32" strokeLinecap="butt" fill="none"/>
      <rect x="42" y="120" width="380" height="16" rx="8" fill="#3a2510"/>
      <circle cx="42" cy="128" r="9" fill={GOLD}/>
      <circle cx="422" cy="128" r="9" fill={GOLD}/>

      {/* ── Investigation board ── */}
      <InvestigationBoard/>

      {/* Board wall lamp */}
      <g transform="translate(830, 55)">
        <rect x="-6" y="0" width="12" height="30" rx="3" fill="#1a1008"/>
        <path d="M -35 30 L 35 30 L 50 75 L -50 75 Z" fill="#2a1a08"/>
        <ellipse cx="0" cy="30" rx="18" ry="5" fill="#3a2510"/>
        <ellipse cx="0" cy="75" rx="38" ry="6" fill="#1a1008"/>
        <ellipse cx="0" cy="50" rx="15" ry="7" fill="rgba(255,210,90,0.35)" className="lamp-glow"/>
      </g>

      {/* ── Hanging desk lamp ── */}
      <path d="M 960 0 Q 940 30, 935 60 Q 928 100, 930 130" stroke="#1a1008" strokeWidth="6" fill="none" strokeLinecap="round"/>
      <path d="M 890 130 L 970 130 L 1010 175 L 850 175 Z" fill="#2a1a08"/>
      <path d="M 895 133 L 965 133 L 1003 172 L 857 172 Z" fill="#1a1008"/>
      <ellipse cx="930" cy="130" rx="40" ry="8" fill="#3a2510"/>
      <ellipse cx="930" cy="175" rx="80" ry="10" fill="#1e1208"/>
      <ellipse cx="930" cy="145" rx="25" ry="12" fill="rgba(255,220,100,0.6)" className="lamp-glow"/>
      <path d="M 850 175 L 500 680 L 1360 680 L 1010 175 Z" fill="url(#lampCone)" className="lamp-glow"/>
      <path d="M 870 175 L 680 580 L 1180 580 L 990 175 Z" fill="url(#lampGlow)" className="lamp-glow-2" opacity="0.7"/>
      <ellipse cx="930" cy="730" rx="420" ry="80" fill="url(#deskLampPool)" className="lamp-glow"/>

      {/* ── Desk surface ── */}
      <path d="M -100 680 L 2020 680 L 2200 1080 L -280 1080 Z" fill="url(#deskSurface)"/>
      {[0,1,2,3,4,5,6,7].map(i => (
        <path key={i} d={`M ${-80+i*80} 680 L ${-180+i*100} 1080`} stroke="rgba(0,0,0,0.08)" strokeWidth={1+i%3}/>
      ))}
      <rect x="-100" y="680" width="2220" height="30" fill="#3d2410"/>
      <path d="M -100 710 L 2020 710 L 2200 1080 L -280 1080 Z" fill="url(#deskFront)" opacity="0.7"/>
      <line x1="-100" y1="680" x2="2020" y2="680" stroke="rgba(200,140,60,0.12)" strokeWidth="2"/>

      {/* ── LEFT SIDE: Books ── */}
      <g transform="translate(185, 622)">
        <rect x="-55" y="-8" width="130" height="22" rx="2" fill="url(#book2)"/>
        <rect x="-60" y="-32" width="120" height="24" rx="2" fill="url(#book1)"/>
        <line x1="-55" y1="-18" x2="55" y2="-18" stroke="rgba(255,255,255,0.06)" strokeWidth="0.5"/>
        <rect x="-52" y="-58" width="115" height="26" rx="2" fill="url(#book3)"/>
        <line x1="-32" y1="-46" x2="46" y2="-46" stroke="rgba(200,160,60,0.4)" strokeWidth="1.5"/>
        <line x1="-32" y1="-42" x2="24" y2="-42" stroke="rgba(200,160,60,0.25)" strokeWidth="1"/>
        <rect x="-55" y="-60" width="6" height="74" fill="rgba(0,0,0,0.3)"/>
      </g>

      {/* ── LEFT SIDE: Open leather notebook (clearly left of NOCTRA center) ── */}
      <g transform="translate(340, 668) rotate(-4)">
        <ellipse cx="0" cy="22" rx="130" ry="18" fill="rgba(0,0,0,0.4)"/>
        {/* Back cover */}
        <rect x="-130" y="-88" width="265" height="112" rx="4" fill="#1e1208"/>
        {/* Left page */}
        <path d="M -128 -86 L -5 -86 L -5 20 L -128 20 Z" fill="#f2ead8"/>
        {/* Right page */}
        <path d="M -3 -86 L 133 -86 L 133 20 L -3 20 Z" fill="#ede5ce"/>
        {/* Spine */}
        <rect x="-6" y="-86" width="12" height="106" fill="#1e1208"/>
        {/* Ruled lines left */}
        {[0,1,2,3,4,5,6].map(i=>(
          <line key={i} x1="-120" y1={-70+i*13} x2="-12" y2={-70+i*13} stroke="rgba(180,150,100,0.28)" strokeWidth="0.7"/>
        ))}
        {/* Ruled lines right */}
        {[0,1,2,3,4,5,6].map(i=>(
          <line key={i} x1="8" y1={-70+i*13} x2="125" y2={-70+i*13} stroke="rgba(180,150,100,0.28)" strokeWidth="0.7"/>
        ))}
        {/* Handwritten content — left page */}
        <text x="-118" y="-74" fontFamily="'Courier Prime', monospace" fontSize="7.5" fill="#2a1808" fontWeight="700">CASE FILE: NOC-2026</text>
        <text x="-118" y="-61" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Subject: Voss Holdings</text>
        <text x="-118" y="-48" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Fraud scale: $2.3B est.</text>
        <text x="-118" y="-35" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Networks: 14 identified</text>
        <text x="-118" y="-22" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#8a1a1a">Status: ACTIVE ⚠</text>
        <text x="-118" y="-9" fontFamily="'Courier Prime', monospace" fontSize="6" fill="#5a3810" fontStyle="italic">Lead: Marcus Voss</text>
        <text x="-118" y="4" fontFamily="'Courier Prime', monospace" fontSize="6" fill="#5a3810" fontStyle="italic">Accomplice: R. Hartmann</text>
        {/* Right page content */}
        <text x="10" y="-74" fontFamily="'Courier Prime', monospace" fontSize="7" fill="#2a1808" fontWeight="700">TIMELINE</text>
        <text x="10" y="-61" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Sep 15 — First transfer</text>
        <text x="10" y="-48" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Oct 10 — $2.3M wired</text>
        <text x="10" y="-35" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Oct 12 — Voss spotted</text>
        <text x="10" y="-22" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#3a2010">Oct 13 — Hotel mtg</text>
        <text x="10" y="-9" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#8a1a1a">Oct 14 — DISAPPEARS</text>
        <text x="10" y="6" fontFamily="'Courier Prime', monospace" fontSize="6" fill="#5a3810" fontStyle="italic">Oct 16 — Case opened</text>
        {/* Fountain pen */}
        <g transform="rotate(12) translate(60, -60)">
          <rect x="0" y="-3" width="88" height="7" rx="3.5" fill="#1a1008"/>
          <rect x="72" y="-3" width="12" height="7" rx="1" fill={GOLD}/>
          <rect x="84" y="-4" width="14" height="9" rx="3" fill="#2a1a08"/>
          <path d="M 0 -1 L -10 0 L 0 1 Z" fill="#6a5020"/>
          <line x1="-10" y1="0" x2="0" y2="0" stroke={GOLD} strokeWidth="0.8"/>
        </g>
        {/* Red ribbon bookmark */}
        <rect x="-14" y="-88" width="10" height="38" fill="#8b1a1a"/>
        <path d="M -14 -50 L -9 -40 L -4 -50" fill="#8b1a1a"/>
      </g>

      {/* ── RIGHT SIDE: Magnifying glass ── */}
      <g transform="translate(1380, 660) rotate(-20)">
        <circle cx="0" cy="0" r="40" fill="none" stroke="#8a6830" strokeWidth="6"/>
        <circle cx="0" cy="0" r="33" fill="rgba(120,160,180,0.06)" stroke="#7a5820" strokeWidth="2"/>
        <rect x="29" y="-5" width="62" height="10" rx="5" fill="#5a3810"/>
        <rect x="31" y="-3" width="58" height="3" fill="rgba(255,255,255,0.06)"/>
        <ellipse cx="-13" cy="-13" rx="11" ry="6" fill="rgba(180,220,255,0.1)" transform="rotate(-20)"/>
        <circle cx="0" cy="0" r="40" fill="none" stroke="#a08040" strokeWidth="1" opacity="0.5"/>
      </g>

      {/* ── RIGHT SIDE: Wax-sealed envelope ── */}
      <g transform="translate(1580, 672) rotate(6)">
        <ellipse cx="0" cy="35" rx="100" ry="12" fill="rgba(0,0,0,0.4)"/>
        <rect x="-100" y="-60" width="200" height="100" rx="3" fill="#e8dcc0"/>
        <rect x="-100" y="-60" width="200" height="100" rx="3" fill="none" stroke="#c8b890" strokeWidth="1.5"/>
        <path d="M -100 -60 L 0 -12 L 100 -60" stroke="#c8b890" strokeWidth="1" fill="none"/>
        <path d="M -100 40 L 0 -12 L 100 40" stroke="rgba(0,0,0,0.08)" strokeWidth="1" fill="rgba(0,0,0,0.03)"/>
        <circle cx="0" cy="-10" r="20" fill="#7a1818"/>
        <circle cx="0" cy="-10" r="17" fill="#8b1a1a"/>
        <text x="0" y="-5" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="13" fontWeight="600" fill="rgba(240,220,180,0.75)">N</text>
      </g>

      {/* ── RIGHT SIDE: Scattered case papers ── */}
      {[[1280, 702, -5, 'EXHIBIT A — BANK RECORDS', 'Account: ****7294 · Balance: $0'], [1400, 695, 4, 'WIRE TRANSFER RECEIPT', 'Ref: CAY-2026-10-0094'], [1500, 708, -2, 'SURVEILLANCE REPORT', 'Subject: Voss · Hotel Meridian']].map(([x,y,r,title,sub],i) => (
        <g key={i} transform={`translate(${x},${y}) rotate(${r})`}>
          <rect x="-72" y="-55" width="144" height="115" rx="2" fill="#f0e8d5" opacity={0.88-Number(i)*0.06}/>
          <rect x="-72" y="-55" width="144" height="14" fill="#e0d8c0" opacity="0.8"/>
          <text x="0" y="-44" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="7" fill="#3a2010" letterSpacing="0.5">{String(title)}</text>
          <line x1="-62" y1="-38" x2="62" y2="-38" stroke="rgba(0,0,0,0.1)" strokeWidth="0.7"/>
          <text x="-60" y="-26" fontFamily="'Courier Prime', monospace" fontSize="6.5" fill="#5a3810">{String(sub)}</text>
          {[0,1,2,3,4].map(l=>(
            <line key={l} x1="-60" y1={-15+l*13} x2="60" y2={-15+l*13} stroke="rgba(0,0,0,0.1)" strokeWidth="0.7"/>
          ))}
          {/* Rubber stamp mark */}
          <rect x="10" y="20" width="50" height="18" rx="2" fill="none" stroke="#8b1a1a" strokeWidth="1.5" opacity="0.5" transform="rotate(-8,35,29)"/>
          <text x="34" y="32" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="6" fill="#8b1a1a" opacity="0.6" transform="rotate(-8,34,32)">CLASSIFIED</text>
        </g>
      ))}

      {/* ── RIGHT SIDE: Inkwell ── */}
      <g transform="translate(1720, 655)">
        <ellipse cx="0" cy="18" rx="26" ry="10" fill="rgba(0,0,0,0.5)"/>
        <rect x="-22" y="-28" width="44" height="46" rx="16" fill="#0d0a06"/>
        <rect x="-18" y="-24" width="36" height="20" rx="12" fill="#1a1510"/>
        <ellipse cx="0" cy="-24" rx="18" ry="6" fill="#050302"/>
        <ellipse cx="0" cy="-26" rx="20" ry="5" fill="#2a1e0a" stroke="#4a3010" strokeWidth="1"/>
        <rect x="-22" y="-2" width="44" height="6" rx="2" fill="#6a4810"/>
      </g>

      {/* ── Brass desk clock ── */}
      <g transform="translate(1820, 624)">
        <circle cx="0" cy="0" r="42" fill="#1e1208" stroke="#8a6820" strokeWidth="4"/>
        <circle cx="0" cy="0" r="36" fill="#0a0805"/>
        <circle cx="0" cy="0" r="35" fill="none" stroke="#6a5010" strokeWidth="1" strokeDasharray="2,10"/>
        <line x1="0" y1="0" x2="0" y2="-22" stroke={GOLD} strokeWidth="2.5" strokeLinecap="round"/>
        <line x1="0" y1="0" x2="16" y2="-8" stroke={GOLD} strokeWidth="1.5" strokeLinecap="round" className="pendulum"/>
        <circle cx="0" cy="0" r="3" fill={GOLD}/>
        <circle cx="22" cy="60" r="10" fill="#3a2810" stroke="#8a6820" strokeWidth="2"/>
        <line x1="0" y1="0" x2="22" y2="50" stroke="#5a3818" strokeWidth="1.5" className="pendulum"/>
      </g>

      {/* ── Vignette ── */}
      <rect x="0" y="0" width="1920" height="1080" fill="url(#vignette)" pointerEvents="none"/>
      <rect x="0" y="1050" width="1920" height="30" fill="rgba(0,0,0,0.6)"/>
    </svg>
  )
}

/* ─── OWL SVG ─────────────────────────────────────────────────────── */
function Orion({ headAngle, eyeOffset, isBlinking }: {
  headAngle: number
  eyeOffset: { x: number; y: number }
  isBlinking: boolean
}) {
  return (
    <svg viewBox="-90 -180 180 220" width="180" height="220" style={{ overflow: 'visible', filter: 'drop-shadow(0 8px 30px rgba(0,0,0,0.8))' }}>
      <defs>
        <radialGradient id="bodyGrd" cx="40%" cy="30%">
          <stop offset="0%" stopColor="#5c3d20"/>
          <stop offset="45%" stopColor="#3a2510"/>
          <stop offset="100%" stopColor="#1e1208"/>
        </radialGradient>
        <radialGradient id="bellyGrd" cx="50%" cy="40%">
          <stop offset="0%" stopColor="#7a5a30"/>
          <stop offset="60%" stopColor="#5a4020"/>
          <stop offset="100%" stopColor="#3a2810"/>
        </radialGradient>
        <radialGradient id="irisGrd" cx="35%" cy="30%">
          <stop offset="0%" stopColor="#f5b800"/>
          <stop offset="40%" stopColor="#d48000"/>
          <stop offset="80%" stopColor="#a85000"/>
          <stop offset="100%" stopColor="#6a2800"/>
        </radialGradient>
        <radialGradient id="headGrd" cx="35%" cy="25%">
          <stop offset="0%" stopColor="#503820"/>
          <stop offset="60%" stopColor="#2e1e0c"/>
          <stop offset="100%" stopColor="#1a1008"/>
        </radialGradient>
        <linearGradient id="wingGrd" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3a2510"/>
          <stop offset="100%" stopColor="#1e1208"/>
        </linearGradient>
      </defs>

      {/* Talons */}
      <g style={{ transform: 'translateY(28px)' }}>
        <path d="M -30 30 Q -35 38 -42 32" stroke="#1a1008" strokeWidth="4" strokeLinecap="round" fill="none"/>
        <path d="M -30 30 Q -28 40 -22 36" stroke="#1a1008" strokeWidth="4" strokeLinecap="round" fill="none"/>
        <path d="M -30 30 Q -20 38 -16 32" stroke="#1a1008" strokeWidth="3.5" strokeLinecap="round" fill="none"/>
        <circle cx="-30" cy="30" r="5" fill="#1e1208"/>
        <path d="M 30 30 Q 35 38 42 32" stroke="#1a1008" strokeWidth="4" strokeLinecap="round" fill="none"/>
        <path d="M 30 30 Q 28 40 22 36" stroke="#1a1008" strokeWidth="4" strokeLinecap="round" fill="none"/>
        <path d="M 30 30 Q 20 38 16 32" stroke="#1a1008" strokeWidth="3.5" strokeLinecap="round" fill="none"/>
        <circle cx="30" cy="30" r="5" fill="#1e1208"/>
      </g>

      {/* Body */}
      <g className="owl-body-anim">
        <ellipse cx="0" cy="10" rx="62" ry="78" fill="url(#bodyGrd)"/>
        <path d="M -62 -10 C -70 10, -68 40, -58 65 C -52 78, -42 82, -30 70 C -20 60, -15 40, -18 10 Z" fill="url(#wingGrd)" className="owl-wing-anim"/>
        {[-1,0,1].map(i=>(
          <path key={i} d={`M ${-62+i*2} ${10+i*20} C ${-65+i} ${30+i*15}, -55 ${55+i*10}, ${-40+i*3} 70`} stroke="rgba(0,0,0,0.35)" strokeWidth="1.5" fill="none"/>
        ))}
        <path d="M 62 -10 C 70 10, 68 40, 58 65 C 52 78, 42 82, 30 70 C 20 60, 15 40, 18 10 Z" fill="url(#wingGrd)" className="owl-wing-anim"/>
        {[1,0,-1].map(i=>(
          <path key={i} d={`M ${62-i*2} ${10+i*20} C ${65-i} ${30+i*15}, 55 ${55+i*10}, ${40-i*3} 70`} stroke="rgba(0,0,0,0.35)" strokeWidth="1.5" fill="none"/>
        ))}
        <ellipse cx="0" cy="18" rx="38" ry="58" fill="url(#bellyGrd)"/>
        {[-3,-1.5,0,1.5,3].map((x,i)=>(
          <path key={i} d={`M ${x*6-5} ${-20+i*8} Q ${x*3} ${-10+i*8}, ${x*6+5} ${-5+i*8}`} stroke="rgba(0,0,0,0.3)" strokeWidth="1.2" strokeLinecap="round" fill="none"/>
        ))}
      </g>

      {/* Head */}
      <g style={{ transform: `rotate(${headAngle}deg)`, transformOrigin: '0px -40px', transition: 'transform 0.6s cubic-bezier(0.4,0,0.2,1)' }}>
        <circle cx="0" cy="-72" r="52" fill="url(#headGrd)"/>
        <polygon points="-28,-122 -22,-95 -10,-118" fill="#1e1208"/>
        <polygon points="-26,-122 -20,-96 -9,-116" fill="#2e1e0c"/>
        <polygon points="28,-122 22,-95 10,-118" fill="#1e1208"/>
        <polygon points="26,-122 20,-96 9,-116" fill="#2e1e0c"/>
        <ellipse cx="0" cy="-68" rx="36" ry="42" fill="#4a3018" opacity="0.7"/>

        {/* Left eye */}
        <circle cx="-20" cy="-70" r="17" fill="#0a0502"/>
        <circle cx="-20" cy="-70" r="15" fill="url(#irisGrd)"/>
        <circle cx={-20+eyeOffset.x} cy={-70+eyeOffset.y} r="8" fill="#050200"/>
        <circle cx={-20+eyeOffset.x-3} cy={-70+eyeOffset.y-3} r="2.5" fill="rgba(255,248,220,0.75)"/>
        <clipPath id="lec"><circle cx="-20" cy="-70" r="17"/></clipPath>
        <rect x="-38" y={isBlinking ? -87 : -107} width="36" height="22" fill="#2e1e0c" clipPath="url(#lec)" style={{ transition: 'y 0.08s ease' }}/>

        {/* Right eye */}
        <circle cx="20" cy="-70" r="17" fill="#0a0502"/>
        <circle cx="20" cy="-70" r="15" fill="url(#irisGrd)"/>
        <circle cx={20+eyeOffset.x} cy={-70+eyeOffset.y} r="8" fill="#050200"/>
        <circle cx={20+eyeOffset.x+3} cy={-70+eyeOffset.y-3} r="2.5" fill="rgba(255,248,220,0.75)"/>
        <clipPath id="rec"><circle cx="20" cy="-70" r="17"/></clipPath>
        <rect x="2" y={isBlinking ? -87 : -107} width="36" height="22" fill="#2e1e0c" clipPath="url(#rec)" style={{ transition: 'y 0.08s ease' }}/>

        <path d="M -7 -58 L 0 -44 L 7 -58 Q 0 -62 -7 -58 Z" fill="#9a8040"/>
      </g>
    </svg>
  )
}

/* ─── CONFIDENTIAL FOLDER ─────────────────────────────────────────── */
function ConfidentialFolder({ phase, onHover, onClick }: {
  phase: 'idle' | 'hover' | 'cracking' | 'opening' | 'open'
  onHover: (h: boolean) => void
  onClick: () => void
}) {
  const isOpening = phase === 'cracking' || phase === 'opening' || phase === 'open'
  return (
    <div
      className="folder-container"
      style={{
        position: 'relative', width: 260,
        cursor: isOpening ? 'default' : 'pointer',
        filter: isOpening ? 'drop-shadow(0 30px 60px rgba(0,0,0,0.9)) drop-shadow(0 0 40px rgba(200,140,40,0.3))' : 'drop-shadow(0 12px 30px rgba(0,0,0,0.7))',
        transform: phase==='hover' ? 'translateY(-8px) scale(1.012)' : phase==='cracking' ? 'translateY(-12px) scale(1.02)' : 'none',
        transition: 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1), filter 0.3s ease',
      }}
      onMouseEnter={() => !isOpening && onHover(true)}
      onMouseLeave={() => !isOpening && onHover(false)}
      onClick={() => !isOpening && onClick()}
    >
      <svg viewBox="0 0 260 340" width="260" height="340" style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id="fGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#c8a870"/>
            <stop offset="40%" stopColor="#b89458"/>
            <stop offset="100%" stopColor="#9a7840"/>
          </linearGradient>
          <linearGradient id="fTop" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#c8a870"/><stop offset="100%" stopColor="#b08840"/>
          </linearGradient>
          <radialGradient id="warmEsc" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255,200,80,0.6)"/>
            <stop offset="100%" stopColor="transparent"/>
          </radialGradient>
        </defs>
        <ellipse cx="130" cy="340" rx="120" ry="16" fill="rgba(0,0,0,0.5)"/>
        {isOpening && <ellipse cx="130" cy="160" rx="90" ry="60" fill="url(#warmEsc)" opacity="0.5"/>}
        <path d="M 10 40 Q 10 30 20 30 L 95 30 Q 105 30 110 20 L 150 20 Q 155 30 165 30 L 240 30 Q 250 30 250 40 L 250 320 Q 250 330 240 330 L 20 330 Q 10 330 10 320 Z" fill="#a07838"/>
        <g className={phase==='opening'||phase==='open' ? 'folder-opening' : ''} style={{ transformOrigin: '130px 330px' }}>
          <path d="M 10 55 Q 10 45 20 45 L 240 45 Q 250 45 250 55 L 250 320 Q 250 330 240 330 L 20 330 Q 10 330 10 320 Z" fill="url(#fGrad)"/>
          {[0,1,2,3,4,5].map(i=>(
            <line key={i} x1="10" y1={75+i*42} x2="250" y2={75+i*42} stroke="rgba(0,0,0,0.07)" strokeWidth="1"/>
          ))}
          <path d="M 85 45 L 85 30 Q 85 22 93 22 L 167 22 Q 175 22 175 30 L 175 45 Z" fill="url(#fTop)"/>
          <circle cx="130" cy="175" r="12" fill="#3a2510"/>
          <circle cx="130" cy="175" r="8" fill="#8a6830"/>
          <circle cx="130" cy="175" r="5" fill="#6a4820"/>
          <circle cx="128" cy="173" r="2" fill="rgba(255,255,255,0.2)"/>
          <text x="130" y="110" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="12" fontWeight="700" letterSpacing="3.5" fill={CRIMSON} opacity="0.9">CONFIDENTIAL</text>
          <rect x="28" y="96" width="204" height="21" rx="2" fill="none" stroke={CRIMSON} strokeWidth="1.5" opacity="0.55"/>
          <text x="130" y="146" textAnchor="middle" fontFamily="'Courier Prime', monospace" fontSize="8" fill="rgba(80,50,20,0.55)" letterSpacing="1">CASE FILE: NOC-2026-0001</text>
          <text x="130" y="240" textAnchor="middle" fontFamily="'Cinzel', serif" fontSize="9" letterSpacing="5" fill="rgba(80,50,20,0.55)">NOCTRA</text>
          <rect x="20" y="40" width="220" height="8" rx="1" fill="#f0e8d5" opacity="0.55"/>
          <rect x="25" y="38" width="210" height="6" rx="1" fill="#ede3cc" opacity="0.38"/>
          <path d="M 220 310 L 250 310 L 250 330 Z" fill="rgba(0,0,0,0.12)"/>
          {(phase==='idle'||phase==='hover') && (
            <text x="130" y="290" textAnchor="middle" fontFamily="'Cormorant Garamond', serif" fontSize="10" letterSpacing="2" fill={`rgba(80,50,20,${phase==='hover'?'0.7':'0.35'})`} fontStyle="italic" style={{ transition: 'fill 0.3s' }}>
              Open Investigation
            </text>
          )}
        </g>
        {(phase==='opening'||phase==='open') && (
          <g className="docs-reveal">
            <rect x="30" y="50" width="200" height="270" rx="2" fill="#f0e8d5"/>
            {[0,1,2,3,4,5,6,7,8].map(i=>(
              <line key={i} x1="50" y1={85+i*22} x2="210" y2={85+i*22} stroke="rgba(100,70,30,0.18)" strokeWidth="0.8"/>
            ))}
            <rect x="55" y="78" width="80" height="6" rx="2" fill="rgba(80,50,20,0.35)"/>
            <rect x="55" y="92" width="120" height="3" rx="1" fill="rgba(80,50,20,0.2)"/>
          </g>
        )}
      </svg>
    </div>
  )
}

/* ─── HUB ─────────────────────────────────────────────────────────── */
function InvestigationHub({ onBack }: { onBack: () => void }) {
  const [hovered, setHovered] = useState<number|null>(null)
  const modules = [
    { key:'SIG', label:'Signal Trace', sub:'Pattern recognition across sources' },
    { key:'DPR', label:'Deep Profile', sub:'Structured entity intelligence' },
    { key:'TMP', label:'Temporal Map', sub:'Chronological event threading' },
    { key:'NET', label:'Network Graph', sub:'Relationship constellation analysis' },
    { key:'DOC', label:'Document Vault', sub:'Classified material synthesis' },
    { key:'SNT', label:'Sentinel Alert', sub:'Continuous surveillance feed' },
  ]
  return (
    <div className="hub-overlay hub-entering">
      <div style={{ position:'absolute', inset:0, backgroundImage:`linear-gradient(rgba(201,168,76,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(201,168,76,0.03) 1px, transparent 1px)`, backgroundSize:'80px 80px' }}/>
      <div style={{ position:'absolute', top:0, left:0, right:0, padding:'28px 48px', display:'flex', alignItems:'center', justifyContent:'space-between', borderBottom:'1px solid rgba(201,168,76,0.1)', zIndex:10 }}>
        <div style={{ display:'flex', alignItems:'center', gap:16 }}>
          <div style={{ width:32, height:32, borderRadius:'50%', background:'radial-gradient(circle at 38% 32%, #a02020, #620e0e)', display:'flex', alignItems:'center', justifyContent:'center', boxShadow:'0 2px 12px rgba(140,20,20,0.4)' }}>
            <span style={{ fontFamily:"'Cinzel', serif", fontSize:10, color:'rgba(240,220,180,0.85)', fontWeight:600 }}>N</span>
          </div>
          <div>
            <div style={{ fontFamily:"'Cinzel', serif", fontSize:13, letterSpacing:'0.28em', color:'rgba(240,220,180,0.9)', fontWeight:600 }}>NOCTRA</div>
            <div style={{ fontFamily:"'Cormorant Garamond', serif", fontSize:10, letterSpacing:'0.2em', color:'rgba(201,168,76,0.5)', fontStyle:'italic' }}>Investigation Bureau</div>
          </div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:32 }}>
          <span style={{ fontFamily:"'Inter', sans-serif", fontSize:11, letterSpacing:'0.12em', color:'rgba(201,168,76,0.5)', textTransform:'uppercase' }}>Case #NOC-2026-0001</span>
          <button onClick={onBack} style={{ background:'none', border:'1px solid rgba(201,168,76,0.2)', color:'rgba(201,168,76,0.6)', fontFamily:"'Cinzel', serif", fontSize:10, letterSpacing:'0.2em', padding:'7px 16px', cursor:'pointer', borderRadius:1, transition:'all 0.2s' }}
            onMouseEnter={e=>{ e.currentTarget.style.borderColor='rgba(201,168,76,0.6)'; e.currentTarget.style.color='rgba(201,168,76,0.9)' }}
            onMouseLeave={e=>{ e.currentTarget.style.borderColor='rgba(201,168,76,0.2)'; e.currentTarget.style.color='rgba(201,168,76,0.6)' }}>
            ← RETURN
          </button>
        </div>
      </div>
      <div style={{ position:'relative', zIndex:5, textAlign:'center', marginBottom:56 }}>
        <div style={{ fontFamily:"'Cormorant Garamond', serif", fontSize:11, letterSpacing:'0.3em', color:'rgba(201,168,76,0.45)', textTransform:'uppercase', marginBottom:20 }}>Clearance Level · Alpha</div>
        <h1 style={{ fontFamily:"'Cinzel', serif", fontSize:'clamp(36px,5vw,64px)', fontWeight:600, letterSpacing:'0.22em', color:'#e8d8a0', lineHeight:1.1, textShadow:`0 0 60px rgba(201,168,76,0.2), 0 2px 4px rgba(0,0,0,0.8)`, marginBottom:12 }}>INVESTIGATION HUB</h1>
        <div style={{ width:1, height:60, background:'linear-gradient(to bottom, transparent, rgba(201,168,76,0.4), transparent)', margin:'16px auto' }}/>
        <p style={{ fontFamily:"'Cormorant Garamond', serif", fontSize:16, fontStyle:'italic', letterSpacing:'0.1em', color:'rgba(201,168,76,0.55)' }}>Select your investigation module</p>
      </div>
      <div style={{ position:'relative', zIndex:5, display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:2, maxWidth:900, width:'100%', padding:'0 24px' }}>
        {modules.map((mod,i) => (
          <div key={i} onMouseEnter={()=>setHovered(i)} onMouseLeave={()=>setHovered(null)} style={{ padding:'32px 28px', background:hovered===i?'rgba(201,168,76,0.07)':'rgba(255,255,255,0.018)', border:`1px solid ${hovered===i?'rgba(201,168,76,0.3)':'rgba(201,168,76,0.08)'}`, cursor:'pointer', transition:'all 0.25s ease', position:'relative' }}>
            <div style={{ position:'absolute', top:0, left:0, right:0, height:1, background:hovered===i?'rgba(201,168,76,0.5)':'transparent', transition:'background 0.25s' }}/>
            <div style={{ fontFamily:"'Cinzel', serif", fontSize:9, letterSpacing:'0.2em', color:'rgba(201,168,76,0.4)', marginBottom:14, textTransform:'uppercase' }}>{mod.key}</div>
            <div style={{ fontFamily:"'Cormorant Garamond', serif", fontSize:20, fontWeight:500, color:hovered===i?'#e8d8a0':'rgba(220,200,150,0.7)', marginBottom:8, letterSpacing:'0.03em', transition:'color 0.25s' }}>{mod.label}</div>
            <div style={{ fontFamily:"'Inter', sans-serif", fontSize:11, letterSpacing:'0.06em', color:'rgba(180,150,90,0.5)', lineHeight:1.5 }}>{mod.sub}</div>
          </div>
        ))}
      </div>
      <div style={{ position:'absolute', bottom:0, left:0, right:0, padding:'14px 48px', borderTop:'1px solid rgba(201,168,76,0.08)', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <span style={{ fontFamily:"'Inter', sans-serif", fontSize:10, letterSpacing:'0.12em', color:'rgba(201,168,76,0.3)', textTransform:'uppercase' }}>Beyond the Obvious.</span>
        <div style={{ display:'flex', gap:20, alignItems:'center' }}>
          <span style={{ width:6, height:6, borderRadius:'50%', background:'#2a6a2a', display:'inline-block' }}/>
          <span style={{ fontFamily:"'Inter', sans-serif", fontSize:10, letterSpacing:'0.1em', color:'rgba(201,168,76,0.3)', textTransform:'uppercase' }}>Systems Nominal</span>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════════
   ROOT APP
═══════════════════════════════════════════════════════════════════ */
export default function App() {
  const [view, setView] = useState<'scene'|'transitioning'|'hub'>('scene')
  const [folderPhase, setFolderPhase] = useState<'idle'|'hover'|'cracking'|'opening'|'open'>('idle')
  const [lightning, setLightning] = useState(false)
  const [headAngle, setHeadAngle] = useState(0)
  const [eyeOffset, setEyeOffset] = useState({ x:0, y:0 })
  const [isBlinking, setIsBlinking] = useState(false)
  const owlRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!owlRef.current) return
      const rect = owlRef.current.getBoundingClientRect()
      const dx = e.clientX - (rect.left + rect.width/2)
      const dy = e.clientY - (rect.top + rect.height/2)
      const dist = Math.sqrt(dx*dx + dy*dy) || 1
      const angle = Math.atan2(dx,-dy)*(180/Math.PI)
      setHeadAngle(Math.max(-15, Math.min(15, angle*0.4)))
      const f = Math.min(1, dist/400)
      setEyeOffset({ x:(dx/dist)*4*f, y:(dy/dist)*4*f })
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  useEffect(() => {
    let tid: ReturnType<typeof setTimeout>
    const blink = () => {
      setIsBlinking(true)
      setTimeout(() => {
        setIsBlinking(false)
        if (Math.random() < 0.25) {
          setTimeout(() => { setIsBlinking(true); setTimeout(() => setIsBlinking(false), 100) }, 200)
        }
      }, 120)
      tid = setTimeout(blink, 2500 + Math.random()*5000)
    }
    tid = setTimeout(blink, 2500 + Math.random()*3000)
    return () => clearTimeout(tid)
  }, [])

  useEffect(() => {
    let tid: ReturnType<typeof setTimeout>
    const flash = () => {
      setLightning(true)
      setTimeout(() => setLightning(false), 400)
      if (Math.random()<0.4) setTimeout(()=>{ setLightning(true); setTimeout(()=>setLightning(false),200) }, 600)
      tid = setTimeout(flash, 7000 + Math.random()*18000)
    }
    tid = setTimeout(flash, 5000 + Math.random()*8000)
    return () => clearTimeout(tid)
  }, [])

  const handleFolderClick = useCallback(() => {
    setFolderPhase('cracking')
    setTimeout(() => setFolderPhase('opening'), 500)
    setTimeout(() => { setFolderPhase('open'); setView('transitioning') }, 1300)
    setTimeout(() => setView('hub'), 1900)
  }, [])

  const handleBack = useCallback(() => { setView('scene'); setFolderPhase('idle') }, [])

  return (
    <div style={{ width:'100vw', height:'100vh', overflow:'hidden', position:'relative', background:'#030201' }}>

      {view !== 'hub' && (
        <div
          className={view==='transitioning' ? 'scene-zooming' : ''}
          style={{ position:'absolute', inset:0, transformOrigin:'50% 60%' }}
        >
          <DeskScene/>

          {/* Rain in window zone */}
          <div style={{ position:'absolute', left:'3.5%', top:'13%', width:'20%', height:'46%', overflow:'hidden', zIndex:4, borderRadius:2 }}>
            <Rain/>
          </div>
          {/* Ambient rain */}
          <div style={{ position:'absolute', inset:0, overflow:'hidden', opacity:0.28, zIndex:4 }}>
            <Rain/>
          </div>

          <Dust/>
          <Lightning active={lightning}/>

          {/* ── NOCTRA BRANDING — white, centered, clear ── */}
          <div style={{
            position:'absolute', left:'50%', top:'55%',
            transform:'translateX(-50%)',
            textAlign:'center', zIndex:8, pointerEvents:'none',
            whiteSpace:'nowrap',
          }}>
            <h1 className="noctra-wordmark" style={{ fontSize:'clamp(32px,5.5vw,78px)', lineHeight:1, marginBottom:'0.12em' }}>
              NOCTRA
            </h1>
            <p className="noctra-tagline" style={{ fontSize:'clamp(11px,1.3vw,20px)' }}>
              Beyond the Obvious.
            </p>
          </div>

          {/* ── Folder — below branding, centered ── */}
          <div style={{ position:'absolute', left:'50%', top:'63%', transform:'translateX(-50%)', zIndex:10 }}>
            <ConfidentialFolder
              phase={folderPhase}
              onHover={h => setFolderPhase(h ? 'hover' : 'idle')}
              onClick={handleFolderClick}
            />
          </div>

          {/* ── Owl ── */}
          <div ref={owlRef} style={{ position:'absolute', right:'11%', bottom:'22%', zIndex:9 }}>
            <Orion headAngle={headAngle} eyeOffset={eyeOffset} isBlinking={isBlinking}/>
          </div>

          {/* Bottom vignette */}
          <div style={{ position:'absolute', bottom:0, left:0, right:0, height:'14%', background:'linear-gradient(to top, rgba(2,1,0,0.7), transparent)', pointerEvents:'none', zIndex:20 }}/>

          <div style={{ position:'absolute', bottom:24, left:32, zIndex:25, fontFamily:"'Inter', sans-serif", fontSize:10, letterSpacing:'0.15em', textTransform:'uppercase', color:'rgba(201,168,76,0.28)' }}>
            Est. 2026 · Intelligence Bureau
          </div>
          <div style={{ position:'absolute', bottom:24, right:32, zIndex:25, fontFamily:"'Cormorant Garamond', serif", fontSize:12, letterSpacing:'0.12em', color:'rgba(201,168,76,0.28)', fontStyle:'italic' }}>
            Open the folder to begin
          </div>
        </div>
      )}

      {view === 'hub' && <InvestigationHub onBack={handleBack}/>}
    </div>
  )
}
