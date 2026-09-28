// Customer Feedback Page Logic

document.addEventListener('DOMContentLoaded', () => {
  // Enforce customer role authentication
  if (!Auth.checkAuth('customer')) return;

  const user = Auth.getUser();
  const userNameEl = document.getElementById('user-name-display');
  if (userNameEl && user) {
    userNameEl.textContent = user.name;
  }

  const feedbackForm = document.getElementById('feedback-form');
  const feedbackInput = document.getElementById('feedback-text');
  const charCounter = document.getElementById('char-counter');
  const submitBtn = document.getElementById('submit-btn');
  const submitBtnText = document.getElementById('submit-btn-text');
  const submitBtnSpinner = document.getElementById('submit-btn-spinner');
  const myFeedbackContainer = document.getElementById('my-feedback-list');

  // Character counter update
  if (feedbackInput && charCounter) {
    feedbackInput.addEventListener('input', () => {
      const len = feedbackInput.value.length;
      charCounter.textContent = `${len} / 2000`;
      if (len > 2000) {
        charCounter.style.color = 'var(--neg-color)';
      } else {
        charCounter.style.color = 'var(--text-dim)';
      }
    });
  }

  // Handle feedback form submission
  if (feedbackForm) {
    feedbackForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      Auth.hideAlert('feedback-alert');

      const text = feedbackInput.value.strip ? feedbackInput.value.strip() : feedbackInput.value.trim();

      if (!text) {
        Auth.showAlert('feedback-alert', 'Please enter your review text before submitting.');
        return;
      }

      if (text.length > 2000) {
        Auth.showAlert('feedback-alert', 'Review exceeds maximum character limit of 2000 characters.');
        return;
      }

      // Set loading state
      submitBtn.disabled = true;
      submitBtnText.textContent = 'Analyzing & Submitting...';
      submitBtnSpinner.style.display = 'inline-block';

      try {
        const res = await fetch('/feedback', {
          method: 'POST',
          headers: Auth.getHeaders(),
          body: JSON.stringify({ feedback_text: text })
        });

        const data = await res.json();

        if (!res.ok) {
          Auth.showAlert('feedback-alert', data.detail || 'Failed to submit review.');
          return;
        }

        // Success state
        feedbackInput.value = '';
        if (charCounter) charCounter.textContent = '0 / 2000';
        
        Auth.showAlert(
          'feedback-alert',
          `Thank you for your feedback! Your review was recorded and automatically analyzed as <strong style="text-transform: capitalize;">${data.sentiment}</strong>.`,
          'success'
        );

        // Reload submission history
        loadMyHistory();

      } catch (err) {
        console.error('Submission error:', err);
        Auth.showAlert('feedback-alert', 'Network error while connecting to server. Please try again.');
      } finally {
        submitBtn.disabled = false;
        submitBtnText.textContent = 'Submit Review';
        submitBtnSpinner.style.display = 'none';
      }
    });
  }

  // Load Customer's Submission History
  async function loadMyHistory() {
    if (!myFeedbackContainer) return;

    try {
      const res = await fetch('/feedback/my', {
        headers: Auth.getHeaders()
      });

      if (!res.ok) return;

      const records = await res.json();
      if (!records || records.length === 0) {
        myFeedbackContainer.innerHTML = '<div class="empty-state">You have not submitted any reviews yet.</div>';
        return;
      }

      myFeedbackContainer.innerHTML = records.map(item => `
        <div class="feedback-card">
          <div class="feedback-meta">
            <span class="sentiment-pill ${item.sentiment}">${item.sentiment}</span>
            <span class="feedback-date">${new Date(item.created_at).toLocaleString()}</span>
          </div>
          <div class="feedback-text">${escapeHtml(item.feedback_text)}</div>
        </div>
      `).join('');

    } catch (err) {
      console.error('Error loading history:', err);
    }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
  }

  loadMyHistory();
});
