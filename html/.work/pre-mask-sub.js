(async () => {
  const s = document.createElement("style");
  s.textContent = ".sub-menu,.menu .sub-menu{display:none!important} header.mainHeader,header.site-header{visibility:hidden!important} .banner-page{background:#333!important} .banner-page::before{display:none!important}";
  document.head.appendChild(s);
})()
