/**
 * affiliate.js — ChevyRoots affiliate link tracking
 *
 * All affiliate links on the site use the /go/ redirect pattern.
 * Click data is stored in localStorage for analytics until a
 * backend is wired up.
 *
 * NOTE: Replace AFFILIATE_IDS values with actual affiliate / partner
 * IDs when accounts are set up. Current values are placeholders.
 */

(function () {
  'use strict';

  const CLICK_LOG_KEY = 'chevyroots_affiliate_clicks';

  /* ----------------------------------------------------------------
     Affiliate ID placeholders
     Replace with actual IDs when accounts are approved.
  ---------------------------------------------------------------- */
  // NOTE: Replace with actual affiliate IDs when accounts are set up
  const AFFILIATE_IDS = {
    summitracing: '',   // e.g. 'chevyroots-20' — get from Summit Racing affiliate program
    jegs:         '',   // e.g. '?utm_source=chevyroots' — JEGS affiliate tag
    amazon:       '',   // e.g. 'chevyroots-20' — Amazon Associates tag
    classicind:   '',   // Classic Industries affiliate ID
    lmctruck:     '',   // LMC Truck affiliate ID
    weathertech:  '',   // WeatherTech affiliate ID
  };

  /* ----------------------------------------------------------------
     Retailer URL builders
  ---------------------------------------------------------------- */

  const RETAILERS = {
    'summit-racing': {
      name: 'Summit Racing',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.summitracing.com/search?keyword=' + encodeURIComponent(term);
        if (AFFILIATE_IDS.summitracing) base += '&affid=' + AFFILIATE_IDS.summitracing;
        return base;
      },
    },
    'jegs': {
      name: 'JEGS',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.jegs.com/search/' + encodeURIComponent(term);
        if (AFFILIATE_IDS.jegs) base += '/' + AFFILIATE_IDS.jegs;
        return base;
      },
    },
    'amazon': {
      name: 'Amazon',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.amazon.com/s?k=' + encodeURIComponent(term);
        if (AFFILIATE_IDS.amazon) base += '&tag=' + AFFILIATE_IDS.amazon;
        return base;
      },
    },
    'classic-industries': {
      name: 'Classic Industries',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.classicindustries.com/search?q=' + encodeURIComponent(term);
        if (AFFILIATE_IDS.classicind) base += '&ref=' + AFFILIATE_IDS.classicind;
        return base;
      },
    },
    'lmc-truck': {
      name: 'LMC Truck',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.lmctruck.com/search?q=' + encodeURIComponent(term);
        if (AFFILIATE_IDS.lmctruck) base += '&ref=' + AFFILIATE_IDS.lmctruck;
        return base;
      },
    },
    'weathertech': {
      name: 'WeatherTech',
      buildUrl: function (term, productId) {
        // NOTE: Replace with actual affiliate IDs when accounts are set up
        var base = 'https://www.weathertech.com/search/?q=' + encodeURIComponent(term);
        if (AFFILIATE_IDS.weathertech) base += '&ref=' + AFFILIATE_IDS.weathertech;
        return base;
      },
    },
  };

  /* ----------------------------------------------------------------
     Click log
  ---------------------------------------------------------------- */

  function getClickLog() {
    try {
      return JSON.parse(localStorage.getItem(CLICK_LOG_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function logClick(retailer, searchTerm, productId, sourcePage) {
    var log = getClickLog();
    log.push({
      retailer:   retailer,
      searchTerm: searchTerm,
      productId:  productId || null,
      sourcePage: sourcePage || window.location.pathname,
      timestamp:  new Date().toISOString(),
    });
    // Keep last 500 entries to avoid bloating localStorage
    if (log.length > 500) log = log.slice(log.length - 500);
    localStorage.setItem(CLICK_LOG_KEY, JSON.stringify(log));
  }

  /* ----------------------------------------------------------------
     Core function: createAffiliateLink
     Returns the destination URL for a given retailer + search term.
  ---------------------------------------------------------------- */

  /**
   * createAffiliateLink(retailer, searchTerm, productId)
   *
   * @param {string} retailer   — One of: 'summit-racing', 'jegs', 'amazon',
   *                              'classic-industries', 'lmc-truck', 'weathertech'
   * @param {string} searchTerm — Product search keyword
   * @param {string} [productId] — Optional specific product ID
   * @returns {string} Full destination URL
   */
  function createAffiliateLink(retailer, searchTerm, productId) {
    var r = RETAILERS[retailer.toLowerCase()];
    if (!r) {
      console.warn('ChevyAffiliate: unknown retailer "' + retailer + '"');
      return '#';
    }
    return r.buildUrl(searchTerm, productId);
  }

  /* ----------------------------------------------------------------
     /go/ redirect handler
     Any link with href starting /go/ is intercepted, logged, then
     the user is sent to the affiliate URL.

     URL format: /go/{retailer}/{encoded-search-term}[/{productId}]
     Example:    /go/summit-racing/350-small-block-headers
  ---------------------------------------------------------------- */

  function parseGoPath(pathname) {
    // Strip leading /go/
    var parts = pathname.replace(/^\/go\//, '').split('/');
    return {
      retailer:   parts[0] ? decodeURIComponent(parts[0]) : null,
      searchTerm: parts[1] ? decodeURIComponent(parts[1].replace(/-/g, ' ')) : null,
      productId:  parts[2] ? decodeURIComponent(parts[2]) : null,
    };
  }

  function handleGoClick(e) {
    var link = e.currentTarget;
    var href = link.getAttribute('href') || '';

    if (!href.startsWith('/go/')) return;

    e.preventDefault();

    var parsed = parseGoPath(href);
    if (!parsed.retailer || !parsed.searchTerm) {
      console.warn('ChevyAffiliate: could not parse /go/ path:', href);
      return;
    }

    logClick(parsed.retailer, parsed.searchTerm, parsed.productId, window.location.pathname);

    var destination = createAffiliateLink(parsed.retailer, parsed.searchTerm, parsed.productId);
    window.open(destination, '_blank', 'noopener,noreferrer');
  }

  function attachGoLinks() {
    var links = document.querySelectorAll('a[href^="/go/"]');
    links.forEach(function (link) {
      link.removeEventListener('click', handleGoClick);
      link.addEventListener('click', handleGoClick);
    });
  }

  /* ----------------------------------------------------------------
     Dashboard — outputs click stats to console
  ---------------------------------------------------------------- */

  function dashboard() {
    var log = getClickLog();

    if (log.length === 0) {
      console.log('%cChevyRoots Affiliate Dashboard — No clicks recorded yet.', 'color:#C4A035;font-weight:bold;');
      return;
    }

    // Aggregate by retailer
    var byRetailer = {};
    var byPage = {};
    log.forEach(function (entry) {
      byRetailer[entry.retailer] = (byRetailer[entry.retailer] || 0) + 1;
      byPage[entry.sourcePage] = (byPage[entry.sourcePage] || 0) + 1;
    });

    console.groupCollapsed('%cChevyRoots Affiliate Dashboard — ' + log.length + ' click(s)', 'color:#C4A035;font-weight:bold;');

    console.group('By Retailer');
    Object.keys(byRetailer).sort().forEach(function (k) {
      console.log(k + ':', byRetailer[k]);
    });
    console.groupEnd();

    console.group('By Source Page');
    Object.keys(byPage).sort().forEach(function (k) {
      console.log(k + ':', byPage[k]);
    });
    console.groupEnd();

    console.group('Last 10 clicks');
    log.slice(-10).reverse().forEach(function (entry, i) {
      console.log(
        (i + 1) + '.',
        entry.retailer,
        '|',
        entry.searchTerm,
        '|',
        entry.sourcePage,
        '|',
        entry.timestamp
      );
    });
    console.groupEnd();

    console.groupEnd();
  }

  /* ----------------------------------------------------------------
     Init
  ---------------------------------------------------------------- */

  function init() {
    attachGoLinks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* ----------------------------------------------------------------
     Public API
  ---------------------------------------------------------------- */

  window.ChevyAffiliate = {
    createAffiliateLink: createAffiliateLink,
    dashboard: dashboard,
    logClick: logClick,
    getClickLog: getClickLog,
    /**
     * Re-attach /go/ links (call after dynamic content renders)
     */
    init: attachGoLinks,
    /**
     * Convenience: build and open a link programmatically
     * e.g. ChevyAffiliate.go('summit-racing', '350 small block headers')
     */
    go: function (retailer, searchTerm, productId) {
      logClick(retailer, searchTerm, productId, window.location.pathname);
      var url = createAffiliateLink(retailer, searchTerm, productId);
      window.open(url, '_blank', 'noopener,noreferrer');
    },
  };

})();
