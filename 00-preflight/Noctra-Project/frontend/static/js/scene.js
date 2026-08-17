const GOLD = '#c9a84c';
const CRIMSON = '#7a1a1a';

function getPersonPortrait(x, y, w, h, pStyle, name, label) {
  const cx = x + w / 2;
  const faceY = y + h * 0.28;
  const r = w * 0.22;

  const skinTones = {
    suit_m: '#9a7858', hat_m: '#8a6848', hair_f: '#b08868',
    glasses_m: '#7a5838', hood_m: '#a08060', bun_f: '#c09878',
    tie_m: '#8a6848', beard_m: '#7a5838',
  };
  const skin = skinTones[pStyle];
  
  let labelG = '';
  if (label) {
    labelG = `
      <line x1="${x}" y1="${y}" x2="${x+w}" y2="${y+h}" stroke="#cc2020" stroke-width="1.5" opacity="0.6"/>
      <line x1="${x+w}" y1="${y}" x2="${x}" y2="${y+h}" stroke="#cc2020" stroke-width="1.5" opacity="0.6"/>
      <text x="${cx}" y="${y+h*0.55}" text-anchor="middle" font-family="'Cinzel', serif" font-size="9" fill="#cc2020" font-weight="700" opacity="0.9">${label}</text>
    `;
  }
  
  let hairG = '';
  if (pStyle === 'hat_m') {
    hairG = `
      <rect x="${cx-r-2}" y="${faceY-r*1.1-8}" width="${r*2+4}" height="8" fill="#3a2810" rx="1"/>
      <rect x="${cx-r*0.8}" y="${faceY-r*1.1-22}" width="${r*1.6}" height="18" fill="#4a3018" rx="2"/>
    `;
  } else if (pStyle === 'hair_f') {
    hairG = `
      <ellipse cx="${cx}" cy="${faceY-r*0.7}" rx="${r*1.1}" ry="${r*0.7}" fill="#2a1808"/>
      <rect x="${cx-r*1.1}" y="${faceY-r*0.5}" width="${r*0.4}" height="${r*1.2}" fill="#2a1808"/>
      <rect x="${cx+r*0.7}" y="${faceY-r*0.5}" width="${r*0.4}" height="${r*1.2}" fill="#2a1808"/>
    `;
  } else if (pStyle === 'bun_f') {
    hairG = `
      <ellipse cx="${cx}" cy="${faceY-r*0.9}" rx="${r*1.05}" ry="${r*0.55}" fill="#1a1008"/>
      <circle cx="${cx+r*0.3}" cy="${faceY-r*1.2}" r="${r*0.3}" fill="#2a1808"/>
    `;
  } else if (pStyle === 'suit_m' || pStyle === 'glasses_m' || pStyle === 'tie_m') {
    hairG = `<ellipse cx="${cx}" cy="${faceY-r*0.95}" rx="${r*0.9}" ry="${r*0.45}" fill="#1a1008"/>`;
  } else if (pStyle === 'beard_m') {
    hairG = `
      <ellipse cx="${cx}" cy="${faceY-r*0.95}" rx="${r*0.9}" ry="${r*0.45}" fill="#3a2810"/>
      <ellipse cx="${cx}" cy="${faceY+r*0.55}" rx="${r*0.75}" ry="${r*0.45}" fill="#3a2810" opacity="0.9"/>
    `;
  } else if (pStyle === 'hood_m') {
    hairG = `<path d="M ${cx-r-4} ${faceY-r*0.3} Q ${cx-r*0.8} ${faceY-r*1.5} ${cx} ${faceY-r*1.3} Q ${cx+r*0.8} ${faceY-r*1.5} ${cx+r+4} ${faceY-r*0.3}" fill="#333"/>`;
  }
  
  let glassesG = '';
  if (pStyle === 'glasses_m') {
    glassesG = `
      <circle cx="${cx-r*0.35}" cy="${faceY-r*0.05}" r="${r*0.22}" fill="none" stroke="#4a3010" stroke-width="1.2"/>
      <circle cx="${cx+r*0.35}" cy="${faceY-r*0.05}" r="${r*0.22}" fill="none" stroke="#4a3010" stroke-width="1.2"/>
      <line x1="${cx-r*0.13}" y1="${faceY-r*0.05}" x2="${cx+r*0.13}" y2="${faceY-r*0.05}" stroke="#4a3010" stroke-width="1.2"/>
    `;
  }
  
  let tieG = '';
  if (pStyle === 'tie_m') {
    tieG = `<path d="M ${cx-3} ${faceY+r*0.85} L ${cx} ${faceY+r*1.1} L ${cx+3} ${faceY+r*0.85} L ${cx} ${faceY+r*0.75} Z" fill="#5a1010" opacity="0.8"/>`;
  }

  return `
    <g>
      <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#c8b898" stroke="#a89878" stroke-width="1.5" rx="1"/>
      <rect x="${x+2}" y="${y+2}" width="${w-4}" height="${h-4}" fill="#b8a880"/>
      <rect x="${x}" y="${y+h-14}" width="${w}" height="14" fill="#a89870"/>
      <text x="${cx}" y="${y+h-4}" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1a08" letter-spacing="0.5">${name}</text>

      <ellipse cx="${cx}" cy="${y+h*0.78}" rx="${w*0.38}" ry="${h*0.28}" fill="${pStyle==='suit_m'||pStyle==='tie_m' ? '#2a2a2a' : pStyle==='hood_m' ? '#333' : '#3a2810'}"/>

      <rect x="${cx-r*0.3}" y="${faceY+r*0.85}" width="${r*0.6}" height="${h*0.12}" fill="${skin}"/>
      <ellipse cx="${cx}" cy="${faceY}" rx="${r}" ry="${r*1.1}" fill="${skin}"/>
      
      ${hairG}
      
      <ellipse cx="${cx-r*0.35}" cy="${faceY-r*0.05}" rx="${r*0.18}" ry="${r*0.12}" fill="#1a1008"/>
      <ellipse cx="${cx+r*0.35}" cy="${faceY-r*0.05}" rx="${r*0.18}" ry="${r*0.12}" fill="#1a1008"/>
      <circle cx="${cx-r*0.35}" cy="${faceY-r*0.05}" r="${r*0.07}" fill="#8a6040" opacity="0.7"/>
      <circle cx="${cx+r*0.35}" cy="${faceY-r*0.05}" r="${r*0.07}" fill="#8a6040" opacity="0.7"/>
      
      ${glassesG}
      
      <ellipse cx="${cx}" cy="${faceY+r*0.2}" rx="${r*0.1}" ry="${r*0.08}" fill="rgba(0,0,0,0.18)"/>
      <path d="M ${cx-r*0.2} ${faceY+r*0.45} Q ${cx} ${faceY+r*0.55} ${cx+r*0.2} ${faceY+r*0.45}" stroke="#5a3828" stroke-width="1" fill="none"/>
      
      ${tieG}
      ${labelG}
      
      <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="rgba(120,80,20,0.22)" rx="1"/>
      <rect x="${x}" y="${y}" width="${w}" height="${h}" fill="rgba(0,0,0,0.08)" rx="1"/>
    </g>
  `;
}

