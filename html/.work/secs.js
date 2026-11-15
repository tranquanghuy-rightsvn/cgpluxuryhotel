(() => { const g = (s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.top + scrollY), Math.round(r.height)]; };
const m = location.host.includes('diamond');
const o = m ? { header: [0, 144], banner: g('.banner-slider'), intro: g('.bt_bb_wrapper > section:nth-of-type(2)'), featured: g('.bt_bb_wrapper > section:nth-of-type(3)'), services: g('.bt_bb_wrapper > section:nth-of-type(4)'), tiles: g('.bt_bb_wrapper > section:nth-of-type(5)'), rooms: g('.bt_bb_wrapper > section:nth-of-type(6)'), news: g('.bt_bb_wrapper > section:nth-of-type(7)'), footer: g('.btSiteFooterWidgets') }
 : { header: [0, 144], banner: g('.banner'), intro: g('.intro'), featured: g('.posts-sec'), services: g('.svc-head'), tiles: g('.svc-tiles'), rooms: g('.rooms'), news: g('.news-sec'), footer: g('.site-footer') };
return JSON.stringify(o); })()
