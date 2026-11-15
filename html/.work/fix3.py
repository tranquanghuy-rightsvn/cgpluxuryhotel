#!/usr/bin/env python3
def edit(p, pairs):
    s = open(p).read()
    for a, b in pairs:
        assert a in s, (p, a[:60]); s = s.replace(a, b)
    open(p, 'w').write(s)

edit('css/booking.css', [
    ('.h4 { font-size: 20px;', '.h4 { font-weight: 400; font-size: 20px;'),
    ('.mybk { background', '.mybk { position: sticky; top: 124px; background'),
])
edit('js/booking.js', [
    ('''    if (scroll) window.scrollTo(''', '''    var mb = $(".mybk", box);
    if (mb) { var fit = function () { if (!document.body.contains(mb)) return window.removeEventListener("resize", fit); mb.style.top = Math.min(124, window.innerHeight - mb.offsetHeight - 20) + "px"; }; fit(); window.addEventListener("resize", fit); }
    if (scroll) window.scrollTo('''),
])
print("ok")