function getInvestigationBoard() {
  const circles = [];
  for(let i=0; i<60; i++) {
    circles.push(`<circle cx="${480+(i*83)%700}" cy="${80+(i*61)%570}" r="${1.5+i%3}" fill="rgba(0,0,0,0.1)" opacity="0.5"/>`);
  }
  const holes = [];
  for(let i=0; i<20; i++) {
    holes.push(`<circle cx="${490+(i*127)%690}" cy="${85+(i*97)%560}" r="1.5" fill="rgba(0,0,0,0.15)"/>`);
  }

  const rects1 = [];
  for(let l=0; l<5; l++) rects1.push(`<rect x="704" y="${120+l*10}" width="${l%2===0 ? 148 : 120}" height="3" rx="1" fill="#5a3810" opacity="0.4"/>`);
  const rects2 = [];
  for(let l=0; l<4; l++) rects2.push(`<rect x="888" y="${112+l*10}" width="${l%2===0 ? 126 : 100}" height="3" rx="1" fill="#5a3810" opacity="0.35"/>`);
  const rects3 = [];
  for(let l=0; l<5; l++) rects3.push(`<rect x="480" y="${472+l*10}" width="${l%2===0 ? 158 : 130}" height="3" rx="1" fill="#5a3810" opacity="0.35"/>`);
  
  const pins = [
    [527, 240, '#8b1a1a'], [636, 235, '#8b6a1a'], [877, 210, '#8b1a1a'],
    [977, 205, '#1a3a8b'], [1054, 78, '#8b1a1a'], [1147, 82, '#8b1a1a'],
    [527, 356, '#2a7a2a'], [736, 265, '#8b1a1a'], [930, 286, '#1a3a8b'],
    [1079, 228, '#8b1a1a'], [1112, 408, '#2a7a2a'], [1057, 350, '#8b1a1a'],
    [844, 530, '#8b6a1a'], [940, 475, '#8b1a1a']
  ].map(([px,py,pc]) => `
    <g>
      <circle cx="${px}" cy="${py}" r="6" fill="${pc}"/>
      <circle cx="${px - 1.5}" cy="${py - 1.5}" r="2.5" fill="rgba(255,255,255,0.3)"/>
    </g>`).join('');

  return `
    <g>
      <!-- Board frame -->
      <rect x="460" y="60" width="740" height="610" rx="4" fill="#2a1808" stroke="#3d2510" stroke-width="8"/>
      <rect x="470" y="70" width="720" height="590" rx="2" fill="#7a5830"/>
      <rect x="470" y="70" width="720" height="590" rx="2" fill="rgba(100,60,20,0.3)"/>
      ${circles.join('')}
      ${holes.join('')}
      
      <!-- Clipping 1 -->
      <g transform="rotate(-2, 510, 95)">
        <rect x="472" y="80" width="200" height="155" fill="#f0e8d0" stroke="#c8b890" stroke-width="0.5"/>
        <rect x="472" y="80" width="200" height="20" fill="#1a1008"/>
        <text x="572" y="93" text-anchor="middle" font-family="'Cinzel', serif" font-size="8" fill="#d4b870" letter-spacing="2">THE HERALD GAZETTE</text>
        <text x="572" y="103" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="6" fill="#9a7850" letter-spacing="1">Est. 1908 · Investigative Edition</text>
        <line x1="472" y1="108" x2="672" y2="108" stroke="#c8b890" stroke-width="0.5"/>
        <text x="572" y="120" text-anchor="middle" font-family="'Cinzel', serif" font-size="10" fill="#1a1008" font-weight="700">CORPORATE FRAUD</text>
        <text x="572" y="132" text-anchor="middle" font-family="'Cinzel', serif" font-size="10" fill="#1a1008" font-weight="700">SCANDAL EXPOSED</text>
        <line x1="480" y1="136" x2="664" y2="136" stroke="#2a1808" stroke-width="0.5"/>
        <text x="572" y="147" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2810">Billions siphoned through offshore shell</text>
        <text x="572" y="157" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2810">corporations linked to Voss Holdings.</text>
        <text x="572" y="169" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2810">Three arrested. CEO whereabouts unknown.</text>
        <text x="572" y="181" text-anchor="middle" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2810">Investigation continues.</text>
        <text x="480" y="226" font-family="'Courier Prime', monospace" font-size="5.5" fill="#8a6840" letter-spacing="0.5">14 OCTOBER 2026 · PAGE 1</text>
        <circle cx="571" cy="80" r="5" fill="#8b1a1a"/>
        <circle cx="571" cy="80" r="3.5" fill="#aa2020"/>
      </g>
      
      <!-- Clipping 2 -->
      <g transform="rotate(1.5, 700, 88)">
        <rect x="696" y="75" width="175" height="128" fill="#ede5c8" stroke="#c8b890" stroke-width="0.5"/>
        <rect x="696" y="75" width="175" height="16" fill="#2a1808"/>
        <text x="783" y="86" text-anchor="middle" font-family="'Cinzel', serif" font-size="7" fill="#c4a860" letter-spacing="1.5">FINANCIAL TIMES</text>
        <text x="783" y="98" text-anchor="middle" font-family="'Cinzel', serif" font-size="8.5" fill="#1a1008" font-weight="700">$2.3B LAUNDERED</text>
        <text x="783" y="110" text-anchor="middle" font-family="'Cinzel', serif" font-size="8.5" fill="#1a1008" font-weight="700">VIA CAYMAN TRUST</text>
        <line x1="702" y1="114" x2="864" y2="114" stroke="#a89870" stroke-width="0.5"/>
        ${rects1.join('')}
        <text x="704" y="198" font-family="'Courier Prime', monospace" font-size="5" fill="#8a6840">Oct 12, 2026</text>
        <circle cx="783" cy="75" r="5" fill="#1a3a8b"/>
        <circle cx="783" cy="75" r="3" fill="#2a4a9b"/>
      </g>
      
      <!-- Clipping 3 -->
      <g transform="rotate(-1, 890, 80)">
        <rect x="880" y="70" width="150" height="110" fill="#f5edd5" stroke="#c8b890" stroke-width="0.5"/>
        <rect x="880" y="70" width="150" height="14" fill="#3a1808"/>
        <text x="955" y="80" text-anchor="middle" font-family="'Cinzel', serif" font-size="6.5" fill="#c4a860" letter-spacing="1">CITY TRIBUNE</text>
        <text x="955" y="93" text-anchor="middle" font-family="'Cinzel', serif" font-size="8" fill="#1a1008" font-weight="700">SHELL CORPS</text>
        <text x="955" y="104" text-anchor="middle" font-family="'Cinzel', serif" font-size="8" fill="#1a1008" font-weight="700">TRACED BACK</text>
        ${rects2.join('')}
        <text x="888" y="175" font-family="'Courier Prime', monospace" font-size="5" fill="#8a6840">Sept 28, 2026</text>
        <circle cx="954" cy="70" r="4.5" fill="#2a7a2a"/>
        <circle cx="954" cy="70" r="3" fill="#3a8a3a"/>
      </g>
      
      <!-- Clipping 4 -->
      <g transform="rotate(2, 490, 430)">
        <rect x="472" y="430" width="180" height="130" fill="#f0e8cc" stroke="#c8b890" stroke-width="0.5"/>
        <rect x="472" y="430" width="180" height="14" fill="#2a1808"/>
        <text x="562" y="440" text-anchor="middle" font-family="'Cinzel', serif" font-size="6.5" fill="#c4a860" letter-spacing="1">INVESTIGATIVE POST</text>
        <text x="562" y="452" text-anchor="middle" font-family="'Cinzel', serif" font-size="8" fill="#1a1008" font-weight="700">CEO MARCUS VOSS</text>
        <text x="562" y="463" text-anchor="middle" font-family="'Cinzel', serif" font-size="8" fill="#1a1008" font-weight="700">MISSING SINCE OCT 14</text>
        ${rects3.join('')}
        <circle cx="562" cy="430" r="5" fill="#8b6a1a"/>
        <circle cx="562" cy="430" r="3.5" fill="#aa8020"/>
      </g>

      <!-- Notes -->
      <g transform="rotate(-3, 700, 275)">
        <rect x="684" y="265" width="105" height="90" fill="#e8dc6a" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>
        <line x1="692" y1="282" x2="780" y2="282" stroke="rgba(0,0,0,0.15)" stroke-width="0.7"/>
        <line x1="692" y1="294" x2="780" y2="294" stroke="rgba(0,0,0,0.15)" stroke-width="0.7"/>
        <line x1="692" y1="306" x2="780" y2="306" stroke="rgba(0,0,0,0.15)" stroke-width="0.7"/>
        <line x1="692" y1="318" x2="780" y2="318" stroke="rgba(0,0,0,0.15)" stroke-width="0.7"/>
        <text x="696" y="279" font-family="'Courier Prime', monospace" font-size="8" fill="#1a1008" font-weight="700">FOLLOW THE</text>
        <text x="696" y="291" font-family="'Courier Prime', monospace" font-size="8" fill="#1a1008" font-weight="700">MONEY →</text>
        <text x="696" y="305" font-family="'Courier Prime', monospace" font-size="7" fill="#3a2010">Voss → shell co.</text>
        <text x="696" y="317" font-family="'Courier Prime', monospace" font-size="7" fill="#3a2010">→ Cayman #44</text>
        <text x="696" y="347" font-family="'Courier Prime', monospace" font-size="6" fill="#8a6840" font-style="italic">check bank rec.</text>
        <circle cx="736" cy="265" r="4.5" fill="#8b1a1a"/>
      </g>
      
      <g transform="rotate(2, 890, 300)">
        <rect x="874" y="286" width="112" height="95" fill="#e0e870" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>
        <text x="880" y="303" font-family="'Courier Prime', monospace" font-size="8" fill="#1a1008" font-weight="700">ALIBI CHECK</text>
        <line x1="880" y1="308" x2="976" y2="308" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="880" y="320" font-family="'Courier Prime', monospace" font-size="7.5" fill="#2a1008">Hotel Meridian</text>
        <text x="880" y="331" font-family="'Courier Prime', monospace" font-size="7.5" fill="#2a1008">11PM — Oct 13</text>
        <line x1="880" y1="335" x2="976" y2="335" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="880" y="347" font-family="'Courier Prime', monospace" font-size="7" fill="#8a1a1a">UNVERIFIED ✗</text>
        <line x1="880" y1="351" x2="976" y2="351" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="880" y="366" font-family="'Courier Prime', monospace" font-size="6.5" fill="#5a3010" font-style="italic">3 witnesses</text>
        <text x="880" y="375" font-family="'Courier Prime', monospace" font-size="6.5" fill="#5a3010" font-style="italic">contradicted</text>
        <circle cx="930" cy="286" r="4.5" fill="#1a3a8b"/>
      </g>

      <g transform="rotate(-1.5, 1040, 240)">
        <rect x="1025" y="228" width="108" height="88" fill="#e8dc6a" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>
        <text x="1031" y="244" font-family="'Courier Prime', monospace" font-size="7.5" fill="#8b1a1a" font-weight="700">⚠ WIRE TRANSFER</text>
        <line x1="1031" y1="249" x2="1123" y2="249" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="1031" y="261" font-family="'Courier Prime', monospace" font-size="8" fill="#1a1008">$2,340,000</text>
        <text x="1031" y="273" font-family="'Courier Prime', monospace" font-size="7" fill="#3a2010">Oct 10 · 02:14 AM</text>
        <line x1="1031" y1="278" x2="1123" y2="278" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="1031" y="290" font-family="'Courier Prime', monospace" font-size="7" fill="#3a2010">Cayman Natl. Bk</text>
        <text x="1031" y="302" font-family="'Courier Prime', monospace" font-size="7" fill="#3a2010">Acct: ****7294</text>
        <circle cx="1079" cy="228" r="4.5" fill="#8b1a1a"/>
      </g>
      
      <g transform="rotate(1, 1080, 420)">
        <rect x="1065" y="408" width="95" height="80" fill="#f0e890" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>
        <text x="1071" y="423" font-family="'Courier Prime', monospace" font-size="7.5" fill="#1a1008" font-weight="700">ACCOMPLICE?</text>
        <line x1="1071" y1="428" x2="1150" y2="428" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="1071" y="440" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">R. Hartmann</text>
        <text x="1071" y="451" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">CFO · Voss Holdings</text>
        <line x1="1071" y1="456" x2="1150" y2="456" stroke="rgba(0,0,0,0.12)" stroke-width="0.7"/>
        <text x="1071" y="468" font-family="'Courier Prime', monospace" font-size="6.5" fill="#8a1a1a">signed transfer</text>
        <text x="1071" y="479" font-family="'Courier Prime', monospace" font-size="6.5" fill="#8a1a1a">documents → ?</text>
        <circle cx="1112" cy="408" r="4.5" fill="#2a7a2a"/>
      </g>
      
      <g transform="rotate(-2, 700, 490)">
        <rect x="680" y="475" width="115" height="85" fill="#e8d870" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>
        <text x="686" y="491" font-family="'Courier Prime', monospace" font-size="7.5" fill="#1a1008" font-weight="700">SHELL CORPS:</text>
        <text x="686" y="503" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">• NovexTrade Ltd</text>
        <text x="686" y="514" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">• BlueHaven Corp</text>
        <text x="686" y="525" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">• ArcLight Holdings</text>
        <text x="686" y="536" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1008">• Meridian Trust</text>
        <text x="686" y="549" font-family="'Courier Prime', monospace" font-size="6.5" fill="#8a1a1a" font-style="italic">all registered 2024</text>
        <circle cx="737" cy="475" r="4.5" fill="#8b6a1a"/>
      </g>

      <!-- Portraits -->
      ${getPersonPortrait(472, 240, 110, 108, 'suit_m', 'MARCUS VOSS', 'SUSPECT #1')}
      ${getPersonPortrait(590, 235, 92, 98, 'glasses_m', 'DR. R. HARTMANN')}
      ${getPersonPortrait(1010, 78, 88, 105, 'hair_f', 'S. CHEN')}
      ${getPersonPortrait(1106, 82, 82, 100, 'tie_m', 'P. LORENZ', 'FLED')}
      
      ${getPersonPortrait(830, 210, 95, 105, 'hat_m', 'UNKNOWN #3')}
      ${getPersonPortrait(933, 205, 88, 100, 'bun_f', 'L. MOREIRA')}
      ${getPersonPortrait(472, 356, 88, 100, 'hood_m', 'UNKNOWN #7')}
      ${getPersonPortrait(1010, 350, 95, 105, 'beard_m', 'T. BLACKWOOD')}
      ${getPersonPortrait(1113, 355, 80, 95, 'suit_m', 'ANALYST X')}
      
      ${getPersonPortrait(800, 480, 88, 100, 'tie_m', 'J. WHITMORE')}
      ${getPersonPortrait(896, 475, 82, 95, 'glasses_m', 'INFORMANT A')}
      
      <!-- Red strings -->
      <line x1="527" y1="240" x2="636" y2="235" stroke="#dd1010" stroke-width="2.5" opacity="0.9"/>
      <line x1="527" y1="240" x2="877" y2="210" stroke="#cc1818" stroke-width="2.2" opacity="0.85"/>
      <line x1="636" y1="235" x2="877" y2="210" stroke="#cc1818" stroke-width="2" opacity="0.8"/>
      <line x1="877" y1="210" x2="977" y2="205" stroke="#dd1010" stroke-width="2.3" opacity="0.88"/>
      <line x1="877" y1="210" x2="1054" y2="78" stroke="#cc1818" stroke-width="2" opacity="0.82"/>
      <line x1="977" y1="205" x2="1054" y2="78" stroke="#dd1010" stroke-width="2.2" opacity="0.87"/>
      <line x1="1054" y1="78" x2="1147" y2="82" stroke="#cc1818" stroke-width="2.5" opacity="0.9"/>

      <line x1="527" y1="356" x2="527" y2="240" stroke="#bb0a0a" stroke-width="2" opacity="0.8"/>
      <line x1="527" y1="356" x2="636" y2="235" stroke="#cc1818" stroke-width="2" opacity="0.75"/>
      <line x1="877" y1="315" x2="736" y2="265" stroke="#dd1010" stroke-width="2.2" opacity="0.85"/>
      <line x1="877" y1="315" x2="1079" y2="228" stroke="#cc1818" stroke-width="2" opacity="0.8"/>
      <line x1="977" y1="205" x2="1112" y2="408" stroke="#dd1010" stroke-width="2" opacity="0.78"/>
      <line x1="1147" y1="82" x2="1057" y2="350" stroke="#cc1818" stroke-width="2.2" opacity="0.82"/>
      <line x1="844" y1="530" x2="736" y2="475" stroke="#dd1010" stroke-width="2" opacity="0.8"/>
      <line x1="844" y1="530" x2="940" y2="475" stroke="#cc1818" stroke-width="2" opacity="0.75"/>
      <line x1="527" y1="356" x2="737" y2="475" stroke="#dd1010" stroke-width="2.2" opacity="0.85"/>
      <line x1="1057" y1="350" x2="940" y2="475" stroke="#cc1818" stroke-width="2" opacity="0.8"/>
      <line x1="736" y1="265" x2="527" y2="240" stroke="#ee1212" stroke-width="2.5" opacity="0.88"/>
      <line x1="930" y1="286" x2="977" y2="205" stroke="#dd1010" stroke-width="2.2" opacity="0.85"/>
      <line x1="930" y1="286" x2="844" y2="530" stroke="#cc1818" stroke-width="2" opacity="0.75"/>

      <line x1="737" y1="315" x2="736" y2="475" stroke="#dd1010" stroke-width="1.8" opacity="0.75"/>
      <line x1="1112" y1="408" x2="1057" y2="350" stroke="#cc1818" stroke-width="2" opacity="0.82"/>
      <line x1="1079" y1="228" x2="1147" y2="82" stroke="#dd1818" stroke-width="2.3" opacity="0.88"/>
      
      ${pins}
    </g>
  `;
}

