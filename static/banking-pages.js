(() => {
  document.querySelectorAll(".js-toggle-card").forEach((button) => {
    button.addEventListener("click", () => {
      const frozen = button.classList.toggle("is-frozen");
      button.textContent = frozen ? button.dataset.off : button.dataset.on;
      const state = document.querySelector(".card-state");
      if (state) state.textContent = frozen ? "Card is frozen. New purchases are blocked." : "Card is active and ready for use.";
    });
  });

  document.querySelectorAll(".js-limit-range").forEach((range) => {
    const readout = document.querySelector(".limit-readout");
    const update = () => {
      const value = Number(range.value).toLocaleString("en-IN");
      if (readout) readout.textContent = `Rs.${value}`;
    };
    range.addEventListener("input", update);
    update();
  });
})();
