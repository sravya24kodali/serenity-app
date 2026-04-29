// =====================================================
//  Serenity — script.js  (FINAL WORKING VERSION)
// =====================================================

const API_BASE = 'http://localhost:5000/api';

let currentUser         = null;
let currentConvId       = null;
let userPreferences     = { name: 'Friend', preferred_tone: 'warm' };
let isTyping            = false;
let conversationHistory = [];
let crisisVisible       = false;
let _loadTimer          = null;

// --------------------------------------------------
//  INIT USER
// --------------------------------------------------
function initializeUser() {
  let uid = localStorage.getItem('serenity_user_id');
  if (!uid) {
    uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('serenity_user_id', uid);
  }
  currentUser = uid;

  const savedName  = localStorage.getItem('serenity_user_name');
  if (savedName) userPreferences.name = savedName;

  const savedPrefs = localStorage.getItem('serenity_user_prefs');
  if (savedPrefs) {
    try { userPreferences = { ...userPreferences, ...JSON.parse(savedPrefs) }; } catch(e) {}
  }

  if (localStorage.getItem('serenity_accepted') === 'true') {
    const overlay = document.getElementById('modalOverlay');
    if (overlay) overlay.remove();
  }
}

// --------------------------------------------------
//  MODAL
// --------------------------------------------------
function closeModal() {
  const overlay = document.getElementById('modalOverlay');
  if (overlay) {
    overlay.style.opacity    = '0';
    overlay.style.transition = 'opacity 0.3s';
    setTimeout(() => overlay.remove(), 300);
  }
  localStorage.setItem('serenity_accepted', 'true');
}

// --------------------------------------------------
//  SETTINGS
// --------------------------------------------------
function openProfileSettings() {
  const box = document.createElement('div');
  box.className = 'settings-modal';
  box.id = 'settingsModal';
  box.innerHTML = `
    <div class="settings-box">
      <h3>Your Preferences</h3>
      <label>YOUR NAME</label>
      <input type="text" id="setPrefName" value="${userPreferences.name}" placeholder="What should Serenity call you?">
      <label>PREFERRED TONE</label>
      <select id="setPrefTone">
        <option value="warm"      ${userPreferences.preferred_tone==='warm'     ?'selected':''}>Warm & Nurturing</option>
        <option value="casual"    ${userPreferences.preferred_tone==='casual'   ?'selected':''}>Casual & Friendly</option>
        <option value="clinical"  ${userPreferences.preferred_tone==='clinical' ?'selected':''}>Clear & Clinical</option>
        <option value="spiritual" ${userPreferences.preferred_tone==='spiritual'?'selected':''}>Spiritual & Reflective</option>
      </select>
      <div class="settings-actions">
        <button type="button" class="btn-secondary" onclick="document.getElementById('settingsModal').remove()">Cancel</button>
        <button type="button" class="btn-primary" onclick="saveSettings()">Save</button>
      </div>
    </div>
  `;
  document.body.appendChild(box);
}

