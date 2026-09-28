// Support Team Dashboard Logic

document.addEventListener('DOMContentLoaded', () => {
  // Enforce Support Team authentication
  if (!Auth.checkAuth('support')) return;

  const supportUser = Auth.getUser();
  const nameEl = document.getElementById('support-name-display');
  if (nameEl && supportUser) {
    nameEl.textContent = supportUser.name;
  }

  // Dashboard UI elements
  const statTotal = document.getElementById('stat-total');
  const statPos = document.getElementById('stat-pos');
  const statNeu = document.getElementById('stat-neu');
  const statNeg = document.getElementById('stat-neg');

  const colPos = document.getElementById('col-positive-body');
  const colNeu = document.getElementById('col-neutral-body');
  const colNeg = document.getElementById('col-negative-body');

  const countPos = document.getElementById('count-pos');
  const countNeu = document.getElementById('count-neu');
  const countNeg = document.getElementById('count-neg');

  const searchInput = document.getElementById('search-input');
  const filterSentiment = document.getElementById('filter-sentiment');
  const sortDirection = document.getElementById('sort-direction');
  const refreshBtn = document.getElementById('refresh-btn');

  let debounceTimer;

  // Event Listeners for Filters
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(loadDashboardData, 300);
    });
  }

  if (filterSentiment) {
    filterSentiment.addEventListener('change', loadDashboardData);
  }

  if (sortDirection) {
    sortDirection.addEventListener('change', loadDashboardData);
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadDashboardData);
  }

  // Main Dashboard Data Loading Function
  async function loadDashboardData() {
    await Promise.all([fetchStats(), fetchFeedback()]);
  }

  // Fetch Stats Counters
  async function fetchStats() {
    try {
      const res = await fetch('/support/stats', {
        headers: Auth.getHeaders()
      });
      if (!res.ok) return;
      const data = await res.json();

      if (statTotal) statTotal.textContent = data.total;
      if (statPos) statPos.textContent = data.positive;
      if (statNeu) statNeu.textContent = data.neutral;
      if (statNeg) statNeg.textContent = data.negative;
    } catch (err) {
      console.error('Error fetching support stats:', err);
    }
  }

  // Fetch Feedback & Organize into 3 Columns
  async function fetchFeedback() {
    try {
      const search = searchInput ? searchInput.value.trim() : '';
      const sentiment = filterSentiment ? filterSentiment.value : '';
      const sort = sortDirection ? sortDirection.value : 'desc';

      let url = `/support/feedback?sort=${sort}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (sentiment) url += `&sentiment=${sentiment}`;

      const res = await fetch(url, {
        headers: Auth.getHeaders()
      });

      if (!res.ok) return;

      const records = await res.json();

      const positiveList = records.filter(item => item.sentiment === 'positive');
      const neutralList = records.filter(item => item.sentiment === 'neutral');
      const negativeList = records.filter(item => item.sentiment === 'negative');

      // Update Column Counts
      if (countPos) countPos.textContent = positiveList.length;
      if (countNeu) countNeu.textContent = neutralList.length;
      if (countNeg) countNeg.textContent = negativeList.length;

      // Render Columns
      renderColumn(colPos, positiveList, 'No positive testimonials match criteria.');
      renderColumn(colNeu, neutralList, 'No neutral feedback matches criteria.');
      renderColumn(colNeg, negativeList, 'No negative improvement feedback matches criteria.');

    } catch (err) {
      console.error('Error fetching support feedback:', err);
    }
  }

  function renderColumn(container, items, emptyMessage) {
    if (!container) return;

    if (!items || items.length === 0) {
      container.innerHTML = `<div class="empty-state">${emptyMessage}</div>`;
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="feedback-card">
        <div class="feedback-meta">
          <div class="customer-info">
            <span class="customer-name">${escapeHtml(item.customer_name || 'Customer')}</span>
            <span class="customer-email">${escapeHtml(item.customer_email || '')}</span>
          </div>
          <span class="sentiment-pill ${item.sentiment}">${item.sentiment}</span>
        </div>
        <div class="feedback-text">"${escapeHtml(item.feedback_text)}"</div>
        <div class="feedback-date">Submitted: ${new Date(item.created_at).toLocaleString()}</div>
      </div>
    `).join('');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
  }

  // Initial load & automatic refresh every 15 seconds
  loadDashboardData();
  setInterval(loadDashboardData, 15000);
});
