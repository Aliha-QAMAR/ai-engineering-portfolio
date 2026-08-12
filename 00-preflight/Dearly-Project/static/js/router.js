(function () {
  const screenOrder = ['landing', 'auth', 'dashboard'];
  const track = document.getElementById('screenTrack');
  const backBtn = document.getElementById('backBtn');
  let historyStack = ['landing'];

  function applyTransform() {
    const current = historyStack[historyStack.length - 1];
    const idx = screenOrder.indexOf(current);
    track.style.transform = `translateX(-${idx * 100}vw)`;
    backBtn.classList.toggle('show', historyStack.length > 1);
  }

  function goTo(name, opts) {
    opts = opts || {};
    if (opts.replace) {
      historyStack[historyStack.length - 1] = name;
    } else if (historyStack[historyStack.length - 1] !== name) {
      historyStack.push(name);
    }
    applyTransform();
    document.dispatchEvent(new CustomEvent('screenchange', { detail: { screen: name } }));
  }

  function back() {
    if (historyStack.length > 1) {
      historyStack.pop();
      applyTransform();
      document.dispatchEvent(new CustomEvent('screenchange', {
        detail: { screen: historyStack[historyStack.length - 1] }
      }));
    }
  }

  function current() {
    return historyStack[historyStack.length - 1];
  }

  backBtn.addEventListener('click', back);
  applyTransform();

  window.Router = { goTo, back, current };
})();