function saveSettings() {
  const name = document.getElementById('setPrefName').value.trim() || 'Friend';
  const tone = document.getElementById('setPrefTone').value;
  userPreferences.name           = name;
  userPreferences.preferred_tone = tone;
  localStorage.setItem('serenity_user_name',  name);
  localStorage.setItem('serenity_user_prefs', JSON.stringify(userPreferences));
  fetch(`${API_BASE}/user-preferences/${currentUser}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ name, preferred_tone: tone })
  }).catch(() => {});
  document.getElementById('settingsModal').remove();
}

// --------------------------------------------------
//  MOOD
// --------------------------------------------------
function selectMood(btn, emoji, label) {
  document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  doSend(`I'm feeling ${label} today ${emoji}`);
}

// --------------------------------------------------
//  CRISIS RESOURCES
// --------------------------------------------------
function showCrisisResources() {
  const box = document.createElement('div');
  box.className = 'settings-modal';
  box.innerHTML = `
    <div class="settings-box">
      <h3>Crisis Resources</h3>
      <p style="font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:16px;">
        If you or someone you know is in crisis, please reach out immediately.
      </p>
      <div style="display:flex;flex-direction:column;gap:12px;font-size:13px;">
        <div style="background:rgba(138,175,140,0.1);padding:14px;border-radius:10px;">
          <strong>🇺🇸 988 Suicide & Crisis Lifeline</strong><br>
          Call or text <strong>988</strong> · Available 24/7<br>
          <a href="https://988lifeline.org" target="_blank" style="color:var(--sage-dark);">988lifeline.org</a>
        </div>
        <div style="background:rgba(138,175,140,0.1);padding:14px;border-radius:10px;">
          <strong>💬 Crisis Text Line</strong><br>
          Text <strong>HOME to 741741</strong> · Available 24/7
        </div>
        <div style="background:rgba(138,175,140,0.1);padding:14px;border-radius:10px;">
          <strong>🏥 SAMHSA Helpline</strong><br>
          <strong>1-800-662-4357</strong> · Free, confidential
        </div>
        <div style="background:rgba(138,175,140,0.1);padding:14px;border-radius:10px;">
          <strong>🤝 NAMI Helpline</strong><br>
          <strong>1-800-950-NAMI</strong> · Mon–Fri 10am–10pm ET
        </div>
      </div>
      <div class="settings-actions" style="margin-top:20px;">
        <button type="button" class="btn-primary" onclick="this.closest('.settings-modal').remove()">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(box);
}

// --------------------------------------------------
//  SEND FROM INPUT BOX
// --------------------------------------------------
function sendMessage() {
  const input = document.getElementById('msgInput');
  const text  = input.value.trim();
  if (!text || isTyping) return;
  input.value = '';
  autoResize(input);
  doSend(text);
}

// --------------------------------------------------
//  SEND FROM SUGGESTION / QUICK PROMPT
// --------------------------------------------------
function sendQuick(btn) {
  const text = btn.querySelector('.prompt-text').textContent.trim();
  doSend(text);
}

function sendSuggestion(btn) {
  const text = btn.textContent.trim();
  doSend(text);
}

// --------------------------------------------------
//  CORE SEND (no underscore, not async arrow)
// --------------------------------------------------
function doSend(text) {
  if (!text || isTyping) return;

  // Remove welcome screen
  const welcome = document.getElementById('welcomeScreen');
  if (welcome) welcome.remove();

  // Remove suggestion bars
  document.querySelectorAll('.suggestions').forEach(s => s.remove());

  // Show user message
  appendMsg('user', text);
  showTyping();

  // Build payload
  const payload = {
    user_id:   currentUser,
    user_name: userPreferences.name,
    message:   text,
    history:   conversationHistory.slice(-10),
    conv_id:   currentConvId
  };

  fetch(`${API_BASE}/chat`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    hideTyping();
    const reply = data.response || data.error || 'Something went wrong.';
    appendMsg('ai', reply);

    if (data.conv_id) currentConvId = data.conv_id;

    if (data.crisis_level > 0 && !crisisVisible) {
      const banner = document.getElementById('crisisBanner');
      if (banner) { banner.classList.remove('hidden'); crisisVisible = true; }
    }

    conversationHistory.push({ role: 'user',      content: text  });
    conversationHistory.push({ role: 'assistant', content: reply });

    setTimeout(loadRecentConversationsOnce, 3000);
  })
  .catch(() => {
    hideTyping();
    appendMsg('ai', getFallback(text));
  });
}

// --------------------------------------------------
//  APPEND MESSAGES
// --------------------------------------------------
function appendMsg(role, text) {
  const messages = document.getElementById('messages');
  const wrap     = document.createElement('div');
  wrap.className = role === 'user' ? 'msg msg-user' : 'msg msg-ai';

  if (role === 'user') {
    wrap.innerHTML = `<div class="bubble bubble-user">${escHtml(text)}</div>`;
  } else {
    wrap.innerHTML = `
      <div class="msg-avatar">🌿</div>
      <div>
        <div class="bubble bubble-ai">${escHtml(text)}</div>
        <div class="suggestions">
          <button type="button" class="suggestion-btn" onclick="sendSuggestion(this)">Tell me more</button>
          <button type="button" class="suggestion-btn" onclick="sendSuggestion(this)">I need help</button>
          <button type="button" class="suggestion-btn" onclick="sendSuggestion(this)">What should I do?</button>
        </div>
      </div>`;
  }

  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

// --------------------------------------------------
//  TYPING INDICATOR
// --------------------------------------------------
function showTyping() {
  isTyping = true;
  const messages = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'msg msg-ai';
  el.id        = 'typingIndicator';
  el.innerHTML = `
    <div class="msg-avatar">🌿</div>
    <div class="bubble bubble-ai">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>`;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

function hideTyping() {
  isTyping = false;
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

// --------------------------------------------------
//  HELPERS
// --------------------------------------------------
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function escHtml(str) {
  return str
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/\n/g, '<br>');
}

// --------------------------------------------------
//  FALLBACK RESPONSES
// --------------------------------------------------
function getFallback(text) {
  const t = text.toLowerCase();
  if (t.includes('anxi') || t.includes('nervous') || t.includes('panic') || t.includes('worried')) {
    const opts = [
      `That took courage to say out loud 🌱 Anxiety loves to make us feel alone, but you're not. What's it been whispering to you lately?`,
      `Feeling anxious doesn't mean something is wrong with you — it means you care deeply 🍃 What's been weighing on your heart?`,
      `Take one slow breath 🍃 In… and out. You're here, you're safe. What's been making you feel this way?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('nobody') || t.includes('alone') || t.includes('lonely') || t.includes('no one') || t.includes('prioritis')) {
    const opts = [
      `You reaching out right now matters more than you know 💚 Loneliness can make the world feel impossibly quiet. What's been going on?`,
      `You are so much more wanted than it feels right now 🌿 What's been happening?`,
      `You're not invisible — I see you, and I'm here 💙 Can you tell me more about what's going on?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('depress') || t.includes('sad') || t.includes('hopeless') || t.includes('empty')) {
    const opts = [
      `Thank you for trusting me with something so personal 💙 What does today feel like for you?`,
      `Even on the darkest days, reaching out shows a light inside you 🌿 What's been going on lately?`,
      `Sometimes just naming the feeling takes real courage 💚 What's been the hardest part?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('sleep') || t.includes('tired') || t.includes('insomnia') || t.includes('exhausted')) {
    const opts = [
      `A tired mind and body deserve so much gentleness 🌙 How long has this been going on?`,
      `When sleep won't come, everything feels heavier 💤 What does your mind do when you lie down at night?`,
      `Sleep troubles are genuinely hard 🌙 What's been keeping you up?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('stress') || t.includes('overwhelm') || t.includes('too much')) {
    const opts = [
      `Feeling overwhelmed just means you've been carrying a lot 🌿 What feels most pressing right now?`,
      `You don't have to solve everything at once 💚 What's the ONE thing weighing on you most?`,
      `Stress has a way of stacking up quietly 🍃 What's been on your plate lately?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('angry') || t.includes('anger') || t.includes('furious') || t.includes('frustrated')) {
    const opts = [
      `Anger is often just hurt wearing armor 🔥 What happened that sparked this feeling?`,
      `That frustration is real 💚 What's going on?`,
      `These feelings make sense 🌿 Tell me what's been going on — no judgment here.`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('mindful') || t.includes('meditat') || t.includes('calm') || t.includes('breathe') || t.includes('peace')) {
    const opts = [
      `Seeking peace is such a beautiful thing 🍃 One deep breath right now — in… hold… and out. How does that feel?`,
      `Mindfulness is a gift you give yourself 🌸 Want to try a quick grounding exercise?`,
      `Finding calm takes real intention 💚 What does your body feel right now?`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('work') || t.includes('job') || t.includes('boss') || t.includes('office') || t.includes('career')) {
    const opts = [
      `Work stress can seep into everything 💼 Your worth is not your productivity — ever. What's been happening?`,
      `It sounds like work has been weighing on you 🌿 What's the biggest challenge right now?`,
      `So much of life is spent at work — it makes sense it affects your wellbeing 💚 Tell me more.`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  if (t.includes('grief') || t.includes('loss') || t.includes('died') || t.includes('miss') || t.includes('gone')) {
    const opts = [
      `Grief is love with nowhere to go 💙 I'm here to sit with you in it. Would you like to tell me about them?`,
      `You don't have to be okay right now 🌿 What are you feeling?`,
      `Grief takes as long as it takes, and that's okay 💙 I'm right here with you.`,
    ];
    return opts[Math.floor(Math.random() * opts.length)];
  }
  const generics = [
    `Really glad you're here 🌿 No judgment, no rush. What would feel good to talk about today?`,
    `It takes courage to put feelings into words 💚 I'm listening — tell me whatever feels right.`,
    `Whatever brought you here today, I'm glad it did 🌸 What's been on your heart lately?`,
    `Not going anywhere 🍃 What feels most important to share right now?`,
    `There's no wrong way to feel here 💙 What's been going on in your world?`,
  ];
  return generics[Math.floor(Math.random() * generics.length)];
}

// --------------------------------------------------
//  NEW CHAT
// --------------------------------------------------
function newChat() {
  conversationHistory = [];
  crisisVisible       = false;
  currentConvId       = null;

  const banner = document.getElementById('crisisBanner');
  if (banner) banner.classList.add('hidden');

  const messages = document.getElementById('messages');
  messages.innerHTML = `
    <div class="welcome" id="welcomeScreen">
      <div class="welcome-orb">🌿</div>
      <div class="welcome-text">
        <h2>Hello, I'm here for you</h2>
        <p>This is a gentle space to share what's on your mind. There's no judgment here — only care, curiosity, and compassion.</p>
      </div>
      <div class="quick-prompts">
        <button type="button" class="quick-prompt" onclick="sendQuick(this)">
          <span class="prompt-icon">😔</span>
          <span class="prompt-text">I've been feeling anxious lately</span>
        </button>
        <button type="button" class="quick-prompt" onclick="sendQuick(this)">
          <span class="prompt-icon">💭</span>
          <span class="prompt-text">I need someone to talk to</span>
        </button>
        <button type="button" class="quick-prompt" onclick="sendQuick(this)">
          <span class="prompt-icon">🧘</span>
          <span class="prompt-text">Help me practice mindfulness</span>
        </button>
        <button type="button" class="quick-prompt" onclick="sendQuick(this)">
          <span class="prompt-icon">😴</span>
          <span class="prompt-text">I've been struggling to sleep</span>
        </button>
      </div>
    </div>`;
}

// --------------------------------------------------
//  BREATHING EXERCISE
// --------------------------------------------------
function startBreathing() {
  const messages = document.getElementById('messages');
  const welcome  = document.getElementById('welcomeScreen');
  if (welcome) welcome.remove();

  const wrap = document.createElement('div');
  wrap.className = 'msg msg-ai';
  wrap.innerHTML = `
    <div class="msg-avatar">🌿</div>
    <div>
      <div class="bubble bubble-ai">Let's do a short breathing exercise together. Follow the circle — expand as it grows, release as it shrinks.</div>
      <div class="breathing-card">
        <h4>🫁 Box Breathing Exercise</h4>
        <div class="breathing-ring" id="breatheRing">breathe</div>
        <p style="font-size:12px;color:var(--muted);">Inhale 4s · Hold 4s · Exhale 4s · Hold 4s</p>
      </div>
    </div>`;
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;

  const ring   = document.getElementById('breatheRing');
  const phases = ['inhale', 'hold', 'exhale', 'hold'];
  let pi = 0;
  setInterval(() => { pi = (pi + 1) % 4; ring.textContent = phases[pi]; }, 4000);
}

// --------------------------------------------------
//  CONVERSATION DATABASE
// --------------------------------------------------
function loadRecentConversations() {
  clearTimeout(_loadTimer);
  _loadTimer = setTimeout(function() {
    if (!currentUser) return;
    fetch(`${API_BASE}/conversations/${currentUser}`)
      .then(function(res) {
        if (!res.ok) return;
        return res.json();
      })
      .then(function(data) {
        if (!data) return;
        renderConversationList(data.conversations || []);
      })
      .catch(function() {});
  }, 2000);
}

function renderConversationList(convs) {
  const list = document.getElementById('historyList');
  if (!list) return;
  list.innerHTML = '';

  if (convs.length === 0) {
    list.innerHTML = '<div style="font-size:12px;color:var(--muted);padding:8px 12px;">No conversations yet</div>';
    return;
  }

  convs.forEach(function(conv) {
    const item = document.createElement('div');
    item.className      = 'history-item';
    item.dataset.convId = conv.id;
    item.innerHTML      = `
      <div class="history-title">${conv.title}</div>
      <div class="history-time">${conv.time_label}</div>
    `;
    item.onclick = function() { loadConversation(conv.id); };
    list.appendChild(item);
  });
}

function loadConversation(convId) {
  fetch(`${API_BASE}/conversation/${currentUser}/${convId}`)
    .then(function(res) { return res.json(); })
    .then(function(conv) {
      if (!conv || !conv.messages) return;

      currentConvId       = convId;
      conversationHistory = conv.messages;

      const messages      = document.getElementById('messages');
      messages.innerHTML  = '';

      conv.messages.forEach(function(msg) {
        if (msg.role === 'user' || msg.role === 'assistant') {
          appendMsg(msg.role === 'assistant' ? 'ai' : 'user', msg.content);
        }
      });

      document.querySelectorAll('.history-item').forEach(function(el) { el.classList.remove('active'); });
      const activeEl = document.querySelector('[data-conv-id="' + convId + '"]');
      if (activeEl) activeEl.classList.add('active');
    })
    .catch(function() {});
}
function loadRecentConversationsOnce() {
  if (!currentUser) return;
  fetch(`${API_BASE}/conversations/${currentUser}`)
    .then(function(res) {
      if (!res.ok) return;
      return res.json();
    })
    .then(function(data) {
      if (!data) return;
      renderConversationList(data.conversations || []);
    })
    .catch(function() {});
}

// --------------------------------------------------
//  BOOT
// --------------------------------------------------
initializeUser();
loadRecentConversationsOnce();