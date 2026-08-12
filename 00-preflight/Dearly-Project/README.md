# Dearly — complete build (Phases 1–4)

## Kaise chalayein (Windows PowerShell)

**Zaroori: isolated virtual environment (venv) use karein — apne global Python mein direct install na karein.**
Global Python mein aksar bohot saari doosri libraries (jaise torch, scipy) pehle se installed hoti hain
jo conflict/hang create kar sakti hain.

1. Python 3.9–3.12 hona chahiye (3.13 pe kabhi kabhi kuch libraries ke naye versions issue karte hain).
2. Project folder mein jaayein aur venv banayein:
   ```powershell
   cd C:\roadmap\projects\dearly-complete\dearly
   python -m venv venv
   venv\Scripts\activate
   ```
   (Prompt ke shuru mein `(venv)` dikhna chahiye — iska matlab isolated environment active hai.)
3. Ab isi (venv) ke andar install karein:
   ```powershell
   pip install -r requirements.txt
   ```
4. `.env` file kholein aur apni OpenAI key paste karein:
   ```
   OPENAI_API_KEY=sk-xxxxxxxx
   ```
5. Server chalayein:
   ```powershell
   python app.py
   ```
6. Browser mein kholein: **http://localhost:3000**

Agli baar bhi chalane se pehle hamesha `venv\Scripts\activate` karein (naya terminal khulte hi).



## Poori app mein kya kaam karta hai

**Navigation & Auth**
- Landing → feather-write "Dearly" animation (bilkul original jaisi)
- "enter the writing room" → Sign up/Sign in (jalte hue letter side se andar aata hai)
- Real accounts — SQLite (`dearly.db`) mein permanently save, password hashed, kabhi delete nahi hota
- Sign in → Dashboard (purana desk scene, same hover/animations)
- Sign-in pe soothing ambient music (generative, on/off toggle)
- Har screen pe "← Back", screens side-by-side slide karte hain

**Letters** (Letters object ya Pen → "A letter")
- Inbox mein do tarah ke letters: pen-pal se aaye hue (phool ke saath) aur anonymous
  bottle-mail (sealed glass bottle mein) — dono database se
- Click karne pe envelope khulta hai / bottle ka cork udta hai, phir letter jale hue
  purane paper ki tarah reveal hota hai
- "Speak aloud" — OpenAI text-to-speech se letter sun sakti hain, speed slider ke saath
- "Reply" — likhein, "Fold and send" pe letter fold hoke gayab hota hai, "Sealed and sent" confirm
- Naya letter likhna: kisi pen pal ko address karein ya khaali chhod dein (anonymous bottle,
  kisi bhi doosre user tak drift karega), mood chips (opening line suggest karte hain),
  mic button se bol kar likhwayein (Whisper), "AI se madad" button

**Journal**
- Naya entry likhein: title, topic, aur visibility (sirf mujhe / mere pen pals / public book)
- "My entries" — apne sab journals
- "The public book" — sab logon ke public journals, har ek pe "Read aloud"
- "Pen pal pages" — sirf apne pen pals ke penpal-visibility journals
- Yahan bhi "AI se madad" available hai

**Pen pals**
- Username search karein, request bhejein
- "Requests" tab mein incoming requests, accept/reject
- "My pen pals" mein accepted list

Sab kuch (accounts, letters, journals, pen-pal connections) `dearly.db` mein user-id
ke against permanently save hota hai — server band/restart karne pe bhi data wahin milega.

## Jo cheezein abhi placeholder hain
- Photo memories aur Timeline abhi bas simple placeholders hain — inko poora banana
  agla step ho sakta hai agar chahiye.
