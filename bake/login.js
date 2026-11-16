(function () {
  "use strict";

  // ===== CHANGE THESE TWO LINES =====
  var API_BASE = "https://the-bakery-management-system-production.up.railway.app";   // your Railway URL once deployed, e.g. "https://your-app.up.railway.app"
  var GOOGLE_CLIENT_ID = "184093230182-lki408sm2dr93de6s47kd66t283duhma.apps.googleusercontent.com";
  // ==================================

  var errorBox = document.getElementById("login-error");

  function showError(text) { errorBox.textContent = text || ""; }

  // Save the session the same way for Google and email logins, then go home.
  function finishLogin(data) {
    try {
      localStorage.setItem("bakery-token", data.access_token);
      localStorage.setItem("bakery-user", JSON.stringify(data.user));
    } catch (e) {}
    window.location.href = "index.html";
  }

  function postJson(path, body) {
    return fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    }).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) { throw new Error(data.detail || "Something went wrong"); }
        return data;
      });
    });
  }

  // ----- Google sign in -----
  function handleGoogleResponse(response) {
    showError("");
    postJson("/auth/google", { credential: response.credential })
      .then(finishLogin)
      .catch(function (err) { showError(err.message); });
  }

  // Google calls this automatically once its script has loaded.
  window.onGoogleLibraryLoad = function () {
    google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback: handleGoogleResponse
    });
    google.accounts.id.renderButton(document.getElementById("google-btn"), {
      theme: "outline",
      size: "large",
      text: "continue_with",
      width: 320
    });
  };

  // ----- Email + password sign in -----
  document.getElementById("login-form").addEventListener("submit", function (event) {
    event.preventDefault();
    showError("");
    var email = document.getElementById("email").value.trim();
    var password = document.getElementById("password").value;
    if (!email || !password) { showError("Enter your email and password."); return; }
    postJson("/auth/login", { email: email, password: password })
      .then(finishLogin)
      .catch(function (err) { showError(err.message); });
  });
})();