// js/sort.js
// Fetch /json/merged_tweets.json and render a sortable/filterable list.
document.addEventListener('DOMContentLoaded', function () {
  // Use absolute path so this works from / or /tweets/ pages
  const DATA_URL = '/json/merged_tweets.json';
  const container = document.getElementById('tweets-container');
  const sortByEl = document.getElementById('sort-by');
  const sortOrderEl = document.getElementById('sort-order');
  const filterAuthorEl = document.getElementById('filter-author');
  const hideHashtagsEl = document.getElementById('hide-hashtags');
  const resetBtn = document.getElementById('reset-filters');

  let items = [];
  let lastFilteredFull = [];

  function getField(o, candidates) {
    for (const k of candidates) {
      if (o[k] !== undefined && o[k] !== null) return o[k];
    }
    return '';
  }

  function parseDate(item) {
    const d = getField(item, ['created_at', 'date', 'timestamp', 'created']);
    const parsed = Date.parse(d);
    return isNaN(parsed) ? 0 : parsed;
  }

  function getAuthor(item) {
    return String(getField(item, ['author', 'username', 'user', 'screen_name', 'name']) || '').trim();
  }

  function getText(item) {
    return String(getField(item, ['text', 'full_text', 'content', 'tweet']) || '').trim();
  }

  function getNumericField(item, candidates) {
    for (const k of candidates) {
      const v = item[k];
      if (v === undefined || v === null) continue;
      const n = Number(v);
      if (!isNaN(n)) return n;
    }
    return 0;
  }

  function getPopularityScore(item) {
    // score = likes + retweets * 3
    const likes = getNumericField(item, ['likes', 'favorite_count', 'favorites_count', 'likes_count']);
    const retweets = getNumericField(item, ['retweets', 'retweet_count', 'rt_count']);
    return likes + (retweets * 3);
  }

  // pagination state
  let currentPage = 1;
  let pageSize = 25;

  function renderList(data) {
    container.innerHTML = '';
    if (!data || data.length === 0) {
      container.innerHTML = '<div class="empty">表示するツイートはありません。</div>';
      return;
    }

  const table = document.createElement('table');
    table.className = 'tweets-table';
    const thead = document.createElement('thead');
    thead.innerHTML = '<tr><th class="col-date">日付</th><th class="col-author">投稿者</th><th class="col-text">本文</th></tr>';
    table.appendChild(thead);
    const tbody = document.createElement('tbody');

    for (const it of data) {
      const tr = document.createElement('tr');
      const dateCell = document.createElement('td');
      const dt = parseDate(it);
      dateCell.textContent = dt ? new Date(dt).toLocaleString() : '-';
      dateCell.className = 'col-date';

      const authorCell = document.createElement('td');
      authorCell.textContent = getAuthor(it) || '-';
      authorCell.className = 'col-author';

      const textCell = document.createElement('td');
      // optionally hide hashtags from displayed text (UI toggle)
      let text = getText(it) || '';
      try {
        if (hideHashtagsEl && hideHashtagsEl.checked) {
          // remove hashtag tokens (non-space sequences starting with #)
          text = text.replace(/#[^\s#]+/g, '').trim();
        }
      } catch (e) {
        // ignore regex errors
      }
      textCell.textContent = text;
      textCell.className = 'col-text';

      tr.appendChild(dateCell);
      tr.appendChild(authorCell);
      tr.appendChild(textCell);
      tbody.appendChild(tr);
      // clickable row: show details on click
      tr.addEventListener('click', function () {
        // if next sibling is detail row, toggle it
        const next = tr.nextElementSibling;
        if (next && next.classList.contains('tweet-detail')) {
          next.parentElement.removeChild(next);
          return;
        }
        // remove any existing detail rows
        const existing = table.querySelectorAll('.tweet-detail');
        existing.forEach(e => e.parentElement.removeChild(e));
        const detailTr = document.createElement('tr');
        detailTr.className = 'tweet-detail';
        const td = document.createElement('td');
        td.colSpan = 3;
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(it, null, 2);
        pre.className = 'tweet-json';
        td.appendChild(pre);
        detailTr.appendChild(td);
        tr.parentElement.insertBefore(detailTr, tr.nextSibling);
      });
    }

    table.appendChild(tbody);
    container.appendChild(table);
    renderPager();
  }

  function renderPager() {
    // remove existing pager if any
    const ex = container.querySelector('.tweets-pager');
    if (ex) ex.parentElement.removeChild(ex);
    const total = lastFilteredFull.length || 0;
    if (total <= pageSize) return; // no pager needed

    const pager = document.createElement('div');
    pager.className = 'tweets-pager';

    const info = document.createElement('div');
    info.className = 'pager-info';
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    info.textContent = `全 ${total} 件 — ${currentPage} / ${totalPages} ページ`;
    pager.appendChild(info);

    const controls = document.createElement('div');
    controls.className = 'pager-controls';

    const prev = document.createElement('button');
    prev.type = 'button'; prev.textContent = '前へ'; prev.disabled = currentPage <= 1;
    prev.addEventListener('click', () => { if (currentPage>1) { currentPage--; updatePage(); } });
    controls.appendChild(prev);

    // page numbers (limited)
    const start = Math.max(1, currentPage - 3);
    const end = Math.min(totalPages, currentPage + 3);
    for (let p = start; p <= end; p++) {
      const b = document.createElement('button');
      b.type = 'button'; b.textContent = String(p);
      if (p === currentPage) b.className = 'active';
      b.addEventListener('click', () => { currentPage = p; updatePage(); });
      controls.appendChild(b);
    }

    const next = document.createElement('button');
    next.type = 'button'; next.textContent = '次へ'; next.disabled = currentPage >= totalPages;
    next.addEventListener('click', () => { if (currentPage<totalPages) { currentPage++; updatePage(); } });
    controls.appendChild(next);

    // page size selector
    const sizeSel = document.createElement('select');
    [10,25,50,100].forEach(n => { const o = document.createElement('option'); o.value = String(n); o.text = String(n); if (n===pageSize) o.selected = true; sizeSel.appendChild(o); });
    sizeSel.addEventListener('change', () => { pageSize = Number(sizeSel.value); currentPage = 1; updatePage(); });

    const sizeWrap = document.createElement('div');
    sizeWrap.className = 'pager-size';
    sizeWrap.appendChild(document.createTextNode('表示数: '));
    sizeWrap.appendChild(sizeSel);

    pager.appendChild(controls);
    pager.appendChild(sizeWrap);

    container.appendChild(pager);
  }

  function updatePage() {
    const total = lastFilteredFull.length || 0;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;
    const slice = lastFilteredFull.slice((currentPage-1)*pageSize, currentPage*pageSize);
    renderList(slice);
  }

  function populateAuthorFilter(list) {
    const authors = new Set();
    list.forEach(i => { const a = getAuthor(i); if (a) authors.add(a); });
    // clear
    filterAuthorEl.innerHTML = '<option value="all">すべて</option>';
    Array.from(authors).sort().forEach(a => {
      const opt = document.createElement('option');
      opt.value = a;
      opt.textContent = a;
      filterAuthorEl.appendChild(opt);
    });
  }

  function applySortAndFilter() {
    const sortBy = sortByEl.value;
    const order = sortOrderEl.value;
    const filterAuthor = filterAuthorEl.value;

  let out = items.slice();
    if (filterAuthor && filterAuthor !== 'all') {
      out = out.filter(i => getAuthor(i) === filterAuthor);
    }

    out.sort((a, b) => {
      if (sortBy === 'date') {
        return parseDate(b) - parseDate(a);
      }
      if (sortBy === 'popularity') {
        return getPopularityScore(b) - getPopularityScore(a);
      }
      // author
      const A = getAuthor(a).toLowerCase();
      const B = getAuthor(b).toLowerCase();
      if (A < B) return -1;
      if (A > B) return 1;
      return 0;
    });

    // handle ascending/descending for each type
    if (order === 'asc') {
      out = out.reverse();
    }

  // reset page when filters change
  currentPage = 1;
  // store full filtered list for pager slicing
  lastFilteredFull = out;
  renderList(out.slice((currentPage-1)*pageSize, currentPage*pageSize));
  }

  function onError(e) {
    container.innerHTML = '<div class="error">読み込みエラー。コンソールを確認してください。</div>';
    console.error('Failed to load tweets JSON', e);
  }

  // Fetch data
  fetch(DATA_URL, { cache: 'no-store' })
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(json => {
      // expect array; if object with items key, try to find array
      if (Array.isArray(json)) items = json;
      else if (Array.isArray(json.items)) items = json.items;
      else if (Array.isArray(json.tweets)) items = json.tweets;
      else {
        // try to collect values that look like tweets
        items = Object.values(json).flat().filter(Boolean);
      }
      populateAuthorFilter(items);
      // store base items
      items = items;
      lastFilteredFull = items.slice();
      applySortAndFilter();
    })
    .catch(onError);

  // events
  sortByEl.addEventListener('change', applySortAndFilter);
  sortOrderEl.addEventListener('change', applySortAndFilter);
  filterAuthorEl.addEventListener('change', applySortAndFilter);
  if (hideHashtagsEl) hideHashtagsEl.addEventListener('change', applySortAndFilter);
  resetBtn.addEventListener('click', function () {
    sortByEl.value = 'date';
    sortOrderEl.value = 'desc';
    filterAuthorEl.value = 'all';
    if (hideHashtagsEl) hideHashtagsEl.checked = false;
    applySortAndFilter();
  });
});