export function createDeskScene(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const panels = [0,1,2,3].map(i => `<rect x="${60+i*460}" y="180" width="400" height="480" fill="none" stroke="rgba(60,35,15,0.2)" stroke-width="2" rx="3"/>`).join('');
  const deskLines = [0,1,2,3,4,5,6,7].map(i => `<path d="M ${-80+i*80} 680 L ${-180+i*100} 1080" stroke="rgba(0,0,0,0.08)" stroke-width="${1+i%3}"/>`).join('');
  const bookLinesL = [0,1,2,3,4,5,6].map(i => `<line x1="-120" y1="${-70+i*13}" x2="-12" y2="${-70+i*13}" stroke="rgba(180,150,100,0.28)" stroke-width="0.7"/>`).join('');
  const bookLinesR = [0,1,2,3,4,5,6].map(i => `<line x1="8" y1="${-70+i*13}" x2="125" y2="${-70+i*13}" stroke="rgba(180,150,100,0.28)" stroke-width="0.7"/>`).join('');
  
  const casePapers = [[1280, 702, -5, 'EXHIBIT A — BANK RECORDS', 'Account: ****7294 · Balance: $0'], [1400, 695, 4, 'WIRE TRANSFER RECEIPT', 'Ref: CAY-2026-10-0094'], [1500, 708, -2, 'SURVEILLANCE REPORT', 'Subject: Voss · Hotel Meridian']].map(([x,y,r,title,sub],i) => `
    <g transform="translate(${x},${y}) rotate(${r})">
      <rect x="-72" y="-55" width="144" height="115" rx="2" fill="#f0e8d5" opacity="${0.88-Number(i)*0.06}"/>
      <rect x="-72" y="-55" width="144" height="14" fill="#e0d8c0" opacity="0.8"/>
      <text x="0" y="-44" text-anchor="middle" font-family="'Cinzel', serif" font-size="7" fill="#3a2010" letter-spacing="0.5">${title}</text>
      <line x1="-62" y1="-38" x2="62" y2="-38" stroke="rgba(0,0,0,0.1)" stroke-width="0.7"/>
      <text x="-60" y="-26" font-family="'Courier Prime', monospace" font-size="6.5" fill="#5a3810">${sub}</text>
      ${[0,1,2,3,4].map(l=>`<line x1="-60" y1="${-15+l*13}" x2="60" y2="${-15+l*13}" stroke="rgba(0,0,0,0.1)" stroke-width="0.7"/>`).join('')}
      <rect x="10" y="20" width="50" height="18" rx="2" fill="none" stroke="#8b1a1a" stroke-width="1.5" opacity="0.5" transform="rotate(-8,35,29)"/>
      <text x="34" y="32" text-anchor="middle" font-family="'Cinzel', serif" font-size="6" fill="#8b1a1a" opacity="0.6" transform="rotate(-8,34,32)">CLASSIFIED</text>
    </g>
  `).join('');

  container.innerHTML = `
    <svg viewBox="0 0 1920 1080" style="position: absolute; inset: 0; width: 100%; height: 100%;" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="roomBg" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#030201"/>
          <stop offset="40%" stop-color="#080503"/>
          <stop offset="80%" stop-color="#110904"/>
          <stop offset="100%" stop-color="#1e1208"/>
        </linearGradient>
        <linearGradient id="deskSurface" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#2a1a08"/>
          <stop offset="15%" stop-color="#3d2610"/>
          <stop offset="35%" stop-color="#5c3a18"/>
          <stop offset="50%" stop-color="#6a4420"/>
          <stop offset="65%" stop-color="#5c3a18"/>
          <stop offset="85%" stop-color="#3d2610"/>
          <stop offset="100%" stop-color="#2a1a08"/>
        </linearGradient>
        <linearGradient id="deskFront" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#3d2610"/>
          <stop offset="100%" stop-color="#1e1208"/>
        </linearGradient>
        <radialGradient id="lampCone" cx="50%" cy="0%" r="100%">
          <stop offset="0%" stop-color="rgba(220,160,60,0.28)"/>
          <stop offset="40%" stop-color="rgba(200,130,40,0.12)"/>
          <stop offset="80%" stop-color="rgba(180,110,20,0.04)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="lampGlow" cx="50%" cy="0%" r="80%">
          <stop offset="0%" stop-color="rgba(255,200,80,0.55)"/>
          <stop offset="30%" stop-color="rgba(230,160,60,0.2)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="deskLampPool" cx="50%" cy="0%" r="60%">
          <stop offset="0%" stop-color="rgba(220,150,50,0.22)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="moonGlow" cx="50%" cy="30%" r="70%">
          <stop offset="0%" stop-color="rgba(140,170,210,0.18)"/>
          <stop offset="100%" stop-color="transparent"/>
        </radialGradient>
        <radialGradient id="vignette" cx="50%" cy="45%" r="70%">
          <stop offset="0%" stop-color="transparent"/>
          <stop offset="65%" stop-color="rgba(2,1,0,0.4)"/>
          <stop offset="100%" stop-color="rgba(2,1,0,0.88)"/>
        </radialGradient>
        <linearGradient id="book1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#3a2010"/><stop offset="100%" stop-color="#2a1408"/>
        </linearGradient>
        <linearGradient id="book2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#4a1818"/><stop offset="100%" stop-color="#350f0f"/>
        </linearGradient>
        <linearGradient id="book3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#1a2a1a"/><stop offset="100%" stop-color="#101a10"/>
        </linearGradient>
      </defs>

      <rect x="0" y="0" width="1920" height="1080" fill="url(#roomBg)"/>
      <rect x="0" y="0" width="1920" height="220" fill="#020100"/>

      ${panels}

      <rect x="60" y="130" width="340" height="460" fill="#0a0806" rx="4"/>
      <rect x="72" y="145" width="316" height="432" fill="#050302" stroke="#3a2510" stroke-width="10" rx="2"/>
      <rect x="77" y="150" width="306" height="422" fill="#0d1520"/>
      <rect x="77" y="150" width="306" height="422" fill="url(#moonGlow)"/>
      <line x1="230" y1="150" x2="230" y2="572" stroke="#3a2510" stroke-width="8"/>
      <line x1="77" y1="360" x2="383" y2="360" stroke="#3a2510" stroke-width="8"/>
      <line x1="154" y1="150" x2="154" y2="360" stroke="#2a1808" stroke-width="4"/>
      <line x1="307" y1="150" x2="307" y2="360" stroke="#2a1808" stroke-width="4"/>
      <line x1="77" y1="254" x2="383" y2="254" stroke="#2a1808" stroke-width="4"/>
      <line x1="77" y1="468" x2="383" y2="468" stroke="#2a1808" stroke-width="4"/>
      <rect x="60" y="575" width="360" height="22" fill="#3a2510"/>
      
      <path d="M 60 130 C 52 200, 48 300, 52 440 C 55 520, 50 560, 54 590" stroke="#2a1808" stroke-width="48" stroke-linecap="butt" fill="none"/>
      <path d="M 60 130 C 52 200, 48 300, 52 440 C 55 520, 50 560, 54 590" stroke="#1e1208" stroke-width="32" stroke-linecap="butt" fill="none"/>
      <path d="M 400 130 C 408 200, 412 300, 408 440 C 405 520, 410 560, 406 590" stroke="#2a1808" stroke-width="48" stroke-linecap="butt" fill="none"/>
      <path d="M 400 130 C 408 200, 412 300, 408 440 C 405 520, 410 560, 406 590" stroke="#1e1208" stroke-width="32" stroke-linecap="butt" fill="none"/>
      <rect x="42" y="120" width="380" height="16" rx="8" fill="#3a2510"/>
      <circle cx="42" cy="128" r="9" fill="${GOLD}"/>
      <circle cx="422" cy="128" r="9" fill="${GOLD}"/>

      ${getInvestigationBoard()}

      <g transform="translate(830, 55)">
        <rect x="-6" y="0" width="12" height="30" rx="3" fill="#1a1008"/>
        <path d="M -35 30 L 35 30 L 50 75 L -50 75 Z" fill="#2a1a08"/>
        <ellipse cx="0" cy="30" rx="18" ry="5" fill="#3a2510"/>
        <ellipse cx="0" cy="75" rx="38" ry="6" fill="#1a1008"/>
        <ellipse cx="0" cy="50" rx="15" ry="7" fill="rgba(255,210,90,0.35)" class="lamp-glow"/>
      </g>

      <path d="M 960 0 Q 940 30, 935 60 Q 928 100, 930 130" stroke="#1a1008" stroke-width="6" fill="none" stroke-linecap="round"/>
      <path d="M 890 130 L 970 130 L 1010 175 L 850 175 Z" fill="#2a1a08"/>
      <path d="M 895 133 L 965 133 L 1003 172 L 857 172 Z" fill="#1a1008"/>
      <ellipse cx="930" cy="130" rx="40" ry="8" fill="#3a2510"/>
      <ellipse cx="930" cy="175" rx="80" ry="10" fill="#1e1208"/>
      <ellipse cx="930" cy="145" rx="25" ry="12" fill="rgba(255,220,100,0.6)" class="lamp-glow"/>
      <path d="M 850 175 L 500 680 L 1360 680 L 1010 175 Z" fill="url(#lampCone)" class="lamp-glow"/>
      <path d="M 870 175 L 680 580 L 1180 580 L 990 175 Z" fill="url(#lampGlow)" class="lamp-glow-2" opacity="0.7"/>
      <ellipse cx="930" cy="730" rx="420" ry="80" fill="url(#deskLampPool)" class="lamp-glow"/>

      <path d="M -100 680 L 2020 680 L 2200 1080 L -280 1080 Z" fill="url(#deskSurface)"/>
      ${deskLines}
      <rect x="-100" y="680" width="2220" height="30" fill="#3d2410"/>
      <path d="M -100 710 L 2020 710 L 2200 1080 L -280 1080 Z" fill="url(#deskFront)" opacity="0.7"/>
      <line x1="-100" y1="680" x2="2020" y2="680" stroke="rgba(200,140,60,0.12)" stroke-width="2"/>

      <g transform="translate(185, 622)">
        <rect x="-55" y="-8" width="130" height="22" rx="2" fill="url(#book2)"/>
        <rect x="-60" y="-32" width="120" height="24" rx="2" fill="url(#book1)"/>
        <line x1="-55" y1="-18" x2="55" y2="-18" stroke="rgba(255,255,255,0.06)" stroke-width="0.5"/>
        <rect x="-52" y="-58" width="115" height="26" rx="2" fill="url(#book3)"/>
        <line x1="-32" y1="-46" x2="46" y2="-46" stroke="rgba(200,160,60,0.4)" stroke-width="1.5"/>
        <line x1="-32" y1="-42" x2="24" y2="-42" stroke="rgba(200,160,60,0.25)" stroke-width="1"/>
        <rect x="-55" y="-60" width="6" height="74" fill="rgba(0,0,0,0.3)"/>
      </g>

      <g transform="translate(340, 668) rotate(-4)">
        <ellipse cx="0" cy="22" rx="130" ry="18" fill="rgba(0,0,0,0.4)"/>
        <rect x="-130" y="-88" width="265" height="112" rx="4" fill="#1e1208"/>
        <path d="M -128 -86 L -5 -86 L -5 20 L -128 20 Z" fill="#f2ead8"/>
        <path d="M -3 -86 L 133 -86 L 133 20 L -3 20 Z" fill="#ede5ce"/>
        <rect x="-6" y="-86" width="12" height="106" fill="#1e1208"/>
        ${bookLinesL}
        ${bookLinesR}
        <text x="-118" y="-74" font-family="'Courier Prime', monospace" font-size="7.5" fill="#2a1808" font-weight="700">CASE FILE: NOC-2026</text>
        <text x="-118" y="-61" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Subject: Voss Holdings</text>
        <text x="-118" y="-48" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Fraud scale: $2.3B est.</text>
        <text x="-118" y="-35" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Networks: 14 identified</text>
        <text x="-118" y="-22" font-family="'Courier Prime', monospace" font-size="6.5" fill="#8a1a1a">Status: ACTIVE ⚠</text>
        <text x="-118" y="-9" font-family="'Courier Prime', monospace" font-size="6" fill="#5a3810" font-style="italic">Lead: Marcus Voss</text>
        <text x="-118" y="4" font-family="'Courier Prime', monospace" font-size="6" fill="#5a3810" font-style="italic">Accomplice: R. Hartmann</text>
        
        <text x="10" y="-74" font-family="'Courier Prime', monospace" font-size="7" fill="#2a1808" font-weight="700">TIMELINE</text>
        <text x="10" y="-61" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Sep 15 — First transfer</text>
        <text x="10" y="-48" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Oct 10 — $2.3M wired</text>
        <text x="10" y="-35" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Oct 12 — Voss spotted</text>
        <text x="10" y="-22" font-family="'Courier Prime', monospace" font-size="6.5" fill="#3a2010">Oct 13 — Hotel mtg</text>
        <text x="10" y="-9" font-family="'Courier Prime', monospace" font-size="6.5" fill="#8a1a1a">Oct 14 — DISAPPEARS</text>
        <text x="10" y="6" font-family="'Courier Prime', monospace" font-size="6" fill="#5a3810" font-style="italic">Oct 16 — Case opened</text>
        
        <g transform="rotate(12) translate(60, -60)">
          <rect x="0" y="-3" width="88" height="7" rx="3.5" fill="#1a1008"/>
          <rect x="72" y="-3" width="12" height="7" rx="1" fill="${GOLD}"/>
          <rect x="84" y="-4" width="14" height="9" rx="3" fill="#2a1a08"/>
          <path d="M 0 -1 L -10 0 L 0 1 Z" fill="#6a5020"/>
          <line x1="-10" y1="0" x2="0" y2="0" stroke="${GOLD}" stroke-width="0.8"/>
        </g>
        <rect x="-14" y="-88" width="10" height="38" fill="#8b1a1a"/>
        <path d="M -14 -50 L -9 -40 L -4 -50" fill="#8b1a1a"/>
      </g>

      <g transform="translate(1380, 660) rotate(-20)">
        <circle cx="0" cy="0" r="40" fill="none" stroke="#8a6830" stroke-width="6"/>
        <circle cx="0" cy="0" r="33" fill="rgba(120,160,180,0.06)" stroke="#7a5820" stroke-width="2"/>
        <rect x="29" y="-5" width="62" height="10" rx="5" fill="#5a3810"/>
        <rect x="31" y="-3" width="58" height="3" fill="rgba(255,255,255,0.06)"/>
        <ellipse cx="-13" cy="-13" rx="11" ry="6" fill="rgba(180,220,255,0.1)" transform="rotate(-20)"/>
        <circle cx="0" cy="0" r="40" fill="none" stroke="#a08040" stroke-width="1" opacity="0.5"/>
      </g>

      <g transform="translate(1580, 672) rotate(6)">
        <ellipse cx="0" cy="35" rx="100" ry="12" fill="rgba(0,0,0,0.4)"/>
        <rect x="-100" y="-60" width="200" height="100" rx="3" fill="#e8dcc0"/>
        <rect x="-100" y="-60" width="200" height="100" rx="3" fill="none" stroke="#c8b890" stroke-width="1.5"/>
        <path d="M -100 -60 L 0 -12 L 100 -60" stroke="#c8b890" stroke-width="1" fill="none"/>
        <path d="M -100 40 L 0 -12 L 100 40" stroke="rgba(0,0,0,0.08)" stroke-width="1" fill="rgba(0,0,0,0.03)"/>
        <circle cx="0" cy="-10" r="20" fill="#7a1818"/>
        <circle cx="0" cy="-10" r="17" fill="#8b1a1a"/>
        <text x="0" y="-5" text-anchor="middle" font-family="'Cinzel', serif" font-size="13" font-weight="600" fill="rgba(240,220,180,0.75)">N</text>
      </g>

      ${casePapers}

      <g transform="translate(1720, 655)">
        <ellipse cx="0" cy="18" rx="26" ry="10" fill="rgba(0,0,0,0.5)"/>
        <rect x="-22" y="-28" width="44" height="46" rx="16" fill="#0d0a06"/>
        <rect x="-18" y="-24" width="36" height="20" rx="12" fill="#1a1510"/>
        <ellipse cx="0" cy="-24" rx="18" ry="6" fill="#050302"/>
        <ellipse cx="0" cy="-26" rx="20" ry="5" fill="#2a1e0a" stroke="#4a3010" stroke-width="1"/>
        <rect x="-22" y="-2" width="44" height="6" rx="2" fill="#6a4810"/>
      </g>

      <g transform="translate(1820, 624)">
        <circle cx="0" cy="0" r="42" fill="#1e1208" stroke="#8a6820" stroke-width="4"/>
        <circle cx="0" cy="0" r="36" fill="#0a0805"/>
        <circle cx="0" cy="0" r="35" fill="none" stroke="#6a5010" stroke-width="1" stroke-dasharray="2,10"/>
        <line x1="0" y1="0" x2="0" y2="-22" stroke="${GOLD}" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="0" y1="0" x2="16" y2="-8" stroke="${GOLD}" stroke-width="1.5" stroke-linecap="round" class="pendulum"/>
        <circle cx="0" cy="0" r="3" fill="${GOLD}"/>
        <circle cx="22" cy="60" r="10" fill="#3a2810" stroke="#8a6820" stroke-width="2"/>
        <line x1="0" y1="0" x2="22" y2="50" stroke="#5a3818" stroke-width="1.5" class="pendulum"/>
      </g>

      <rect x="0" y="0" width="1920" height="1080" fill="url(#vignette)" pointer-events="none"/>
      <rect x="0" y="1050" width="1920" height="30" fill="rgba(0,0,0,0.6)"/>
    </svg>
  `;
}
