(async () => {
  // Hide third-party popups/widgets that are not part of the site design
  const hide = [...document.querySelectorAll("body > *")].filter((e) => {
    const cs = getComputedStyle(e);
    return cs.position === "fixed" && !e.matches("header, .mainHeader, .btPageWrap");
  });
  hide.forEach((e) => (e.style.display = "none"));
  document.querySelectorAll("[id*='popup'],[class*='popup'],[id*='be-promo'],[class*='promo-widget']").forEach((e) => { if (!e.closest('.btPageWrap')) e.style.display = "none"; });
  // freeze sliders on first slide
  document.querySelectorAll(".slick-slider").forEach((s) => { try { window.jQuery && jQuery(s).slick("slickPause").slick("slickGoTo", 0, true); } catch (e) {} });
  document.querySelectorAll(".owl-carousel").forEach((s) => { try { window.jQuery && jQuery(s).trigger("stop.owl.autoplay").trigger("to.owl.carousel", [0, 0]); } catch (e) {} });
  await new Promise((r) => setTimeout(r, 800));
})()
