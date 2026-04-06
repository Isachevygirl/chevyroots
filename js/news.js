/**
 * ChevyRoots News — Dynamic article loader
 * Loads articles from /data/news_articles.json, maps photos, handles filtering,
 * pagination, and search.
 */

(function () {
  'use strict';

  const ARTICLES_PER_PAGE = 24;
  const PHOTO_BASE = '/photos';

  // ── Photo catalog: model keyword → directory + sample filenames ──
  // We'll pick a random photo from the matched directory
  const PHOTO_MAP = {
    corvette:   { dir: 'corvette',   files: null },
    'zr1':      { dir: 'corvette',   files: null },
    'e-ray':    { dir: 'corvette',   files: null },
    'eray':     { dir: 'corvette',   files: null },
    stingray:   { dir: 'corvette',   files: null },
    'grand sport': { dir: 'corvette', files: null },
    'c8':       { dir: 'corvette',   files: null },
    'lt2':      { dir: 'corvette',   files: null },
    'lt7':      { dir: 'corvette',   files: null },
    silverado:  { dir: 'silverado',  files: null },
    'sierra':   { dir: 'silverado',  files: null },
    camaro:     { dir: 'camaro',     files: null },
    'zl1':      { dir: 'camaro',     files: null },
    'copo':     { dir: 'camaro',     files: null },
    tahoe:      { dir: 'tahoe',      files: null },
    suburban:   { dir: 'suburban',    files: null },
    blazer:     { dir: 'blazer',     files: null },
    equinox:    { dir: 'equinox',    files: null },
    colorado:   { dir: 'colorado',   files: null },
    'zr2':      { dir: 'colorado',   files: null },
    bolt:       { dir: 'bolt',       files: null },
    'bolt ev':  { dir: 'bolt',       files: null },
    'bolt euv': { dir: 'bolt',       files: null },
    traverse:   { dir: 'modern-misc', files: null },
    trax:       { dir: 'modern-misc', files: null },
    impala:     { dir: 'impala',     files: null },
    'bel air':  { dir: 'belair',     files: null },
    chevelle:   { dir: 'chevelle',   files: null },
    nova:       { dir: 'nova',       files: null },
    malibu:     { dir: 'malibu',     files: null },
    'monte carlo': { dir: 'monte-carlo', files: null },
    's-10':     { dir: 's10',        files: null },
    's10':      { dir: 's10',        files: null },
    // Racing / generic fallbacks
    nascar:     { dir: 'camaro',     files: null },
    hendrick:   { dir: 'camaro',     files: null },
    indycar:    { dir: 'modern-misc', files: null },
    'le mans':  { dir: 'corvette',   files: null },
    imsa:       { dir: 'corvette',   files: null },
    // Classics
    'square body': { dir: 'trucks-classic', files: null },
    'squarebody':  { dir: 'trucks-classic', files: null },
    'classic':  { dir: 'classic-misc', files: null },
    'barn find': { dir: 'classic-misc', files: null },
    'lowrider': { dir: 'impala',     files: null },
    'sema':     { dir: 'camaro',     files: null },
    'auction':  { dir: 'classic-misc', files: null },
    'barrett':  { dir: 'classic-misc', files: null },
    'mecum':    { dir: 'classic-misc', files: null },
    'restomod': { dir: 'classic-misc', files: null },
    // EV generic
    'ultium':   { dir: 'bolt',       files: null },
    'ev':       { dir: 'bolt',       files: null },
    'electric': { dir: 'bolt',       files: null },
    'nacs':     { dir: 'bolt',       files: null },
  };

  // Category fallback photos (if no keyword matches)
  const CATEGORY_FALLBACK = {
    'new-models': 'modern-misc',
    'recalls':    'modern-misc',
    'racing':     'camaro',
    'culture':    'classic-misc',
    'ev':         'bolt',
    'deals':      'silverado',
  };

  // Category display config
  const CATEGORY_CONFIG = {
    'new-models': { label: 'New Models',       cssClass: 'cat-new-models' },
    'recalls':    { label: 'Recalls & Safety',  cssClass: 'cat-recalls' },
    'racing':     { label: 'Racing',            cssClass: 'cat-racing' },
    'culture':    { label: 'Culture',           cssClass: 'cat-culture' },
    'ev':         { label: 'EV News',           cssClass: 'cat-ev' },
    'deals':      { label: 'Deals',             cssClass: 'cat-deals' },
  };

  // Gradient backgrounds per category (for photo overlay fallback)
  const CATEGORY_GRADIENTS = {
    'new-models': 'linear-gradient(135deg, #1a2028, #1e2a38)',
    'recalls':    'linear-gradient(135deg, #2a1a1a, #351e1e)',
    'racing':     'linear-gradient(135deg, #1e1a2a, #28204a)',
    'culture':    'linear-gradient(135deg, #2a2a1a, #3a3a1a)',
    'ev':         'linear-gradient(135deg, #1a2a1e, #1e3526)',
    'deals':      'linear-gradient(135deg, #1c2018, #2a3020)',
  };

  // ── State ──
  let allArticles = [];
  let filteredArticles = [];
  let currentPage = 1;
  let currentFilter = 'all';
  let currentSearch = '';
  let photoCatalog = {};  // dir → [filenames]

  // ── Load photo catalog ──
  async function loadPhotoCatalog() {
    try {
      const resp = await fetch('/photos/catalog_pexels_tagged.json');
      if (resp.ok) {
        const data = await resp.json();
        // Build dir → filenames map
        if (Array.isArray(data)) {
          data.forEach(item => {
            const dir = item.directory || item.model;
            if (dir) {
              if (!photoCatalog[dir]) photoCatalog[dir] = [];
              if (item.filename) photoCatalog[dir].push(item.filename);
            }
          });
        }
      }
    } catch (e) {
      // Fallback: use hardcoded photo counts and generate filenames
    }

    // Also try the plain catalog (primary format: [{file: "dir/filename", category: "dir"}])
    try {
      const resp = await fetch('/photos/catalog_pexels.json');
      if (resp.ok) {
        const data = await resp.json();
        if (Array.isArray(data)) {
          data.forEach(item => {
            // Format: { file: "corvette/pexels_123.jpeg", category: "corvette" }
            if (item.file) {
              const parts = item.file.split('/');
              if (parts.length === 2) {
                const dir = parts[0];
                const filename = parts[1];
                if (!photoCatalog[dir]) photoCatalog[dir] = [];
                if (!photoCatalog[dir].includes(filename)) {
                  photoCatalog[dir].push(filename);
                }
              }
            }
            // Also handle directory/model + filename format
            const dir = item.directory || item.model || item.category;
            const filename = item.filename;
            if (dir && filename) {
              if (!photoCatalog[dir]) photoCatalog[dir] = [];
              if (!photoCatalog[dir].includes(filename)) {
                photoCatalog[dir].push(filename);
              }
            }
          });
        }
      }
    } catch (e) { /* no catalog available */ }

    // Load complete catalog (all photos including Wikipedia/manual ones)
    try {
      const resp = await fetch('/photos/catalog_all.json');
      if (resp.ok) {
        const data = await resp.json();
        // Format: { "dir": ["file1.jpg", "file2.jpg", ...] }
        Object.entries(data).forEach(([dir, files]) => {
          if (!photoCatalog[dir]) photoCatalog[dir] = [];
          files.forEach(f => {
            if (!photoCatalog[dir].includes(f)) photoCatalog[dir].push(f);
          });
        });
      }
    } catch (e) { /* no catalog */ }

    if (Object.keys(photoCatalog).length === 0) {
      console.warn('ChevyRoots News: photo catalog empty, photos will use gradient fallbacks');
    } else {
      const total = Object.values(photoCatalog).reduce((s, a) => s + a.length, 0);
      console.log(`ChevyRoots News: loaded ${total} photos across ${Object.keys(photoCatalog).length} directories`);
    }
  }

  // ── Find a photo for an article ──
  function getPhotoForArticle(article) {
    const text = (article.title + ' ' + article.summary).toLowerCase();

    // Try keyword matching (longest match first for specificity)
    const keywords = Object.keys(PHOTO_MAP).sort((a, b) => b.length - a.length);
    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        const dir = PHOTO_MAP[keyword].dir;
        return pickRandomPhoto(dir);
      }
    }

    // Fallback to category
    const fallbackDir = CATEGORY_FALLBACK[article.category] || 'modern-misc';
    return pickRandomPhoto(fallbackDir);
  }

  function pickRandomPhoto(dir) {
    const files = photoCatalog[dir];
    if (files && files.length > 0) {
      const file = files[Math.floor(Math.random() * files.length)];
      return `${PHOTO_BASE}/${dir}/${file}`;
    }
    // If no catalog, return null (will use gradient fallback)
    return null;
  }

  // ── Render functions ──

  function renderFeaturedCard(article) {
    const photo = getPhotoForArticle(article);
    const cat = CATEGORY_CONFIG[article.category] || CATEGORY_CONFIG['new-models'];
    const shareText = encodeURIComponent(article.title + ' @ChevyRoots');
    const shareUrl = encodeURIComponent('https://chevyroots.com/pages/news/');

    return `
      <article class="featured-card" data-category="${article.category}">
        <div class="featured-image">
          ${photo
            ? `<img src="${photo}" alt="${escapeHtml(article.title)}" loading="eager" style="width:100%;height:100%;object-fit:cover;" onerror="this.parentElement.innerHTML='<div class=\\'img-placeholder\\'><span>${escapeHtml(article.title)}</span></div>'">`
            : `<div class="img-placeholder" style="background:${CATEGORY_GRADIENTS[article.category] || CATEGORY_GRADIENTS['new-models']}"><span>${escapeHtml(article.title)}</span></div>`
          }
        </div>
        <div class="featured-body">
          <div class="featured-meta">
            <span class="cat-badge ${cat.cssClass}">${cat.label}</span>
            <span class="news-source">${escapeHtml(article.source)}</span>
            <span class="news-date">${formatDate(article.date)}</span>
          </div>
          <h2 class="featured-title">${escapeHtml(article.title)}</h2>
          <p class="featured-summary">${escapeHtml(article.summary)}</p>
          <div>
            <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" class="read-link">Read Full Story &rarr;</a>
          </div>
          <div class="featured-share-row">
            <span class="featured-share-label">Share:</span>
            <button class="share-btn" onclick="copyLink(this, 'https://chevyroots.com/pages/news/')">&#128279; Copy Link</button>
            <a href="https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}" target="_blank" rel="noopener noreferrer" class="share-btn share-btn-x">&#120143; Share on X</a>
          </div>
        </div>
      </article>`;
  }

  function renderNewsCard(article) {
    const photo = getPhotoForArticle(article);
    const cat = CATEGORY_CONFIG[article.category] || CATEGORY_CONFIG['new-models'];
    const shareText = encodeURIComponent(article.title + ' @ChevyRoots');
    const shareUrl = encodeURIComponent('https://chevyroots.com/pages/news/');

    return `
      <article class="news-card" data-category="${article.category}">
        <div class="card-image">
          ${photo
            ? `<img src="${photo}" alt="${escapeHtml(article.title)}" loading="lazy" style="width:100%;height:100%;object-fit:cover;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="img-placeholder" style="display:none;height:100%;background:${CATEGORY_GRADIENTS[article.category]}"><span>${escapeHtml(article.source)}</span></div>`
            : `<div class="img-placeholder" style="height:100%;background:${CATEGORY_GRADIENTS[article.category] || CATEGORY_GRADIENTS['new-models']}"><span>${escapeHtml(article.source)}</span></div>`
          }
        </div>
        <div class="card-body">
          <div class="card-meta">
            <span class="cat-badge ${cat.cssClass}">${cat.label}</span>
            <span class="news-source">${escapeHtml(article.source)}</span>
          </div>
          <h3 class="card-title">${escapeHtml(article.title)}</h3>
          <p class="card-summary">${escapeHtml(article.summary)}</p>
          <div class="card-footer">
            <span class="news-date">${formatDate(article.date)}</span>
            <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" class="read-link">Read Full Story &rarr;</a>
          </div>
          <div class="share-btns" style="margin-top:0.75rem;">
            <button class="share-btn" onclick="copyLink(this, '${escapeHtml(article.url)}')">&#128279; Copy</button>
            <a href="https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}" target="_blank" rel="noopener noreferrer" class="share-btn share-btn-x">&#120143; X</a>
          </div>
        </div>
      </article>`;
  }

  function renderMostRead(articles) {
    // Pick top articles from different categories
    const picks = [];
    const usedCats = new Set();
    for (const a of articles) {
      if (!usedCats.has(a.category) && picks.length < 5) {
        picks.push(a);
        usedCats.add(a.category);
      }
    }
    // Fill remaining from top of list
    for (const a of articles) {
      if (picks.length >= 5) break;
      if (!picks.includes(a)) picks.push(a);
    }

    const items = picks.map((a, i) => {
      const opacity = i === 0 ? '1' : i === 1 ? '0.55' : i === 2 ? '0.35' : '0.2';
      return `
        <li style="display:flex;align-items:flex-start;gap:1rem;${i < picks.length - 1 ? 'padding-bottom:1rem;border-bottom:1px solid rgba(255,255,255,0.07);' : ''}">
          <span style="font-family:var(--font-heading);font-size:2.5rem;font-weight:800;color:rgba(196,160,53,${opacity});line-height:1;min-width:2rem;text-align:center;">${i + 1}</span>
          <div>
            <a href="${escapeHtml(a.url)}" target="_blank" rel="noopener noreferrer" style="font-family:var(--font-heading);font-size:1.1rem;font-weight:700;text-transform:uppercase;letter-spacing:0.02em;color:var(--off-white);margin-bottom:0.25rem;display:block;text-decoration:none;transition:color 200ms ease;" onmouseover="this.style.color='var(--gold)'" onmouseout="this.style.color='var(--off-white)'">${escapeHtml(a.title)}</a>
            <div style="font-family:var(--font-mono);font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--light-gray);">${CATEGORY_CONFIG[a.category]?.label || a.category} &nbsp;&bull;&nbsp; ${escapeHtml(a.source)}</div>
          </div>
        </li>`;
    }).join('');

    return `
      <div style="background:var(--warm-gray);border:1px solid rgba(196,160,53,0.2);border-radius:8px;padding:2rem 2rem 1.75rem;margin-top:3rem;">
        <div style="font-family:var(--font-mono);font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:var(--gold);margin-bottom:0.5rem;">Trending</div>
        <h2 style="font-family:var(--font-heading);font-size:clamp(1.5rem,3vw,2rem);font-weight:800;text-transform:uppercase;letter-spacing:0.02em;color:var(--off-white);margin-bottom:1.5rem;">Most Read</h2>
        <ol style="list-style:none;display:flex;flex-direction:column;gap:1rem;">${items}</ol>
      </div>`;
  }

  // ── Pagination ──

  function renderPagination() {
    const totalPages = Math.ceil(filteredArticles.length / ARTICLES_PER_PAGE);
    if (totalPages <= 1) return '';

    let buttons = '';
    const maxVisible = 7;
    let start = Math.max(1, currentPage - 3);
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1);

    if (currentPage > 1) {
      buttons += `<button class="pagination-btn" onclick="window.chevyNews.goToPage(${currentPage - 1})">&laquo; Prev</button>`;
    }

    if (start > 1) {
      buttons += `<button class="pagination-btn" onclick="window.chevyNews.goToPage(1)">1</button>`;
      if (start > 2) buttons += `<span class="pagination-dots">&hellip;</span>`;
    }

    for (let i = start; i <= end; i++) {
      buttons += `<button class="pagination-btn${i === currentPage ? ' active' : ''}" onclick="window.chevyNews.goToPage(${i})">${i}</button>`;
    }

    if (end < totalPages) {
      if (end < totalPages - 1) buttons += `<span class="pagination-dots">&hellip;</span>`;
      buttons += `<button class="pagination-btn" onclick="window.chevyNews.goToPage(${totalPages})">${totalPages}</button>`;
    }

    if (currentPage < totalPages) {
      buttons += `<button class="pagination-btn" onclick="window.chevyNews.goToPage(${currentPage + 1})">Next &raquo;</button>`;
    }

    return `
      <div class="pagination" role="navigation" aria-label="News pagination">
        <div class="pagination-info">
          Showing ${((currentPage - 1) * ARTICLES_PER_PAGE) + 1}&ndash;${Math.min(currentPage * ARTICLES_PER_PAGE, filteredArticles.length)} of ${filteredArticles.length} stories
        </div>
        <div class="pagination-buttons">${buttons}</div>
      </div>`;
  }

  // ── Filter & Search ──

  function applyFilters() {
    filteredArticles = allArticles.filter(a => {
      const matchesCat = currentFilter === 'all' || a.category === currentFilter;
      const matchesSearch = !currentSearch ||
        a.title.toLowerCase().includes(currentSearch) ||
        a.summary.toLowerCase().includes(currentSearch) ||
        a.source.toLowerCase().includes(currentSearch);
      return matchesCat && matchesSearch;
    });
    currentPage = 1;
    render();
  }

  // ── Main render ──

  function render() {
    const featuredContainer = document.getElementById('featuredArticle');
    const gridContainer = document.getElementById('newsGrid');
    const paginationContainer = document.getElementById('newsPagination');
    const mostReadContainer = document.getElementById('mostRead');
    const noResults = document.getElementById('noResults');
    const statNum = document.querySelector('.page-hero-stat-num');
    const statLabel = document.querySelector('.page-hero-stat-label');

    if (!gridContainer) return;

    // Update stat
    if (statNum) statNum.textContent = filteredArticles.length;
    if (statLabel) statLabel.textContent = currentFilter === 'all' ? 'Total Stories' : CATEGORY_CONFIG[currentFilter]?.label || 'Stories';

    if (filteredArticles.length === 0) {
      if (featuredContainer) featuredContainer.innerHTML = '';
      gridContainer.innerHTML = '';
      if (paginationContainer) paginationContainer.innerHTML = '';
      if (noResults) noResults.style.display = 'block';
      return;
    }

    if (noResults) noResults.style.display = 'none';

    // Featured = first article
    if (featuredContainer) {
      featuredContainer.innerHTML = renderFeaturedCard(filteredArticles[0]);
    }

    // Grid = remaining articles for current page
    const start = (currentPage - 1) * ARTICLES_PER_PAGE;
    const end = start + ARTICLES_PER_PAGE;
    // Skip first article (it's featured) on page 1
    const pageArticles = currentPage === 1
      ? filteredArticles.slice(1, end)
      : filteredArticles.slice(start, end);

    gridContainer.innerHTML = pageArticles.map(renderNewsCard).join('');

    // Pagination
    if (paginationContainer) {
      paginationContainer.innerHTML = renderPagination();
    }

    // Most read (only show on page 1, all filter)
    if (mostReadContainer) {
      if (currentPage === 1 && currentFilter === 'all' && !currentSearch) {
        mostReadContainer.innerHTML = renderMostRead(allArticles);
        mostReadContainer.style.display = '';
      } else {
        mostReadContainer.style.display = 'none';
      }
    }
  }

  // ── Helpers ──

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr + 'T00:00:00');
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) {
      return dateStr;
    }
  }

  // ── Initialize ──

  async function init() {
    // Load photo catalog first
    await loadPhotoCatalog();

    // Load articles
    try {
      const resp = await fetch('/data/news_articles.json');
      if (!resp.ok) throw new Error('Failed to load articles');
      allArticles = await resp.json();

      // Sort by date descending (newest first)
      allArticles.sort((a, b) => (b.date || '').localeCompare(a.date || ''));

      filteredArticles = [...allArticles];
      render();

      // Update "last updated" based on newest article
      const lastUpdated = document.getElementById('lastUpdated');
      if (lastUpdated && allArticles.length > 0) {
        lastUpdated.textContent = formatDate(allArticles[0].date);
      }

      // Update category counts in filter buttons
      const counts = {};
      allArticles.forEach(a => { counts[a.category] = (counts[a.category] || 0) + 1; });
      document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
        const filter = btn.dataset.filter;
        if (filter !== 'all' && counts[filter] !== undefined) {
          btn.innerHTML = btn.textContent.trim() + ` <span class="filter-count">${counts[filter]}</span>`;
        } else if (filter === 'all') {
          btn.innerHTML = btn.textContent.trim() + ` <span class="filter-count">${allArticles.length}</span>`;
        }
      });

    } catch (err) {
      console.error('ChevyRoots News: could not load articles', err);
      document.getElementById('newsGrid').innerHTML =
        '<p style="text-align:center;color:var(--light-gray);padding:3rem;font-family:var(--font-mono);font-size:0.85rem;">Unable to load news articles. Please try again later.</p>';
    }
  }

  // ── Public API ──
  window.chevyNews = {
    filter(category, btn) {
      currentFilter = category;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      applyFilters();
    },
    search(query) {
      currentSearch = query.toLowerCase().trim();
      applyFilters();
    },
    goToPage(page) {
      currentPage = page;
      render();
      // Scroll to top of grid
      const grid = document.getElementById('newsGrid');
      if (grid) {
        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },
  };

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
