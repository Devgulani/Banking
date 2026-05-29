(() => {
  const body = document.body;
  const backdrop = document.getElementById("sidebar-backdrop");
  const toggle = document.getElementById("sidebar-toggle");
  const navLinks = document.querySelectorAll(".sidebar-link[data-nav]");
  const sections = ["overview", "transactions", "quick-actions", "dashboard-analytics"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  const setSidebarOpen = (open) => {
    body.classList.toggle("sidebar-open", open);
    toggle?.setAttribute("aria-expanded", open ? "true" : "false");
    if (backdrop) backdrop.hidden = !open;
  };

  const setActiveNav = (slug) => {
    navLinks.forEach((link) => {
      link.classList.toggle("is-active", link.dataset.nav === slug);
    });
  };

  toggle?.addEventListener("click", () => {
    setSidebarOpen(!body.classList.contains("sidebar-open"));
  });

  document.querySelectorAll("[data-sidebar-close]").forEach((el) => {
    el.addEventListener("click", () => setSidebarOpen(false));
  });

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (link.dataset.nav) setActiveNav(link.dataset.nav);
      if (window.matchMedia("(max-width: 879px)").matches) setSidebarOpen(false);
    });
  });

  const slugForSection = (id) => {
    if (id === "overview") return "overview";
    if (id === "transactions") return "transactions";
    if (id === "quick-actions") return "actions";
    if (id === "dashboard-analytics") return "analytics";
    return null;
  };

  if (sections.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) {
          const slug = slugForSection(visible.target.id);
          if (slug) setActiveNav(slug);
        }
      },
      { rootMargin: "-28% 0px -55% 0px", threshold: [0.1, 0.35, 0.6] }
    );
    sections.forEach((section) => observer.observe(section));
  }

  document.querySelectorAll(".action-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const label = btn.querySelector(".action-label")?.textContent ?? "Action";
      btn.classList.add("is-pressed");
      window.setTimeout(() => btn.classList.remove("is-pressed"), 220);
      btn.setAttribute("aria-live", "polite");
      btn.dataset.feedback = `${label} ready`;
    });
  });

  document.querySelectorAll(".reveal").forEach((el) => {
    el.classList.add("is-visible");
  });
})();
