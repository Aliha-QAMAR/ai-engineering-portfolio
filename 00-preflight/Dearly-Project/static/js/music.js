(function () {
  let ctx = null;
  let masterGain = null;
  let voices = [];
  let playing = false;
  let started = false;

  const toggleBtn = document.getElementById('musicToggle');
  const icon = document.getElementById('musicIcon');
  const label = document.getElementById('musicLabel');

  // a soft, slow-moving chord — the "soothing" pad
  const notes = [130.81, 164.81, 196.00, 246.94]; // C3, E3, G3, B3 (Cmaj7, warm & calm)

  function buildVoice(freq, ctxRef, destination) {
    const osc = ctxRef.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq;

    const lfo = ctxRef.createOscillator();
    lfo.type = 'sine';
    lfo.frequency.value = 0.06 + Math.random() * 0.05;
    const lfoGain = ctxRef.createGain();
    lfoGain.gain.value = 2.5;
    lfo.connect(lfoGain);
    lfoGain.connect(osc.frequency);

    const voiceGain = ctxRef.createGain();
    voiceGain.gain.value = 0;

    osc.connect(voiceGain);
    voiceGain.connect(destination);

    osc.start();
    lfo.start();

    // slow fade in
    voiceGain.gain.linearRampToValueAtTime(0.05, ctxRef.currentTime + 3);

    return { osc, lfo, gain: voiceGain };
  }

  function ensureContext() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = ctx.createGain();
    masterGain.gain.value = 0.5;

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 900;

    masterGain.connect(filter);
    filter.connect(ctx.destination);

    voices = notes.map(f => buildVoice(f, ctx, masterGain));
  }

  function play() {
    ensureContext();
    if (ctx.state === 'suspended') ctx.resume();
    playing = true;
    updateUI();
  }

  function stop() {
    if (!ctx) { playing = false; updateUI(); return; }
    masterGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.6);
    playing = false;
    updateUI();
  }

  function toggle() {
    if (playing) stop();
    else {
      if (ctx) masterGain.gain.linearRampToValueAtTime(0.5, ctx.currentTime + 0.6);
      play();
    }
  }

  function playOnEnter() {
    if (!started) {
      started = true;
      play();
    }
  }

  function updateUI() {
    icon.textContent = playing ? '🔊' : '🔈';
    label.textContent = playing ? 'Music on' : 'Music off';
  }

  toggleBtn.addEventListener('click', toggle);

  window.DearlyMusic = { play, stop, toggle, playOnEnter };
})();
