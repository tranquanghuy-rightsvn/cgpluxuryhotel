#!/usr/bin/env python3
"""Booking widget polish to match original Exely screens. Run from html/."""
def edit(p, pairs):
    s = open(p).read()
    for a, b in pairs:
        assert a in s, (p, a[:60]); s = s.replace(a, b)
    open(p, 'w').write(s)

edit('css/booking.css', [
    ('.plate-cap { padding: 24px 20px 16px;', '.plate-cap { font-weight: 400; padding: 24px 20px 16px;'),
    ('.mybk-dates .dash {', '.mybk-dates .mybk-sep {'),
    ('.mybk { position: sticky; top: 124px; background', '.mybk { background'),
    ('.psf .x-check { margin: 4px 0 16px; }', '.psf .x-check { margin: 4px 0 16px; }\n.psf-extra { display: inline-flex; align-items: center; gap: 8px; color: var(--c-link); font-size: 14px; }\n.psf-extra svg { width: 16px; height: 16px; fill: var(--c-link); }\n.x-input output { display: block; padding: 0 16px; line-height: 40px; }\n.x-input .x-native { position: absolute; inset: 0; opacity: 0; cursor: pointer; padding: 0; }'),
])

edit('js/booking.js', [
    ('<span class="dash">—</span>', '<span class="mybk-sep">—</span>'),
    ('''<span class="x-input"><input type="date" id="s-ci" min="' + today + '" value="' + S.checkin + '" required>''',
     '''<span class="x-input"><output data-for="s-ci">' + esc(I.longDate(parse(S.checkin))) + '</output><input class="x-native" type="date" id="s-ci" min="' + today + '" value="' + S.checkin + '" required>'''),
    ('''<span class="x-input"><input type="date" id="s-co" min="' + addDays(S.checkin, 1) + '" value="' + S.checkout + '" required>''',
     '''<span class="x-input"><output data-for="s-co">' + esc(I.longDate(parse(S.checkout))) + '</output><input class="x-native" type="date" id="s-co" min="' + addDays(S.checkin, 1) + '" value="' + S.checkout + '" required>'''),
    ('''<select id="s-ch">' + ch + '</select><i class="chev"></i></label></div>' +
      "<hr>" +''',
     '''<select id="s-ch">' + ch + '</select><i class="chev"></i></label></div>' +
      '<p style="margin-top:24px"><button type="button" class="psf-extra" data-extra>' + I.t("tl.extra") + ICON.plus + '</button></p><p class="psf-note" id="s-extra" hidden>' + I.t("tl.extraNote") + "</p>" +
      "<hr>" +'''),
    ('''    if (t.id === "s-ci" && t.value) { var co = $("#s-co"); co.min = addDays(t.value, 1); if (!co.value || co.value <= t.value) co.value = co.min; }''',
     '''    if (t.id === "s-ci" && t.value) { var co = $("#s-co"); co.min = addDays(t.value, 1); if (!co.value || co.value <= t.value) co.value = co.min; }
    if (t.id === "s-ci" || t.id === "s-co") $$("#tl output[data-for]").forEach(function (o) { var v = $("#" + o.dataset.for).value; o.textContent = okDate(v) ? I.longDate(parse(v)) : ""; });'''),
    ('''    var x = t.closest("[data-expand]");''',
     '''    if (t.closest("[data-extra]")) { $("#s-extra").hidden = !$("#s-extra").hidden; return; }
    var nat = t.closest(".x-native"); if (nat) { try { nat.showPicker(); } catch (er) {} }
    var x = t.closest("[data-expand]");'''),
])

edit('js/i18n.js', [
    ('    "tl.promo": [', '''    "tl.extra": ["Thêm phòng", "Extra room", "객실 추가", "添加客房", "Ещё номер", "Weiteres Zimmer"],
    "tl.extraNote": ["Cần đặt nhiều phòng? Vui lòng liên hệ khách sạn qua hotline hoặc email.", "Need more than one room? Please contact the hotel by phone or email.", "객실이 여러 개 필요하시면 전화 또는 이메일로 문의해 주세요.", "需要多间客房？请通过电话或邮件联系酒店。", "Нужно несколько номеров? Свяжитесь с отелем по телефону или email.", "Mehrere Zimmer? Bitte kontaktieren Sie das Hotel per Telefon oder E-Mail."],
    "tl.promo": ['''),
])
print("ok")
