document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".fade-up");

  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
          obs.unobserve(entry.target); // animate once
        }
      });
    },
    {
      threshold: 0.15,
      rootMargin: "0px 0px -50px 0px"
    }
  );

  elements.forEach(el => observer.observe(el));
});
