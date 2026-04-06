/**
 * newsletter.js — ChevyRoots newsletter signup handler
 * Handles form submissions across all pages, stores to localStorage
 * until a real email service (Resend or similar) is connected.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'chevyroots_newsletter_subscribers';
  const SOURCE_KEY = 'chevyroots_signup_source';

  /* ----------------------------------------------------------------
     Utilities
  ---------------------------------------------------------------- */

  function getSubscribers() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function saveSubscribers(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function getCount() {
    return getSubscribers().length;
  }

  function isDuplicate(email) {
    const normalized = email.trim().toLowerCase();
    return getSubscribers().some(function (sub) {
      return sub.email === normalized;
    });
  }

  function addSubscriber(email, source) {
    const subscribers = getSubscribers();
    subscribers.push({
      email: email.trim().toLowerCase(),
      source: source || window.location.pathname,
      timestamp: new Date().toISOString(),
    });
    saveSubscribers(subscribers);
  }

  /* ----------------------------------------------------------------
     Success message
  ---------------------------------------------------------------- */

  function showSuccess(form) {
    var existing = form.parentNode.querySelector('.newsletter-success-msg');
    if (existing) existing.remove();

    var msg = document.createElement('div');
    msg.className = 'newsletter-success-msg';
    msg.setAttribute('role', 'status');
    msg.setAttribute('aria-live', 'polite');
    msg.innerHTML =
      '<span class="newsletter-success-icon">&#10003;</span>' +
      '<span class="newsletter-success-text">You\'re in! First issue arrives Thursday.</span>';

    // Inline styles so the message works even without a dedicated stylesheet
    msg.style.cssText = [
      'display:flex',
      'align-items:center',
      'gap:0.6rem',
      'margin-top:1rem',
      'padding:0.9rem 1.25rem',
      'background:rgba(196,160,53,0.12)',
      'border:1px solid rgba(196,160,53,0.45)',
      'border-radius:4px',
      'font-family:"Inter",sans-serif',
      'font-size:0.9rem',
      'color:#F0EDE6',
      'opacity:0',
      'transition:opacity 300ms ease',
    ].join(';');

    var icon = msg.querySelector('.newsletter-success-icon');
    if (icon) {
      icon.style.cssText = [
        'display:inline-flex',
        'align-items:center',
        'justify-content:center',
        'width:22px',
        'height:22px',
        'min-width:22px',
        'background:#C4A035',
        'color:#1A1A1A',
        'border-radius:50%',
        'font-size:0.75rem',
        'font-weight:700',
      ].join(';');
    }

    form.parentNode.insertBefore(msg, form.nextSibling);

    // Fade in
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        msg.style.opacity = '1';
      });
    });

    // Hide the form inputs so it looks clean
    var input = form.querySelector('input[type="email"]');
    var btn = form.querySelector('button[type="submit"]');
    if (input) {
      input.disabled = true;
      input.style.opacity = '0.45';
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Subscribed';
      btn.style.opacity = '0.7';
    }
  }

  function showDuplicate(form) {
    var existing = form.parentNode.querySelector('.newsletter-dup-msg');
    if (existing) return;

    var msg = document.createElement('div');
    msg.className = 'newsletter-dup-msg';
    msg.setAttribute('role', 'status');
    msg.setAttribute('aria-live', 'polite');
    msg.textContent = 'That email is already subscribed.';
    msg.style.cssText = [
      'margin-top:0.75rem',
      'font-family:"Inter",sans-serif',
      'font-size:0.85rem',
      'color:#C4A035',
      'opacity:0',
      'transition:opacity 300ms ease',
    ].join(';');

    form.parentNode.insertBefore(msg, form.nextSibling);

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        msg.style.opacity = '1';
      });
    });

    setTimeout(function () {
      msg.style.opacity = '0';
      setTimeout(function () { msg.remove(); }, 300);
    }, 4000);
  }

  /* ----------------------------------------------------------------
     Update subscriber count displays
  ---------------------------------------------------------------- */

  function updateCountDisplays() {
    var count = getCount();
    var els = document.querySelectorAll('[data-subscriber-count]');
    els.forEach(function (el) {
      el.textContent = count.toLocaleString();
    });
  }

  /* ----------------------------------------------------------------
     Form handler
  ---------------------------------------------------------------- */

  function handleFormSubmit(e) {
    e.preventDefault();

    var form = e.currentTarget;
    var emailInput = form.querySelector('input[type="email"]');
    if (!emailInput) return;

    var email = emailInput.value.trim();
    if (!email) return;

    // Basic format check (browser does this too, but belt-and-suspenders)
    var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRe.test(email)) return;

    if (isDuplicate(email)) {
      showDuplicate(form);
      return;
    }

    var source = form.dataset.signupSource || window.location.pathname;
    addSubscriber(email, source);
    updateCountDisplays();
    showSuccess(form);
  }

  /* ----------------------------------------------------------------
     Attach to all newsletter forms on the page
  ---------------------------------------------------------------- */

  function attachForms() {
    // Matches forms with class "newsletter-form" or data-newsletter-form attribute
    var forms = document.querySelectorAll('.newsletter-form, [data-newsletter-form]');
    forms.forEach(function (form) {
      form.removeEventListener('submit', handleFormSubmit); // prevent double-bind
      form.addEventListener('submit', handleFormSubmit);
    });

    updateCountDisplays();
  }

  /* ----------------------------------------------------------------
     Init — run on DOMContentLoaded or immediately if already loaded
  ---------------------------------------------------------------- */

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachForms);
  } else {
    attachForms();
  }

  /* ----------------------------------------------------------------
     Public API (accessible as window.ChevyNewsletter)
  ---------------------------------------------------------------- */

  window.ChevyNewsletter = {
    getCount: getCount,
    getSubscribers: getSubscribers,
    isDuplicate: isDuplicate,
    /**
     * Programmatically re-attach forms (useful after dynamic content loads)
     */
    init: attachForms,
    /**
     * Debug: log all stored subscribers to the console
     */
    debug: function () {
      var subs = getSubscribers();
      console.groupCollapsed('ChevyRoots Newsletter — ' + subs.length + ' subscriber(s)');
      if (subs.length === 0) {
        console.log('No subscribers yet.');
      } else {
        subs.forEach(function (s, i) {
          console.log((i + 1) + '.', s.email, '|', s.source, '|', s.timestamp);
        });
      }
      console.groupEnd();
    },
  };

})();
