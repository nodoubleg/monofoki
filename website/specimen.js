"use strict";

const root = document.documentElement;
const systemTheme = window.matchMedia("(prefers-color-scheme: light)");
const buttons = document.querySelectorAll("[data-theme-choice]");
function currentTheme() {
  return root.dataset.theme || (systemTheme.matches ? "light" : "dark");
}
function syncTheme() {
  buttons.forEach((button) =>
    button.setAttribute(
      "aria-pressed",
      String(button.dataset.themeChoice === currentTheme()),
    ),
  );
}
buttons.forEach((button) =>
  button.addEventListener("click", () => {
    root.dataset.theme = button.dataset.themeChoice;
    try {
      localStorage.setItem("monofoki-theme", root.dataset.theme);
    } catch (_) {
      /* Private browsing can disable storage. */
    }
    syncTheme();
  }),
);
systemTheme.addEventListener("change", syncTheme);
syncTheme();

const sample = document.querySelector("#type-sample");
const original = sample.value;
const style = document.querySelector("#style");
const size = document.querySelector("#size");
function updateSample() {
  sample.style.fontWeight = style.value.includes("bold") ? "700" : "400";
  sample.style.fontStyle = style.value.includes("italic") ? "italic" : "normal";
  sample.style.fontSize = `${size.value}px`;
  document.querySelector("#size-value").value = `${size.value} px`;
}
style.addEventListener("change", updateSample);
size.addEventListener("input", updateSample);
document.querySelector("#reset").addEventListener("click", () => {
  sample.value = original;
  style.value = "regular";
  size.value = "32";
  updateSample();
});
updateSample();

document
  .querySelector("#copy-demo")
  .addEventListener("click", async (event) => {
    const button = event.currentTarget;
    try {
      await navigator.clipboard.writeText(
        "python3 script_helper/terminal_demo.py --art",
      );
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = "Copy command";
      }, 2000);
    } catch (_) {
      button.textContent = "Select the command to copy";
    }
  });
