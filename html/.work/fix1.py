#!/usr/bin/env python3
"""Fix home search box: dd/mm/yyyy display, ', 0 children' text, box height. Run from html/."""
p = '.work/build.py'; s = open(p).read()
for n, k, lbl in (('checkin', 'box.checkin', 'Check-in'), ('checkout', 'box.checkout', 'Check-out')):
    a = f'<label class="sfl-field"><span data-i18n="{k}">{lbl}</span><input type="date" name="{n}" required><i>{{SVG["cal"]}}</i></label>'
    assert a in s, a
    s = s.replace(a, f'<label class="sfl-field"><span data-i18n="{k}">{lbl}</span><output data-show="{n}"></output><input class="sfl-native" type="date" name="{n}" required><i>{{SVG["cal"]}}</i></label>')
open(p, 'w').write(s)

p = 'css/home.css'; s = open(p).read()
for a, b in [('.sfl { padding-top: 24px; }', '.sfl { min-height: 333px; padding-top: 24px; }'),
             ('.sfl-field input::-webkit-calendar-picker-indicator', '.sfl-native { position: absolute; inset: 0; opacity: 0; cursor: pointer; }\n.sfl-field input::-webkit-calendar-picker-indicator'),
             ('.sfl-field input, .sfl-field select, .sfl-field output {', '.sfl-field select, .sfl-field output {')]:
    assert a in s, a; s = s.replace(a, b)
open(p, 'w').write(s)

p = 'js/main.js'; s = open(p).read()
a = '    var promo = $(".sfl-promo", sfl);'
assert a in s
s = s.replace(a, '''    var show = function () {
      $$("[data-show]", sfl).forEach(function (o) { var v = $('[name="' + o.dataset.show + '"]', sfl).value.split("-"); o.textContent = v.length === 3 ? v[2] + "/" + v[1] + "/" + v[0] : ""; });
    };
    $$(".sfl-native", sfl).forEach(function (n) {
      n.addEventListener("change", show);
      n.addEventListener("click", function () { try { n.showPicker(); } catch (e) {} });
    });
    ci.addEventListener("change", show); show();
    var adultsText = function () { $$('[name="adults"] option', sfl).forEach(function (o) { o.textContent = I.t("g.a" + o.value) + I.t("g.c0"); }); };
    adultsText(); document.addEventListener("langchange", adultsText);
''' + a)
open(p, 'w').write(s)
print("ok")
