/*
 * Dearly — front-end behaviour.
 * Speech features use the browser's built-in Web Speech API, so no
 * external AI key or network call is required. On browsers that don't
 * support it (e.g. Firefox for dictation), the buttons degrade
 * gracefully with a short message instead of throwing an error.
 */

const DearlySpeech = (function () {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function speak(text, rate) {

    if (!("speechSynthesis" in window)) {
        alert("Text-to-speech isn't supported in this browser.");
        return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "en-US";
    utterance.pitch = 1.2;
    utterance.volume = 1;
    utterance.rate = rate || 1;

    // Try to use a female voice
    const voices = window.speechSynthesis.getVoices();

    const femaleVoice =
        voices.find(v => v.name.includes("Jenny")) ||
        voices.find(v => v.name.includes("Aria")) ||
        voices.find(v => v.name.includes("Zira")) ||
        voices.find(v => v.name.includes("Sonia")) ||
        voices.find(v => v.name.includes("Female")) ||
        voices.find(v => v.name.includes("Google UK English Female"));

    if (femaleVoice) {
        utterance.voice = femaleVoice;
    }

    setLiyaahSpeaking(true);

    utterance.onend = function () {
        setLiyaahSpeaking(false);
    };

    utterance.onerror = function () {
        setLiyaahSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
}

  function setLiyaahSpeaking(isSpeaking) {
    const el = document.getElementById("liyaah");
    if (!el) return;
    el.classList.toggle("speaking", isSpeaking);
    const bubble = document.getElementById("liyaah-bubble");
    if (!isSpeaking) {
      if (!el.classList.contains("manual-spotlight")) {
        el.classList.remove("liyaah-spotlight");
      }
      if (bubble && !el.classList.contains("liyaah-spotlight")) {
        bubble.textContent = "Your letters have been waiting for you.";
      }
    }
  }

  function attachDictation(button, targetTextarea, statusEl) {
    if (!button || !targetTextarea) return;

    if (!SpeechRecognition) {
      button.addEventListener("click", function () {
        if (statusEl) statusEl.textContent = "Speech recognition isn't supported in this browser — try Chrome or Edge.";
      });
      return;
    }

    let recognizing = false;
    let starting = false;
    let recognition = null;

    function resetButtonState() {
      recognizing = false;
      starting = false;
      button.textContent = "🎙 Speech to text";
      button.classList.remove("btn-listening");
      const liyaah = document.getElementById("liyaah");
      if (liyaah) liyaah.classList.remove("thinking");
    }

    function startRecognition() {
      recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.interimResults = true;
      recognition.continuous = true;

      const baseText = targetTextarea.value && !targetTextarea.value.endsWith(" ")
        ? targetTextarea.value + " "
        : (targetTextarea.value || "");

      recognition.onstart = function () {
        recognizing = true;
        starting = false;
        button.textContent = "⏺ Listening... (click to stop)";
        button.classList.add("btn-listening");
        const liyaah = document.getElementById("liyaah");
        if (liyaah) liyaah.classList.add("thinking");
        if (statusEl) statusEl.textContent = "Liyaah is listening...";
      };

      recognition.onresult = function (event) {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        targetTextarea.value = baseText + transcript;
      };

      recognition.onerror = function (event) {
        resetButtonState();
        if (statusEl) {
          if (event.error === "not-allowed" || event.error === "service-not-allowed") {
            statusEl.textContent = "Microphone access is blocked. Please allow it in your browser's site settings and try again.";
          } else if (event.error === "no-speech") {
            statusEl.textContent = "Didn't catch that — click the mic and try again.";
          } else if (event.error === "network") {
            statusEl.textContent = "Speech recognition needs an internet connection. Please check your connection and try again.";
          } else {
            statusEl.textContent = "Couldn't hear that clearly (" + event.error + "). Try again.";
          }
        }
      };

      recognition.onend = function () {
        resetButtonState();
        if (statusEl) statusEl.textContent = "";
      };

      try {
        recognition.start();
      } catch (err) {
        resetButtonState();
        if (statusEl) statusEl.textContent = "Couldn't start the microphone. Try again in a moment.";
      }
    }

    button.addEventListener("click", function () {
      if (recognizing) {
        if (recognition) recognition.stop();
        return;
      }
      if (starting) return;
      starting = true;

      if (statusEl) statusEl.textContent = "Requesting microphone access...";

      // Explicitly request mic permission first — on many browsers,
      // calling recognition.start() without this ever having been
      // granted fails silently (no audio is ever captured) instead
      // of raising a catchable error.
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(function (stream) {
            // Release the stream immediately; SpeechRecognition opens its own.
            stream.getTracks().forEach(function (track) { track.stop(); });
            startRecognition();
          })
          .catch(function () {
            starting = false;
            if (statusEl) statusEl.textContent = "Microphone access is blocked. Please allow it in your browser's site settings and try again.";
          });
      } else {
        startRecognition();
      }
    });
  }

  return { speak: speak, attachDictation: attachDictation };
})();


const bubble = document.getElementById("liyaah-bubble");
const liyaah = document.getElementById("liyaah");

if (liyaah) {
  liyaah.addEventListener("click", function () {
    const path = window.location.pathname;
    let lines = [
        "Welcome back. Your letters have been waiting for you.",
        "Would you like to write something today?",
        "Every letter tells a story.",
        "Someone may be waiting for your reply.",
        "Take your time. I'm here whenever you need me.",
        "Let's preserve another beautiful memory together."
    ];

    if (path.includes("/desk")) {
      lines = [
        "Welcome back to your writing desk. Shall we write a page or read your mailbox?",
        "Your desk is quiet and peaceful today. Take your time to reflect.",
        "A quiet desk of your own is waiting."
      ];
    } else if (path.includes("/mailbox")) {
      lines = [
        "Let's see who has written to you. Every letter is a keepsake.",
        "A sealed letter holds a little piece of someone's heart.",
        "Who has sent you a letter today?"
      ];
    } else if (path.includes("/letter/")) {
      lines = [
        "A letter from a friend. Shall I read it out loud for you?",
        "This is a keeper. What beautiful words."
      ];
    } else if (path.includes("/send")) {
      lines = [
        "Dip your quill in ink. Who are we writing to today?",
        "Take your time. Let your words flow like ink on parchment.",
        "A letter is a quiet gift."
      ];
    } else if (path.includes("/journals")) {
      lines = [
        "Your journals hold your quietest memories. Let's look over them.",
        "Every page in this journal is a part of you.",
        "Let's preserve another beautiful memory together."
      ];
    } else if (path.includes("/penpals")) {
      lines = [
        "Our circle of writers is growing. Send a warm hello to a friend.",
        "Pen pals share thoughts, not posts. It's a special connection."
      ];
    } else if (path.includes("/settings")) {
      lines = [
        "Let's adjust your desk settings. Tend to your space however you like.",
        "Take your time."
      ];
    } else if (path.includes("/memory/")) {
      lines = [
        "This is a beautiful photograph. Let's reflect on its mood together.",
        "I am looking at this memory with you."
      ];
    }

    const line = lines[Math.floor(Math.random() * lines.length)];

    if (bubble) {
        bubble.textContent = line;
    }

    // Toggle: zoom her in on the spot and keep her text visible until closed again.
    const backdrop = document.getElementById("liyaah-backdrop");
    const isOpen = liyaah.classList.contains("manual-spotlight");

    if (isOpen) {
      liyaah.classList.remove("manual-spotlight", "liyaah-spotlight");
      if (backdrop) backdrop.classList.remove("visible");
      return;
    }

    liyaah.classList.add("liyaah-spotlight", "manual-spotlight");
    if (backdrop) backdrop.classList.add("visible");
    DearlySpeech.speak(line, 1);
  });

  const liyaahBackdrop = document.getElementById("liyaah-backdrop");
  if (liyaahBackdrop) {
    liyaahBackdrop.addEventListener("click", function () {
      liyaah.classList.remove("manual-spotlight", "liyaah-spotlight");
      liyaahBackdrop.classList.remove("visible");
    });
  }
}