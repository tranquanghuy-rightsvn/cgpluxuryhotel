(async () => {
  [...document.querySelectorAll("body > *")].forEach((e) => { const cs = getComputedStyle(e); if (cs.position === "fixed" && !e.matches("header, .mainHeader, .btPageWrap, .site-header")) e.style.display = "none"; });
  const st = document.createElement("style");
  st.textContent = "img{opacity:0!important} iframe:not(#be-search-form iframe){visibility:hidden!important} .slick-slide.item,.banner-slide,.bg-cover-top,.btImage,.post-img,.room-img,.tile,.intro-slider,.rowItem[style*=background-image]{background:#7a7a7a!important} .site-slider,.banner{background:#7a7a7a!important} .banner-slide{opacity:1!important}";
  document.head.appendChild(st);
  document.querySelectorAll("[style*='background-image']").forEach((e) => { if (!e.closest('.btn,.sf-calendar-button')) e.style.backgroundImage = "none"; });
  document.querySelectorAll(".map").forEach((e) => (e.style.background = "#e5e5e5"));
  await new Promise((r) => setTimeout(r, 500));
})()
