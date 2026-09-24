// ── Cards page logic ──
// Reuse nav behaviors from home.js are not loaded here; keep this page self-contained.

const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
if (hamburger) {
  const closeMenu = () => {
    hamburger.classList.remove('active');
    hamburger.setAttribute('aria-expanded', 'false');
    navLinks.classList.remove('open');
    document.body.style.overflow = '';
  };
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', String(navLinks.classList.contains('open')));
    document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
  });
  navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
}

const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 80);
}, { passive: true });

const DECKS = [
  { key: 'zonghui', name: '宗辉 · 道诗' },
  { key: 'yunqing2026', name: '云清 · 2026 道诗' },
];

const dialog = document.getElementById('card-dialog');
const dialogBody = document.getElementById('dialog-body');

function openCard(card, deckName) {
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  dialogBody.innerHTML = `
    <img src="${card.image}" alt="《${esc(card.title)}》卡面" loading="lazy">
    <div class="dialog-deck">${esc(deckName)} · 第 ${(/^\d+$/.test(card.id) ? parseInt(card.id, 10) : card.id)} 签</div>
    <div class="dialog-title">《${esc(card.title)}》</div>
    <pre class="dialog-poem">${esc(card.poem)}</pre>
    ${card.quote ? `<p class="dialog-quote">“${esc(card.quote)}”</p>` : ''}
    ${card.highlight ? `<div class="dialog-section-label">点睛</div><p class="dialog-text">${esc(card.highlight)}</p>` : ''}
    ${card.insight ? `<div class="dialog-section-label">今日一悟</div><p class="dialog-text">${esc(card.insight)}</p>` : ''}
    ${card.question ? `<div class="dialog-section-label">今日一问</div><p class="dialog-text">${esc(card.question)}</p>` : ''}
    ${card.action ? `<div class="dialog-section-label">今日一行</div><p class="dialog-text">${esc(card.action)}</p>` : ''}
  `;
  dialog.showModal();
  dialogBody.scrollTop = 0;
}

document.getElementById('dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });

fetch('cards-data.json')
  .then(r => r.json())
  .then(data => {
    for (const deck of DECKS) {
      const grid = document.getElementById('grid-' + deck.key);
      const cards = data[deck.key] || [];
      cards.forEach(card => {
        const el = document.createElement('button');
        el.className = 'card-item';
        el.id = `${deck.key}-${card.id}`;
        el.innerHTML = `
          <img src="${card.image}" alt="《${card.title}》" loading="lazy">
          <div class="card-item-bar">
            <span class="card-item-title">《${card.title}》</span>
            <span class="card-item-num">第 ${(/^\d+$/.test(card.id) ? parseInt(card.id, 10) : card.id)} 签</span>
          </div>
        `;
        el.addEventListener('click', () => openCard(card, deck.name));
        grid.appendChild(el);
      });
    }

    // Deck filter tabs
    document.querySelectorAll('.deck-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.deck-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const deck = tab.dataset.deck;
        document.querySelectorAll('.deck-section').forEach(sec => {
          sec.style.display = (deck === 'all' || sec.id === deck) ? '' : 'none';
        });
      });
    });

    // Deep link: #zonghui-03 opens that card
    if (location.hash) {
      const target = document.getElementById(location.hash.slice(1));
      if (target && target.classList.contains('card-item')) {
        target.scrollIntoView({ block: 'center' });
        target.click();
      }
    }
  });
