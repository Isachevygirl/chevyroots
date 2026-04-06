/* ============================================================
   mechanics.js — ChevyRoots Mechanic Finder
   Data loading, filtering, sorting, rendering, composite scores
============================================================ */

(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────
  let allMechanics = [];
  let taxonomy = [];
  let communityReviews = [];
  let filters = {
    search: '',
    state: '',
    specialties: [],
    minRating: 0,
    sort: 'composite_score'
  };
  const PER_PAGE = 12;
  let visibleCount = PER_PAGE;

  // ── Data Loading ───────────────────────────────────────
  async function loadJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`Failed to load ${path}`);
    return res.json();
  }

  async function loadAllData() {
    const [mechData, reviewData] = await Promise.all([
      loadJSON('/data/mechanics.json'),
      loadJSON('/data/mechanic-reviews.json').catch(() => ({ reviews: [] }))
    ]);
    allMechanics = mechData.mechanics || [];
    taxonomy = mechData.specialties_taxonomy || [];
    communityReviews = reviewData.reviews || [];
    return { mechanics: allMechanics, taxonomy, communityReviews };
  }

  // ── Composite Score ────────────────────────────────────
  // Weighted average with Bayesian prior for small sample sizes
  function calcComposite(r) {
    const PRIOR = 3.5;
    const MIN_COUNT = 5;
    const sources = [
      { avg: r.google_avg, count: r.google_count, weight: 0.35 },
      { avg: r.yelp_avg, count: r.yelp_count, weight: 0.30 },
      { avg: r.chevyroots_avg, count: r.chevyroots_count, weight: 0.35 }
    ];

    let num = 0;
    let den = 0;
    for (const s of sources) {
      if (!s.count) continue;
      // Bayesian adjustment for sources with few reviews
      const adj = s.count < MIN_COUNT
        ? (s.avg * s.count + PRIOR * MIN_COUNT) / (s.count + MIN_COUNT)
        : s.avg;
      num += adj * s.count * s.weight;
      den += s.count * s.weight;
    }
    return den > 0 ? Math.round((num / den) * 100) / 100 : 0;
  }

  function totalReviewCount(r) {
    return (r.google_count || 0) + (r.yelp_count || 0) + (r.chevyroots_count || 0);
  }

  // ── Filtering ──────────────────────────────────────────
  function applyFilters(mechanics) {
    return mechanics.filter(m => {
      // Text search
      if (filters.search) {
        const q = filters.search.toLowerCase();
        const haystack = [
          m.name, m.address.city, m.address.state, m.description,
          ...m.specialties, ...(m.chevy_models_served || [])
        ].join(' ').toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      // State filter
      if (filters.state && m.address.state !== filters.state) return false;
      // Specialty filter
      if (filters.specialties.length > 0) {
        if (!filters.specialties.some(s => m.specialties.includes(s))) return false;
      }
      // Min rating
      if (filters.minRating > 0 && m.ratings.composite_score < filters.minRating) return false;
      return true;
    });
  }

  // ── Sorting ────────────────────────────────────────────
  function applySort(mechanics) {
    const sorted = [...mechanics];
    switch (filters.sort) {
      case 'composite_score':
        sorted.sort((a, b) => b.ratings.composite_score - a.ratings.composite_score);
        break;
      case 'review_count':
        sorted.sort((a, b) => totalReviewCount(b.ratings) - totalReviewCount(a.ratings));
        break;
      case 'newest':
        sorted.sort((a, b) => new Date(b.added_date) - new Date(a.added_date));
        break;
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
    }
    return sorted;
  }

  // ── Stars HTML ─────────────────────────────────────────
  function starsHTML(rating, size) {
    size = size || 'md';
    const full = Math.floor(rating);
    const half = rating - full >= 0.25 && rating - full < 0.75 ? 1 : 0;
    const bump = rating - full >= 0.75 ? 1 : 0;
    const empty = 5 - full - half - bump;
    const cls = size === 'sm' ? 'star star-sm' : 'star';
    let html = '';
    for (let i = 0; i < full + bump; i++) html += `<span class="${cls} star-full">&#9733;</span>`;
    for (let i = 0; i < half; i++) html += `<span class="${cls} star-half">&#9733;</span>`;
    for (let i = 0; i < empty; i++) html += `<span class="${cls} star-empty">&#9734;</span>`;
    return html;
  }

  // ── Specialty Label ────────────────────────────────────
  function specialtyLabel(id) {
    const t = taxonomy.find(t => t.id === id);
    return t ? t.label : id.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  // ── Card Renderer ──────────────────────────────────────
  function renderCard(m) {
    const total = totalReviewCount(m.ratings);
    const tags = m.specialties.slice(0, 3).map(s =>
      `<span class="mech-tag">${specialtyLabel(s)}</span>`
    ).join('');
    const verified = m.verified ? '<span class="mech-verified" title="Verified Listing">&#10003; Verified</span>' : '';
    const featured = m.featured ? '<span class="mech-featured-badge">Featured</span>' : '';

    return `
      <a href="/pages/mechanics/profile.html?id=${m.slug}" class="mech-card${m.featured ? ' mech-card-featured' : ''}">
        <div class="mech-card-header">
          <div class="mech-card-name">${m.name}</div>
          ${featured}
        </div>
        <div class="mech-card-location">${m.address.city}, ${m.address.state}</div>
        <div class="mech-card-rating">
          <div class="mech-stars">${starsHTML(m.ratings.composite_score)}</div>
          <span class="mech-score">${m.ratings.composite_score.toFixed(1)}</span>
          <span class="mech-review-count">(${total} reviews)</span>
        </div>
        <div class="mech-card-tags">${tags}</div>
        <div class="mech-card-footer">
          ${verified}
          <span class="mech-years">${m.years_in_business} yrs in business</span>
        </div>
      </a>`;
  }

  // ── Spotlight Renderer ─────────────────────────────────
  function renderSpotlight(mechanics) {
    const featured = mechanics.filter(m => m.featured).slice(0, 3);
    if (!featured.length) return '';
    return featured.map(m => {
      const total = totalReviewCount(m.ratings);
      return `
        <div class="spotlight-card">
          <div class="spotlight-badge">Mechanic Spotlight</div>
          <div class="spotlight-name">${m.name}</div>
          <div class="spotlight-location">${m.address.city}, ${m.address.state}</div>
          <div class="spotlight-rating">
            ${starsHTML(m.ratings.composite_score, 'sm')}
            <span>${m.ratings.composite_score.toFixed(1)}</span>
            <span class="mech-review-count">(${total})</span>
          </div>
          <p class="spotlight-desc">${m.description}</p>
          <a href="/pages/mechanics/profile.html?id=${m.slug}" class="btn btn-gold btn-sm">View Profile</a>
        </div>`;
    }).join('');
  }

  // ── Directory Page Init ────────────────────────────────
  function initDirectory() {
    const grid = document.getElementById('mechanicsGrid');
    const spotlightEl = document.getElementById('mechanicsSpotlight');
    const countEl = document.getElementById('resultsCount');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (!grid) return;

    loadAllData().then(() => {
      // Populate state dropdown
      const states = [...new Set(allMechanics.map(m => m.address.state))].sort();
      const stateSelect = document.getElementById('filterState');
      if (stateSelect) {
        states.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          stateSelect.appendChild(opt);
        });
      }

      // Populate specialty checkboxes
      const specContainer = document.getElementById('filterSpecialties');
      if (specContainer) {
        taxonomy.forEach(t => {
          const label = document.createElement('label');
          label.className = 'spec-check';
          label.innerHTML = `<input type="checkbox" value="${t.id}" /> ${t.label}`;
          specContainer.appendChild(label);
        });
      }

      // Render spotlight
      if (spotlightEl) {
        spotlightEl.innerHTML = renderSpotlight(allMechanics);
      }

      renderResults();
      bindFilterEvents();
    });

    function renderResults() {
      const filtered = applySort(applyFilters(allMechanics));
      const visible = filtered.slice(0, visibleCount);
      grid.innerHTML = visible.map(renderCard).join('');
      if (countEl) countEl.textContent = `${filtered.length} mechanic${filtered.length !== 1 ? 's' : ''} found`;
      if (loadMoreBtn) {
        loadMoreBtn.style.display = visibleCount >= filtered.length ? 'none' : '';
      }
    }

    function bindFilterEvents() {
      const searchInput = document.getElementById('filterSearch');
      const stateSelect = document.getElementById('filterState');
      const sortSelect = document.getElementById('filterSort');
      const ratingSlider = document.getElementById('filterRating');
      const ratingValue = document.getElementById('ratingValue');
      const specContainer = document.getElementById('filterSpecialties');

      if (searchInput) searchInput.addEventListener('input', () => {
        filters.search = searchInput.value;
        visibleCount = PER_PAGE;
        renderResults();
      });
      if (stateSelect) stateSelect.addEventListener('change', () => {
        filters.state = stateSelect.value;
        visibleCount = PER_PAGE;
        renderResults();
      });
      if (sortSelect) sortSelect.addEventListener('change', () => {
        filters.sort = sortSelect.value;
        visibleCount = PER_PAGE;
        renderResults();
      });
      if (ratingSlider) ratingSlider.addEventListener('input', () => {
        filters.minRating = parseFloat(ratingSlider.value);
        if (ratingValue) ratingValue.textContent = filters.minRating > 0 ? filters.minRating.toFixed(1) + '+' : 'Any';
        visibleCount = PER_PAGE;
        renderResults();
      });
      if (specContainer) specContainer.addEventListener('change', () => {
        filters.specialties = [...specContainer.querySelectorAll('input:checked')].map(i => i.value);
        visibleCount = PER_PAGE;
        renderResults();
      });
      if (loadMoreBtn) loadMoreBtn.addEventListener('click', () => {
        visibleCount += PER_PAGE;
        renderResults();
      });
    }
  }

  // ── Profile Page Init ──────────────────────────────────
  function initProfile() {
    const container = document.getElementById('mechanicProfile');
    if (!container) return;

    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) {
      container.innerHTML = '<p>Mechanic not found.</p>';
      return;
    }

    loadAllData().then(() => {
      const mech = allMechanics.find(m => m.slug === id || m.id === id);
      if (!mech) {
        container.innerHTML = '<p>Mechanic not found. <a href="/pages/mechanics/" style="color:var(--gold)">Browse all mechanics &rarr;</a></p>';
        return;
      }

      // Update page title
      document.title = `${mech.name} | ChevyRoots Mechanics`;
      const metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) metaDesc.content = `${mech.name} — ${mech.description}`;

      // JSON-LD structured data
      const jsonLd = document.getElementById('json-ld-schema');
      if (jsonLd) {
        jsonLd.textContent = JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'AutoRepair',
          'name': mech.name,
          'address': {
            '@type': 'PostalAddress',
            'streetAddress': mech.address.street,
            'addressLocality': mech.address.city,
            'addressRegion': mech.address.state,
            'postalCode': mech.address.zip
          },
          'telephone': mech.phone,
          'url': mech.website,
          'aggregateRating': {
            '@type': 'AggregateRating',
            'ratingValue': mech.ratings.composite_score,
            'reviewCount': totalReviewCount(mech.ratings)
          }
        });
      }

      const total = totalReviewCount(mech.ratings);
      const verified = mech.verified ? '<span class="profile-verified">&#10003; Verified Listing</span>' : '';
      const certified = mech.certified ? '<span class="profile-certified">GM Certified</span>' : '';

      // Specialties tags
      const specTags = mech.specialties.map(s =>
        `<span class="mech-tag">${specialtyLabel(s)}</span>`
      ).join('');

      // Models served
      const modelLinks = (mech.chevy_models_served || []).map(slug =>
        `<a href="/pages/models/template.html?model=${slug}" class="model-link">${slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</a>`
      ).join('');

      // Rating breakdown
      const ratingBreakdown = [
        { label: 'Google', avg: mech.ratings.google_avg, count: mech.ratings.google_count },
        { label: 'Yelp', avg: mech.ratings.yelp_avg, count: mech.ratings.yelp_count },
        { label: 'ChevyRoots', avg: mech.ratings.chevyroots_avg, count: mech.ratings.chevyroots_count }
      ].map(s => `
        <div class="rating-source">
          <span class="rating-source-label">${s.label}</span>
          <div class="rating-source-stars">${starsHTML(s.avg, 'sm')}</div>
          <span class="rating-source-score">${s.avg ? s.avg.toFixed(1) : '—'}</span>
          <span class="rating-source-count">(${s.count || 0})</span>
        </div>
      `).join('');

      // Community reviews for this mechanic
      const mechReviews = communityReviews
        .filter(r => r.mechanic_id === mech.id && r.status === 'approved')
        .sort((a, b) => new Date(b.date) - new Date(a.date));

      const reviewsHTML = mechReviews.length
        ? mechReviews.map(r => `
            <div class="review-card">
              <div class="review-header">
                <span class="review-author">${r.author}</span>
                <span class="review-date">${new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
              </div>
              <div class="review-rating">${starsHTML(r.rating, 'sm')}</div>
              ${r.vehicle ? `<div class="review-vehicle">${r.vehicle}</div>` : ''}
              ${r.title ? `<div class="review-title">${r.title}</div>` : ''}
              <p class="review-body">${r.body}</p>
            </div>`).join('')
        : '<p class="no-reviews">No community reviews yet. Be the first to share your experience!</p>';

      // Related mechanics (same state, different shop)
      const related = allMechanics
        .filter(m => m.id !== mech.id && m.address.state === mech.address.state)
        .sort((a, b) => b.ratings.composite_score - a.ratings.composite_score)
        .slice(0, 3);
      const relatedHTML = related.length ? related.map(m => `
        <a href="/pages/mechanics/profile.html?id=${m.slug}" class="related-card">
          <div class="related-name">${m.name}</div>
          <div class="related-location">${m.address.city}, ${m.address.state}</div>
          <div class="related-rating">${starsHTML(m.ratings.composite_score, 'sm')} ${m.ratings.composite_score.toFixed(1)}</div>
        </a>
      `).join('') : '';

      container.innerHTML = `
        <div class="profile-header">
          <div class="profile-header-main">
            <h1 class="profile-name">${mech.name}</h1>
            <div class="profile-badges">${verified} ${certified}</div>
            <div class="profile-location">${mech.address.street}, ${mech.address.city}, ${mech.address.state} ${mech.address.zip}</div>
            <div class="profile-contact">
              <a href="tel:${mech.phone.replace(/[^+\d]/g, '')}" class="profile-phone">${mech.phone}</a>
              ${mech.website ? `<a href="${mech.website}" target="_blank" rel="noopener" class="profile-website">Visit Website &rarr;</a>` : ''}
            </div>
          </div>
          <div class="profile-score-box">
            <div class="profile-composite">${mech.ratings.composite_score.toFixed(1)}</div>
            <div class="profile-composite-stars">${starsHTML(mech.ratings.composite_score)}</div>
            <div class="profile-composite-count">${total} total reviews</div>
          </div>
        </div>

        <div class="profile-body">
          <div class="profile-main">
            <p class="profile-desc">${mech.description}</p>

            <div class="profile-section">
              <h2 class="profile-section-title">Specialties</h2>
              <div class="profile-tags">${specTags}</div>
            </div>

            <div class="profile-section">
              <h2 class="profile-section-title">Chevy Models Served</h2>
              <div class="profile-models">${modelLinks}</div>
            </div>

            <div class="profile-section">
              <h2 class="profile-section-title">Rating Breakdown</h2>
              <div class="rating-breakdown">${ratingBreakdown}</div>
            </div>

            <div class="profile-section" id="externalReviews">
              <h2 class="profile-section-title">Yelp & Google Reviews</h2>
              <p class="external-reviews-note">External reviews are aggregated from Yelp and Google. Connect your Yelp and Google Business IDs to display individual reviews here.</p>
            </div>

            <div class="profile-section">
              <h2 class="profile-section-title">Community Reviews</h2>
              <div class="reviews-list">${reviewsHTML}</div>
            </div>

            <div class="profile-section" id="writeReview">
              <h2 class="profile-section-title">Write a Review</h2>
              <form name="mechanic-review" method="POST" data-netlify="true" class="review-form" id="reviewForm">
                <input type="hidden" name="mechanic_id" value="${mech.id}" />
                <input type="hidden" name="form-name" value="mechanic-review" />
                <div class="form-row">
                  <div class="form-group">
                    <label for="reviewName">Your Name</label>
                    <input type="text" id="reviewName" name="author" required placeholder="e.g. Mike R." />
                  </div>
                  <div class="form-group">
                    <label for="reviewVehicle">Your Chevy</label>
                    <input type="text" id="reviewVehicle" name="vehicle" placeholder="e.g. 2022 Silverado 1500" />
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label for="reviewService">Service Type</label>
                    <select id="reviewService" name="service_type">
                      <option value="">Select...</option>
                      ${taxonomy.map(t => `<option value="${t.id}">${t.label}</option>`).join('')}
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Rating</label>
                    <div class="star-picker" id="starPicker">
                      ${[1,2,3,4,5].map(n => `<button type="button" class="star-pick" data-value="${n}" aria-label="${n} star${n > 1 ? 's' : ''}">&#9733;</button>`).join('')}
                    </div>
                    <input type="hidden" name="rating" id="reviewRating" required value="" />
                  </div>
                </div>
                <div class="form-group">
                  <label for="reviewTitle">Review Title</label>
                  <input type="text" id="reviewTitle" name="title" required placeholder="Summarize your experience" />
                </div>
                <div class="form-group">
                  <label for="reviewBody">Your Review</label>
                  <textarea id="reviewBody" name="body" rows="4" required placeholder="Tell us about the service you received..."></textarea>
                </div>
                <button type="submit" class="btn btn-gold">Submit Review</button>
              </form>
            </div>
          </div>

          <aside class="profile-sidebar">
            <div class="sidebar-box">
              <h3 class="sidebar-title">Hours</h3>
              <div class="hours-list">
                <div class="hours-row"><span>Mon – Fri</span><span>${mech.hours.mon_fri}</span></div>
                <div class="hours-row"><span>Saturday</span><span>${mech.hours.sat}</span></div>
                <div class="hours-row"><span>Sunday</span><span>${mech.hours.sun}</span></div>
              </div>
            </div>
            <div class="sidebar-box">
              <h3 class="sidebar-title">Quick Facts</h3>
              <div class="fact-row"><span class="fact-label">In Business</span><span>${mech.years_in_business} years</span></div>
              <div class="fact-row"><span class="fact-label">Verified</span><span>${mech.verified ? 'Yes' : 'Pending'}</span></div>
              <div class="fact-row"><span class="fact-label">Certified</span><span>${mech.certified ? 'GM Certified' : '—'}</span></div>
            </div>
            ${related.length ? `
            <div class="sidebar-box">
              <h3 class="sidebar-title">Nearby Shops</h3>
              ${relatedHTML}
            </div>` : ''}
          </aside>
        </div>`;

      // Star picker interaction
      const starPicker = document.getElementById('starPicker');
      const ratingInput = document.getElementById('reviewRating');
      if (starPicker) {
        starPicker.addEventListener('click', e => {
          const btn = e.target.closest('.star-pick');
          if (!btn) return;
          const val = parseInt(btn.dataset.value);
          ratingInput.value = val;
          starPicker.querySelectorAll('.star-pick').forEach((b, i) => {
            b.classList.toggle('active', i < val);
          });
        });
      }

      // Form submission
      const form = document.getElementById('reviewForm');
      if (form) {
        form.addEventListener('submit', e => {
          if (!ratingInput.value) {
            e.preventDefault();
            alert('Please select a star rating.');
          }
        });
      }
    });
  }

  // ── Homepage Spotlight Init ────────────────────────────
  function initHomepageSpotlight() {
    const el = document.getElementById('homepageMechanicSpotlight');
    if (!el) return;
    loadAllData().then(() => {
      el.innerHTML = renderSpotlight(allMechanics);
    });
  }

  // ── Boot ───────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    initDirectory();
    initProfile();
    initHomepageSpotlight();
  });

  // Expose for external use
  window.ChevyMechanics = { loadAllData, calcComposite, starsHTML, specialtyLabel };
})();
