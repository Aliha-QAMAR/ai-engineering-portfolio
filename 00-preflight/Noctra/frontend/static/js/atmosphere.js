let atmosphereIntervals = [];

export function createRain(containerId, config = {}) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const count = config.count || 120;
  
  let html = '';
  for(let i=0; i<count; i++) {
    const left = `${(i * 7.3 + Math.sin(i) * 40) % 100}%`;
    const height = `${14 + (i % 8) * 3}px`;
    const duration = `${0.55 + (i % 9) * 0.08}s`;
    const delay = `${(i * 0.13) % 2}s`;
    const opacity = 0.12 + (i % 5) * 0.055;
    
    html += `<div class="rain-drop" style="left: ${left}; height: ${height}; opacity: ${opacity}; animation-duration: ${duration}; animation-delay: ${delay};"></div>`;
  }
  container.innerHTML = html;
}

export function createWindowRain(containerId) {
  createRain(containerId, { count: 30 }); // fewer drops in window zone
}

export function createDust(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  let html = '';
  for(let i=0; i<28; i++) {
    const left = `${28 + (i * 11.7 + Math.cos(i) * 20) % 45}%`;
    const bottom = `${20 + (i * 8.3) % 50}%`;
    const size = `${1.5 + (i % 4) * 0.8}px`;
    const duration = `${6 + (i % 7) * 2}s`;
    const delay = `${(i * 0.7) % 5}s`;
    
    html += `<div class="dust-mote" style="left: ${left}; bottom: ${bottom}; width: ${size}; height: ${size}; animation-duration: ${duration}; animation-delay: ${delay};"></div>`;
  }
  container.innerHTML = html;
}

export function createLightningOverlay() {
  const overlay = document.createElement('div');
  overlay.className = 'lightning-overlay';
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 500);
}

export function initLightning(callback) {
  const flash = () => {
    if (callback) callback('start');
    createLightningOverlay();
    
    if (Math.random() < 0.4) {
      setTimeout(() => {
        createLightningOverlay();
        if (callback) setTimeout(() => callback('end'), 500);
      }, 600);
    } else {
      if (callback) setTimeout(() => callback('end'), 500);
    }
    
    atmosphereIntervals.push(setTimeout(flash, 7000 + Math.random() * 18000));
  };
  
  atmosphereIntervals.push(setTimeout(flash, 5000 + Math.random() * 8000));
}

export function startAtmosphere() {
  // Can be bound to a global init where elements are already present
  // Dust and rain are often initialized statically via create functions
  initLightning();
}

export function stopAtmosphere() {
  atmosphereIntervals.forEach(clearTimeout);
  atmosphereIntervals = [];
}
