// Transitions between cinematic screens

export function folderToAccess() {
  const folder = document.querySelector('.folder-container');
  if (folder) {
    folder.classList.add('cracking');
    setTimeout(() => {
      folder.classList.remove('cracking');
      folder.classList.add('opening');
    }, 500);
  }
}

export function accessToAuth(onComplete) {
  const screen = document.getElementById('scene-screen');
  if (screen) {
    screen.classList.add('scene-zooming');
    setTimeout(() => {
      if (onComplete) onComplete();
    }, 1200);
  }
}

export function authToHub(onComplete) {
  const auth = document.getElementById('auth-screen');
  if (auth) {
    auth.style.opacity = '0';
    auth.style.transition = 'opacity 0.8s ease-out';
    setTimeout(() => {
      if (onComplete) onComplete();
    }, 800);
  }
}

export function hubToLanding(onComplete) {
  // Reverse transition back to landing
  if (onComplete) onComplete();
}

export function screenTransition(fromScreenId, toScreenId, type) {
  const fromEl = document.getElementById(fromScreenId);
  const toEl = document.getElementById(toScreenId);
  
  if (!fromEl || !toEl) return;
  
  if (type === 'zoom') {
    fromEl.classList.add('scene-zooming');
    setTimeout(() => {
      fromEl.style.display = 'none';
      fromEl.classList.remove('scene-zooming');
      toEl.style.display = 'block'; // or flex
      toEl.classList.add('hub-entering');
    }, 1200);
  } else if (type === 'fade') {
    fromEl.style.opacity = '0';
    setTimeout(() => {
      fromEl.style.display = 'none';
      toEl.style.display = 'block';
      toEl.style.opacity = '1';
    }, 800);
  }
}
