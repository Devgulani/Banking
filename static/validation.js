(() => {
  const rules = {
    username(value) {
      if (!value) return "Username is required.";
      if (value.length < 5) return "Username must be at least 5 characters.";
      if (!/^[A-Za-z0-9_]+$/.test(value)) return "Use only letters, numbers, and underscores.";
      return "";
    },
    email(value) {
      if (!value) return "Email is required.";
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return "Enter a valid email address.";
      return "";
    },
    account_number(value) {
      if (!value) return "Account number is required.";
      if (!/^\d+$/.test(value)) return "Account number must contain numbers only.";
      return "";
    },
    password(value, relaxed = false) {
      if (!value) return "Password is required.";
      if (value.length < 8) return "Password must be at least 8 characters.";
      if (relaxed) return "";
      if (!/[A-Z]/.test(value)) return "Add at least one uppercase letter.";
      if (!/[a-z]/.test(value)) return "Add at least one lowercase letter.";
      if (!/\d/.test(value)) return "Add at least one number.";
      if (!/[^A-Za-z0-9]/.test(value)) return "Add at least one special character.";
      return "";
    },
    confirm_password(value, form) {
      if (!value) return "Please confirm your password.";
      if (value !== form.elements.password?.value) return "Passwords do not match.";
      return "";
    },
    sender(value) {
      return value ? "" : "Choose a sender account.";
    },
    receiver(value) {
      if (!value) return "Receiver account is required.";
      if (!/^\d+$/.test(value)) return "Receiver account must be numeric.";
      if (value.length < 6) return "Receiver account looks too short.";
      return "";
    },
    amount(value) {
      if (!value) return "Amount is required.";
      const amount = Number(value);
      if (!Number.isFinite(amount) || amount <= 0) return "Enter an amount greater than zero.";
      if (amount > 125200) return "Amount exceeds available balance.";
      return "";
    },
    remarks(value) {
      if (value.length > 120) return "Remarks must stay under 120 characters.";
      return "";
    },
    subject(value) {
      if (!value) return "Subject is required.";
      if (value.length < 4) return "Subject must be at least 4 characters.";
      return "";
    },
    message(value) {
      if (!value) return "Message is required.";
      if (value.length < 12) return "Message must be at least 12 characters.";
      return "";
    },
  };

  const fieldNames = {
    login: ["username", "password"],
    signup: ["username", "email", "account_number", "password", "confirm_password"],
    transfer: ["sender", "receiver", "amount", "remarks"],
    support: ["subject", "message"],
  };

  const scorePassword = (value) => {
    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[a-z]/.test(value)) score += 1;
    if (/\d/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;
    return score;
  };

  const setError = (form, name, message) => {
    const field = form.elements[name];
    const error = form.querySelector(`[data-error-for="${name}"]`);
    field?.classList.toggle("is-invalid", Boolean(message));
    field?.classList.toggle("is-valid", !message && Boolean(field.value));
    if (error) error.textContent = message;
  };

  const validateField = (form, name, type) => {
    const field = form.elements[name];
    if (!field || !rules[name]) return true;
    const value = field.value.trim();
    let message = "";
    if (name === "password") {
      message = rules.password(value, type === "login");
    } else if (name === "confirm_password") {
      message = rules.confirm_password(value, form);
    } else {
      message = rules[name](value, form);
    }
    setError(form, name, message);
    return !message;
  };

  const updateStrength = (form) => {
    const password = form.elements.password;
    const meter = form.querySelector(".strength-meter span");
    const label = form.querySelector(".strength-label");
    if (!password || !meter || !label) return;

    const score = scorePassword(password.value);
    const names = ["Very weak", "Weak", "Fair", "Good", "Strong"];
    meter.style.width = `${Math.max(score, 1) * 20}%`;
    meter.dataset.score = String(score);
    label.textContent = password.value ? names[Math.max(score - 1, 0)] : "Password strength";
  };

  const validateForm = (form, type) => {
    const valid = fieldNames[type].every((name) => validateField(form, name, type));
    const submit = form.querySelector("[type='submit']");
    if (submit) submit.disabled = !valid;
    updateStrength(form);
    return valid;
  };

  const enhanceForm = (form, type) => {
    const names = fieldNames[type];
    names.forEach((name) => {
      const field = form.elements[name];
      field?.addEventListener("input", () => validateForm(form, type));
      field?.addEventListener("blur", () => validateField(form, name, type));
    });

    form.querySelectorAll(".password-toggle").forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const input = toggle.parentElement.querySelector("input");
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        toggle.textContent = show ? "Hide" : "Show";
        toggle.setAttribute("aria-label", show ? "Hide password" : "Show password");
      });
    });

    form.addEventListener("submit", (event) => {
      if (!validateForm(form, type)) {
        event.preventDefault();
        return;
      }

      const submit = form.querySelector("[type='submit']");
      submit?.classList.add("is-loading");

      if (type === "transfer" || type === "support") {
        event.preventDefault();
        window.setTimeout(() => {
          submit?.classList.remove("is-loading");
          const success = form.closest(".card")?.querySelector(".form-success");
          if (success) success.hidden = false;
          form.reset();
          validateForm(form, type);
        }, 550);
      }
    });

    validateForm(form, type);
  };

  document.querySelectorAll(".js-auth-form").forEach((form) => {
    enhanceForm(form, form.dataset.formType || "login");
  });
  document.querySelectorAll(".js-transfer-form").forEach((form) => enhanceForm(form, "transfer"));
  document.querySelectorAll(".js-support-form").forEach((form) => enhanceForm(form, "support"));
})();
