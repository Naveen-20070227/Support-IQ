// Authentication Helper Utilities

const TOKEN_KEY = 'sentiment_app_token';
const USER_KEY = 'sentiment_app_user';

const Auth = {
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  getUser() {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  },

  setAuth(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = '/index.html';
  },

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },

  checkAuth(requiredRole = null) {
    const token = this.getToken();
    const user = this.getUser();

    if (!token || !user) {
      if (requiredRole) {
        if (requiredRole === 'support') {
          window.location.href = '/support-login.html';
        } else {
          window.location.href = '/customer-login.html';
        }
      }
      return false;
    }

    if (requiredRole && user.role !== requiredRole) {
      if (user.role === 'customer') {
        window.location.href = '/feedback.html';
      } else if (user.role === 'support') {
        window.location.href = '/dashboard.html';
      }
      return false;
    }

    return true;
  },

  showAlert(elementId, message, type = 'danger') {
    const alertEl = document.getElementById(elementId);
    if (!alertEl) return;
    alertEl.className = `alert alert-${type}`;
    alertEl.innerHTML = `
      <span class="alert-icon-badge">${type === 'danger' ? '!' : '✓'}</span>
      <div>${message}</div>
    `;
    alertEl.style.display = 'flex';
  },


  hideAlert(elementId) {
    const alertEl = document.getElementById(elementId);
    if (alertEl) {
      alertEl.style.display = 'none';
    }
  }
};
