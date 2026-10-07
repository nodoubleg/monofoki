"use strict";

(() => {
  const controls = document.querySelector(".symbol-controls");
  if (!controls) return;
  const search = document.querySelector("#symbol-search");
  const block = document.querySelector("#symbol-block");
  const donor = document.querySelector("#symbol-donor");
  const cards = Array.from(document.querySelectorAll(".symbol-card"));
  const groups = Array.from(document.querySelectorAll(".symbol-group"));
  const count = document.querySelector("#symbol-count");
  const copyStatus = document.querySelector("#copy-status");
  let statusTimer;
  controls.hidden = false;

  function filter() {
    const query = search.value.trim().toLowerCase();
    const code = /^(?:u\+|0x)?0*([0-9a-f]{4,6})$/i.exec(query);
    let shown = 0;
    cards.forEach((card) => {
      const matchesText = code
        ? parseInt(card.dataset.codepoint, 16) === parseInt(code[1], 16)
        : `${card.dataset.name} ${card.dataset.codepoint}`.toLowerCase().includes(query);
      card.hidden = !(
        matchesText &&
        (block.value === "all" || card.dataset.block === block.value) &&
        (donor.value === "all" || card.dataset.donor === donor.value)
      );
      if (!card.hidden) shown += 1;
    });
    groups.forEach((group) => {
      const visible = group.querySelectorAll(".symbol-card:not([hidden])").length;
      const total = group.querySelectorAll(".symbol-card").length;
      group.hidden = visible === 0;
      group.querySelector(".group-count").textContent = visible === total ? total : `${visible} / ${total}`;
    });
    count.textContent = `Showing ${shown} of ${cards.length} symbols`;
    document.querySelector("#symbol-empty").hidden = shown !== 0;
  }
  search.addEventListener("input", filter);
  block.addEventListener("change", filter);
  donor.addEventListener("change", filter);
  document.querySelector("#symbol-reset").addEventListener("click", () => {
    search.value = "";
    block.value = donor.value = "all";
    history.replaceState(null, "", location.pathname + location.search + "#catalogue");
    filter();
    search.focus();
  });

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.hidden = false;
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(String.fromCodePoint(parseInt(button.dataset.copy, 16)));
        copyStatus.textContent = `Copied U+${button.dataset.copy}`;
      } catch (_) {
        copyStatus.textContent = "Clipboard unavailable. Select the glyph to copy it.";
      }
      clearTimeout(statusTimer);
      statusTimer = setTimeout(() => { copyStatus.textContent = ""; }, 4000);
    });
  });

  function showLinkedGlyph() {
    const match = /^#u-([0-9a-f]+)$/i.exec(location.hash);
    if (!match || !document.getElementById(`u-${match[1].toLowerCase()}`)) return;
    search.value = `U+${match[1].toUpperCase()}`;
    block.value = donor.value = "all";
    filter();
    document.getElementById(`u-${match[1].toLowerCase()}`).scrollIntoView({ block: "center" });
  }
  window.addEventListener("hashchange", showLinkedGlyph);
  filter();
  showLinkedGlyph();

  const iconSearch = document.querySelector("#icon-search");
  if (iconSearch) {
    document.querySelector(".icon-search-label").hidden = false;
    const icons = Array.from(document.querySelectorAll(".nerd-icon"));
    iconSearch.addEventListener("input", () => {
      let query = iconSearch.value.trim().toLowerCase().replace(/^nf-/, "");
      query = query.replace(/^(?:u\+|0x)0*/, "");
      let shown = 0;
      icons.forEach((icon) => {
        icon.hidden = !icon.dataset.iconSearch.includes(query);
        if (!icon.hidden) shown += 1;
      });
      document.querySelectorAll(".icon-group").forEach((group) => {
        const visible = group.querySelectorAll(".nerd-icon:not([hidden])").length;
        group.hidden = visible === 0;
        if (query) group.open = visible !== 0;
        else group.open = false;
      });
      document.querySelector("#icon-count").textContent = `Showing ${shown} of ${icons.length} mapped Nerd glyphs`;
    });
  }
  const fallbackVariant = document.querySelector("#fallback-variant");
  if (fallbackVariant) {
    document.querySelector(".fallback-controls").hidden = false;
    const fallbackSearch = document.querySelector("#fallback-search");
    const previews = Array.from(document.querySelectorAll(".fallback-card"));
    function filterFallback() {
      const query = fallbackSearch.value.trim().toLowerCase().replace(/^(?:u\+|0x)0*/, "");
      let shown = 0;
      previews.forEach((preview) => {
        preview.hidden = preview.dataset.variant !== fallbackVariant.value || !preview.dataset.fallbackSearch.includes(query);
        if (!preview.hidden) shown += 1;
      });
      document.querySelector("#fallback-count").textContent = `Showing ${shown} characters absent from ${fallbackVariant.value === "regular" ? "Monofoki" : "Monofoki Nerd Font"}`;
    }
    fallbackVariant.addEventListener("change", filterFallback);
    fallbackSearch.addEventListener("input", filterFallback);
    filterFallback();
  }
})();
