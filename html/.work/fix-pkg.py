#!/usr/bin/env python3
"""Make package data match info-rooms.docx exactly: inclusions (verbatim), description, CTA, all 8 terms. Run from html/."""
import json, re

p = "js/data.js"; s = open(p, encoding="utf-8").read()

NEW_INC = {
    "acc2": ["Lưu trú {N} cho 2 khách", "{n}-night accommodation for 2 guests", "2인 {N} 숙박", "2位宾客{N}住宿", "Проживание: {N}, 2 гостя", "{n} Übernachtungen für 2 Gäste"],
    "acc0": ["Lưu trú {N}", "{n}-night accommodation", "{N} 숙박", "{N}住宿", "Проживание: {N}", "{n} Übernachtungen"],
    "accP": ["Lưu trú {N} hạng phòng cao cấp cho 2 khách", "{n}-night accommodation in a premium room category for 2 guests", "프리미엄 객실 2인 {N} 숙박", "2位宾客{N}高级房型住宿", "Проживание: {N} в номере премиум-категории, 2 гостя", "{n} Übernachtungen in einer Premium-Zimmerkategorie für 2 Gäste"],
    "acc1": ["Lưu trú {N} cho 1 khách", "{n}-night accommodation for 1 guest", "1인 {N} 숙박", "1位宾客{N}住宿", "Проживание: {N}, 1 гость", "{n} Übernachtungen für 1 Gast"],
    "wdp": ["Đồ uống chào mừng", "Welcome drinks", "웰컴 드링크", "迎宾饮品", "Приветственные напитки", "Begrüßungsgetränke"],
    "wd1a": ["Đồ uống chào mừng khi đến", "Welcome drink upon arrival", "도착 시 웰컴 드링크", "抵达时迎宾饮品", "Приветственный напиток по прибытии", "Begrüßungsgetränk bei Ankunft"],
    "wd1": ["Đồ uống chào mừng", "Welcome drink", "웰컴 드링크", "迎宾饮品", "Приветственный напиток", "Begrüßungsgetränk"],
    "wfp": ["Trái cây chào mừng", "Welcome fruit", "웰컴 과일", "迎宾水果", "Приветственные фрукты", "Willkommensobst"],
    "d1g2": ["Một bữa tối cho 2 khách", "One dinner for 2 guests", "2인 디너 1회", "双人晚餐一次", "Один ужин на двоих", "Ein Abendessen für 2 Gäste"],
    "d1g1": ["Một bữa tối cho 1 khách", "One dinner for 1 guest", "1인 디너 1회", "单人晚餐一次", "Один ужин на одного гостя", "Ein Abendessen für 1 Gast"],
    "d2g2": ["Hai bữa tối cho 2 khách", "Two dinners for 2 guests", "2인 디너 2회", "双人晚餐两次", "Два ужина на двоих", "Zwei Abendessen für 2 Gäste"],
    "tea2": ["Một buổi trà chiều cho 2 khách", "One afternoon tea experience for 2 guests", "2인 애프터눈 티 1회", "双人下午茶一次", "Послеобеденный чай на двоих", "Ein Afternoon Tea für 2 Gäste"],
    "mass1": ["Một buổi massage thư giãn*", "One relaxing massage experience*", "릴랙싱 마사지 1회*", "舒缓按摩一次*", "Один сеанс расслабляющего массажа*", "Eine Entspannungsmassage*"],
    "laundryR": ["Dịch vụ giặt ủi định kỳ (theo định mức của gói)", "Regular laundry service, subject to package allowance", "정기 세탁 서비스 (패키지 한도 내)", "定期洗衣服务（按套餐额度）", "Регулярная стирка (в рамках пакета)", "Regelmäßiger Wäscheservice (im Paketumfang)"],
}

# Inclusions in the exact order of the docx
INC_LISTS = {
    1: ["acc2", "bf", "wd", "wf", "d1g2", "pool", "late"],
    2: ["acc2", "bf", "deco", "flow", "wfp", "rdin", "sig", "late"],
    3: ["acc2", "bf", "hdeco", "flow", "cake", "wfp", "sdin", "tea2", "mass60", "late"],
    4: ["acc0", "famroom", "bf", "wdp", "wfp", "fdin", "laundry", "kids", "late"],
    5: ["acc2", "bf", "ap1", "wdp", "wfp", "d1g2", "late"],
    6: ["acc2", "bf", "ap2", "wdp", "wfp", "d1g2", "tea2", "laundry", "late"],
    7: ["acc2", "bf", "tdeco", "flow", "ccake", "wfp", "sdin", "sig", "photo", "late"],
    8: ["acc2", "bf", "coffee", "wfp", "tea2", "d1g2", "laundry", "late"],
    9: ["acc0", "bf", "wifi", "work", "coffee", "laundryR", "d1", "bev", "late"],
    10: ["accP", "bf", "ap2", "wdp", "wfp", "minibar", "d2g2", "tea2", "mass", "laundry", "sdeco", "late"],
    11: ["acc1", "bf", "wd1a", "wfp", "coffee", "d1g1", "tea", "pool", "late"],
    12: ["acc1", "bf", "wd1", "wfp", "coffee", "d1g1", "tea", "mass1", "laundry", "late"],
    13: ["acc1", "bf", "ap2", "wd1", "wfp", "coffee", "d2", "tea", "mass1", "minibar", "laundry", "late"],
}

DESC = {
    1: ["Tạm rời nhịp sống thường ngày để tận hưởng kỳ nghỉ thư thái tại CGP Luxury Hotel. Thức dậy với bữa sáng ngon miệng, thư giãn bên hồ bơi và cảm nhận lòng hiếu khách ấm áp của người Việt giữa không gian cổ kính của Hội An.",
        "Escape the everyday and enjoy a relaxing stay at CGP Luxury Hotel. Wake up to a delicious daily breakfast, unwind by the pool, and experience warm Vietnamese hospitality while enjoying the charming atmosphere of Hoi An.",
        "일상에서 벗어나 CGP 럭셔리 호텔에서 여유로운 휴식을 즐기세요. 맛있는 조식으로 하루를 시작하고 수영장에서 휴식을 취하며, 호이안의 매력적인 분위기 속에서 따뜻한 베트남식 환대를 경험해 보세요.",
        "暂别日常，在 CGP 奢华酒店享受悠闲时光。每天以美味早餐开启新的一天，在泳池边放松身心，在会安迷人的氛围中感受越南式的热情款待。",
        "Отвлекитесь от повседневности и отдохните в CGP Luxury Hotel: вкусный завтрак каждое утро, отдых у бассейна и тёплое вьетнамское гостеприимство в очаровательной атмосфере Хойана.",
        "Lassen Sie den Alltag hinter sich und genießen Sie einen entspannten Aufenthalt im CGP Luxury Hotel. Wachen Sie mit einem leckeren Frühstück auf, entspannen Sie am Pool und erleben Sie herzliche vietnamesische Gastfreundschaft in der charmanten Atmosphäre von Hoi An."],
    2: ["Tôn vinh tình yêu với kỳ nghỉ lãng mạn tại CGP Luxury Hotel. Căn phòng được trang trí xinh đẹp, bữa tối đặc biệt cho hai người cùng những chi tiết chu đáo sẽ giúp khoảng thời gian bên nhau thật khó quên.",
        "Celebrate love with a romantic escape at CGP Luxury Hotel. Enjoy a beautifully decorated room, a special dinner for two, and thoughtful touches designed to make your time together truly unforgettable.",
        "CGP 럭셔리 호텔에서 로맨틱한 휴가로 사랑을 기념하세요. 아름답게 꾸며진 객실, 둘만을 위한 특별한 디너, 세심한 배려로 함께하는 시간을 잊지 못할 추억으로 만들어 드립니다.",
        "在 CGP 奢华酒店来一场浪漫之旅，为爱庆祝。精心布置的客房、专属双人晚餐与贴心细节，让你们的相伴时光难以忘怀。",
        "Отпразднуйте любовь романтическим отдыхом в CGP Luxury Hotel: красиво оформленный номер, особый ужин на двоих и продуманные детали, которые сделают ваше время вместе незабываемым.",
        "Feiern Sie die Liebe mit einer romantischen Auszeit im CGP Luxury Hotel. Ein liebevoll dekoriertes Zimmer, ein besonderes Dinner zu zweit und aufmerksame Details machen Ihre gemeinsame Zeit unvergesslich."],
    3: ["Làm cho tuần trăng mật thêm đáng nhớ với kỳ nghỉ lãng mạn dành riêng cho các cặp đôi mới cưới. Từ trang trí phòng chu đáo, bữa tối riêng tư đến những phút giây thư giãn — hãy để CGP Luxury Hotel lo từng chi tiết nhỏ.",
        "Make your honeymoon even more memorable with a romantic stay designed especially for newlyweds. From thoughtful room decoration to intimate dining and relaxing moments, let CGP Luxury Hotel take care of the little details.",
        "신혼부부를 위해 특별히 준비한 로맨틱한 스테이로 허니문을 더욱 특별하게 만드세요. 세심한 객실 장식부터 오붓한 디너와 휴식의 순간까지, 작은 디테일은 CGP 럭셔리 호텔이 챙겨 드립니다.",
        "专为新婚夫妇打造的浪漫住宿，让蜜月更加难忘。从用心的客房布置到私密晚餐与放松时光，所有细节交给 CGP 奢华酒店。",
        "Сделайте медовый месяц ещё более запоминающимся: романтический отдых, созданный специально для молодожёнов. От оформления номера до ужина вдвоём — CGP Luxury Hotel позаботится о каждой мелочи.",
        "Machen Sie Ihre Flitterwochen noch unvergesslicher mit einem romantischen Aufenthalt speziell für Frischvermählte. Von der Zimmerdekoration bis zu intimen Dinners und entspannten Momenten – das CGP Luxury Hotel kümmert sich um die kleinen Details."],
    4: ["Tận hưởng kỳ nghỉ gia đình thoải mái tại Hội An với phòng nghỉ rộng rãi, bữa sáng hằng ngày và các dịch vụ chu đáo giúp chuyến đi cùng người thân dễ dàng, thư thái và vui vẻ hơn.",
        "Enjoy a comfortable family getaway in Hoi An with spacious accommodation, daily breakfast, and thoughtful services designed to make travelling with your loved ones easier, more relaxing, and more enjoyable.",
        "넓은 객실과 매일 조식, 세심한 서비스로 사랑하는 가족과의 여행을 더 편안하고 즐겁게 만들어 줄 호이안 가족 휴가를 즐기세요.",
        "宽敞的客房、每日早餐与贴心服务，让您与家人在会安的旅行更轻松、更惬意、更愉快。",
        "Комфортный семейный отдых в Хойане: просторный номер, ежедневный завтрак и внимательный сервис, чтобы путешествие с близкими было проще, спокойнее и приятнее.",
        "Genießen Sie einen komfortablen Familienurlaub in Hoi An mit geräumiger Unterkunft, täglichem Frühstück und aufmerksamem Service, der das Reisen mit Ihren Liebsten einfacher, entspannter und schöner macht."],
    5: ["Bắt đầu kỳ nghỉ Hội An thật nhẹ nhàng. Tận hưởng kỳ lưu trú thoải mái với dịch vụ đón sân bay khi bạn đến, bữa sáng hằng ngày và các dịch vụ chu đáo giúp chuyến đi dễ dàng, thư thái.",
        "Start your Hoi An holiday without the hassle. Enjoy a comfortable stay with airport pick-up arranged for your arrival, daily breakfast, and thoughtful services to make your getaway easy and relaxing.",
        "번거로움 없이 호이안 휴가를 시작하세요. 도착 시 공항 픽업, 매일 조식, 세심한 서비스로 편안하고 여유로운 휴가를 즐길 수 있습니다.",
        "轻松开启会安假期。抵达时安排机场接机，每日早餐与贴心服务，让您的旅程轻松惬意。",
        "Начните отпуск в Хойане без забот: встреча в аэропорту по прибытии, ежедневный завтрак и внимательный сервис для лёгкого и спокойного отдыха.",
        "Starten Sie Ihren Urlaub in Hoi An ganz entspannt: Abholung vom Flughafen bei Ankunft, tägliches Frühstück und aufmerksamer Service für eine unkomplizierte Auszeit."],
    6: ["Ở lâu hơn, tận hưởng nhiều hơn. Gói Trải nghiệm lưu trú trọn vẹn kết hợp phòng nghỉ thoải mái, ẩm thực và các dịch vụ tiện lợi cho du khách muốn có kỳ nghỉ nhẹ nhàng, thư thái tại Hội An.",
        "Stay longer and enjoy more. Our Complete Stay Experience combines comfortable accommodation, dining, and convenient services for travellers looking for an easy and relaxing holiday in Hoi An.",
        "더 오래 머물고 더 많이 즐기세요. 컴플리트 스테이 익스피리언스는 편안한 객실, 다이닝, 편리한 서비스를 결합해 호이안에서 여유로운 휴가를 원하는 여행객에게 딱 맞습니다.",
        "住得更久，享受更多。全享住宿体验集舒适客房、餐饮与便捷服务于一体，适合想在会安轻松度假的旅客。",
        "Оставайтесь дольше — получайте больше. Пакет сочетает комфортное проживание, питание и удобные услуги для лёгкого и спокойного отдыха в Хойане.",
        "Länger bleiben, mehr genießen: Das Paket verbindet komfortable Unterkunft, Kulinarik und praktische Services für einen unkomplizierten, entspannten Urlaub in Hoi An."],
    7: ["Dù là kỷ niệm ngày cưới, sinh nhật hay một cột mốc đặc biệt, hãy để CGP Luxury Hotel tạo nên dịp kỷ niệm đáng nhớ với những chi tiết chu đáo và sự hiếu khách ấm áp.",
        "Whether it is an anniversary, birthday, or another special milestone, let CGP Luxury Hotel create a memorable celebration filled with thoughtful details and warm hospitality.",
        "결혼기념일, 생일 또는 특별한 순간이라면 CGP 럭셔리 호텔이 세심한 디테일과 따뜻한 환대로 잊지 못할 축하를 준비해 드립니다.",
        "无论是周年纪念、生日还是其他特别时刻，CGP 奢华酒店都将以贴心细节与热情款待，为您打造难忘的庆祝。",
        "Годовщина, день рождения или другое важное событие — CGP Luxury Hotel устроит запоминающийся праздник с продуманными деталями и тёплым гостеприимством.",
        "Ob Jahrestag, Geburtstag oder ein anderer besonderer Anlass – das CGP Luxury Hotel gestaltet eine unvergessliche Feier mit aufmerksamen Details und herzlicher Gastfreundschaft."],
    8: ["Khám phá niềm vui sống chậm với kỳ lưu trú dài hơn tại CGP Luxury Hotel. Thong thả tận hưởng những buổi sáng nhàn nhã, buổi chiều thư giãn và vẻ đẹp, nét duyên của Hội An theo nhịp riêng của bạn.",
        "Discover the joy of slow living with a longer stay at CGP Luxury Hotel. Take your time, enjoy leisurely mornings and relaxing afternoons, and experience the beauty and charm of Hoi An at your own pace.",
        "CGP 럭셔리 호텔에서 긴 휴식을 즐기며 슬로우 라이프의 기쁨을 발견하세요. 여유로운 아침과 편안한 오후를 보내며 나만의 속도로 호이안의 아름다움과 매력을 경험해 보세요.",
        "在 CGP 奢华酒店长住，体验慢生活的乐趣。从容享受悠闲的早晨与惬意的午后，按自己的节奏感受会安的美丽与魅力。",
        "Откройте радость неспешной жизни, оставшись в CGP Luxury Hotel подольше: спокойные утра, расслабленные дни и красота Хойана в вашем собственном ритме.",
        "Entdecken Sie die Freude des langsamen Lebens bei einem längeren Aufenthalt im CGP Luxury Hotel: gemütliche Morgen, entspannte Nachmittage und Hoi An in Ihrem eigenen Tempo."],
    9: ["Dành cho người làm việc từ xa và khách lưu trú dài ngày, gói này mang đến sự tiện nghi cần thiết để bạn làm việc hiệu quả trong khi vẫn tận hưởng nhịp sống thư thái tại Hội An.",
        "Designed for remote workers and long-stay travellers, this package offers the comfort and convenience you need to stay productive while enjoying a relaxing lifestyle in Hoi An.",
        "원격 근무자와 장기 투숙객을 위한 패키지로, 호이안의 여유로운 라이프스타일을 즐기면서도 생산적으로 일할 수 있는 편안함과 편의를 제공합니다.",
        "专为远程办公者和长住旅客设计，在会安享受悠闲生活的同时，提供保持高效工作所需的舒适与便利。",
        "Пакет для удалённых работников и длительных поездок: всё необходимое для продуктивной работы и спокойной жизни в Хойане.",
        "Für Remote-Worker und Langzeitreisende: Komfort und Annehmlichkeiten, um produktiv zu bleiben und zugleich den entspannten Lebensstil in Hoi An zu genießen."],
    10: ["Trải nghiệm những gì tinh túy nhất của CGP Luxury Hotel với kỳ nghỉ Signature. Bảy đêm thư thái với phòng nghỉ cao cấp, ẩm thực, chăm sóc sức khỏe và những chi tiết cá nhân hóa dành cho du khách muốn có một kỳ nghỉ thật đặc biệt tại Hội An.",
         "Experience the best of CGP Luxury Hotel with our signature stay. Enjoy seven relaxing nights with premium accommodation, dining, wellness, and personalised touches designed for guests who want something truly special from their time in Hoi An.",
         "시그니처 스테이로 CGP 럭셔리 호텔의 모든 것을 경험하세요. 프리미엄 객실, 다이닝, 웰니스, 맞춤형 서비스와 함께하는 7박은 호이안에서 특별한 시간을 원하는 분께 안성맞춤입니다.",
         "以尊享假期体验 CGP 奢华酒店的精华。七晚悠闲时光，尽享高级客房、美食、康体与个性化服务，为追求非凡会安之旅的宾客而设。",
         "Лучшее, что может предложить CGP Luxury Hotel: семь ночей в номере премиум-класса, питание, велнес и персональный подход для тех, кто хочет по-настоящему особенного отдыха в Хойане.",
         "Erleben Sie das Beste des CGP Luxury Hotel: sieben entspannte Nächte mit Premium-Unterkunft, Kulinarik, Wellness und persönlichen Details für Gäste, die etwas wirklich Besonderes suchen."],
    11: ["Dành cho mình một kỳ nghỉ xứng đáng và tận hưởng sự tự do khi du lịch một mình. Gói Solo Escape được thiết kế cho du khách độc lập tìm kiếm sự thoải mái, thư giãn và thời gian riêng giữa không gian quyến rũ của Hội An.",
         "Take a well-deserved break and enjoy the freedom of travelling solo. The Solo Escape package is designed for independent travellers looking for comfort, relaxation, and personal time in the charming atmosphere of Hoi An.",
         "자신에게 휴식을 선물하고 혼자 여행하는 자유를 누리세요. 솔로 이스케이프는 호이안의 매력적인 분위기 속에서 편안함과 휴식, 나만의 시간을 원하는 여행자를 위한 패키지입니다.",
         "给自己一个应得的假期，享受独自旅行的自由。独享之旅套餐专为追求舒适、放松与个人时光的独立旅行者打造，让您沉浸在会安的迷人氛围中。",
         "Заслуженный отдых и свобода путешествия в одиночку. Пакет создан для самостоятельных путешественников, которые ищут комфорт, расслабление и время для себя в атмосфере Хойана.",
         "Gönnen Sie sich eine wohlverdiente Pause und genießen Sie die Freiheit des Alleinreisens – für unabhängige Reisende, die Komfort, Erholung und Zeit für sich in der charmanten Atmosphäre von Hoi An suchen."],
    12: ["Rời xa nhịp sống vội vã và tận hưởng năm đêm thư thái tại CGP Luxury Hotel. Được thiết kế riêng cho du khách đi một mình, gói này cho bạn tự do sống chậm, nạp lại năng lượng và khám phá Hội An hoàn toàn theo nhịp của mình.",
         "Escape the rush of everyday life and enjoy five relaxing nights at CGP Luxury Hotel. Designed especially for solo travellers, this package gives you the freedom to slow down, recharge, and experience Hoi An entirely at your own pace.",
         "바쁜 일상에서 벗어나 CGP 럭셔리 호텔에서 5박의 여유를 즐기세요. 혼자 여행하는 분을 위해 특별히 준비한 패키지로, 천천히 쉬고 재충전하며 나만의 속도로 호이안을 경험할 수 있습니다.",
         "远离日常的匆忙，在 CGP 奢华酒店享受五晚悠闲时光。专为独自旅行者设计，让您自由地放慢脚步、恢复活力，完全按自己的节奏体验会安。",
         "Сбегите от суеты и проведите пять спокойных ночей в CGP Luxury Hotel. Пакет создан для путешествующих в одиночку: замедлитесь, восстановите силы и откройте Хойан в своём ритме.",
         "Entfliehen Sie der Hektik des Alltags und genießen Sie fünf entspannte Nächte im CGP Luxury Hotel – speziell für Alleinreisende, um zu entschleunigen, aufzutanken und Hoi An ganz im eigenen Tempo zu erleben."],
    13: ["Tìm lại niềm vui có thời gian cho riêng mình với kỳ nghỉ Solo Signature bảy đêm. Tận hưởng kỳ lưu trú dài thư thái với ẩm thực chu đáo, chăm sóc sức khỏe và những chi tiết cá nhân hóa dành cho du khách độc lập tìm kiếm sự thoải mái và riêng tư tại Hội An.",
         "Rediscover the joy of having time for yourself with our seven-night Solo Signature Stay. Enjoy a relaxing extended stay with thoughtful dining, wellness, and personalised touches designed for independent travellers seeking comfort and privacy in Hoi An.",
         "7박 솔로 시그니처 스테이로 나만의 시간을 갖는 기쁨을 다시 발견하세요. 세심한 다이닝, 웰니스, 맞춤형 서비스와 함께 호이안에서 편안함과 프라이버시를 원하는 독립 여행자를 위한 여유로운 장기 숙박입니다.",
         "七晚独享尊选假期，让您重拾独处的乐趣。贴心的餐饮、康体与个性化服务，为在会安追求舒适与私密的独立旅行者打造悠闲长住体验。",
         "Вновь откройте радость времени для себя: семь ночей Solo Signature с продуманным питанием, велнесом и персональным подходом для тех, кто ценит комфорт и уединение в Хойане.",
         "Entdecken Sie die Freude an Zeit für sich selbst neu: sieben Nächte Solo Signature mit durchdachter Kulinarik, Wellness und persönlichen Details für unabhängige Reisende, die in Hoi An Komfort und Privatsphäre suchen."],
}

CTA = {
    1: ["Đặt kỳ nghỉ thư giãn", "Book your relaxing stay", "릴랙싱 스테이 예약", "预订悠闲假期", "Забронировать отдых", "Entspannung buchen"],
    2: ["Đặt kỳ nghỉ lãng mạn", "Book your romantic escape", "로맨틱 이스케이프 예약", "预订浪漫之旅", "Забронировать романтический отдых", "Romantische Auszeit buchen"],
    3: ["Đặt gói trăng mật", "Celebrate your honeymoon", "허니문 예약", "预订蜜月之旅", "Отпраздновать медовый месяц", "Flitterwochen feiern"],
    4: ["Đặt kỳ nghỉ gia đình", "Book your family getaway", "가족 여행 예약", "预订家庭假期", "Забронировать семейный отдых", "Familienurlaub buchen"],
    5: ["Đặt gói tiện lợi", "Book your easy stay", "이지 스테이 예약", "预订轻松住宿", "Забронировать «Лёгкий отдых»", "Easy Stay buchen"],
    6: ["Đặt trải nghiệm trọn vẹn", "Book the complete experience", "컴플리트 스테이 예약", "预订全享体验", "Забронировать полный отдых", "Rundum-Erlebnis buchen"],
    7: ["Kỷ niệm cùng chúng tôi", "Celebrate with us", "함께 축하하기", "与我们一起庆祝", "Отпразднуйте с нами", "Mit uns feiern"],
    8: ["Sống chậm tại Hội An", "Slow down in Hoi An", "호이안에서 천천히", "在会安慢下来", "Замедлиться в Хойане", "In Hoi An entschleunigen"],
    9: ["Làm việc & nghỉ dưỡng tại Hội An", "Work & stay in Hoi An", "호이안에서 워크 & 스테이", "在会安工作与度假", "Работать и жить в Хойане", "Arbeiten & wohnen in Hoi An"],
    10: ["Trải nghiệm CGP Signature", "Experience CGP Signature", "CGP 시그니처 경험하기", "体验 CGP 尊享", "Открыть CGP Signature", "CGP Signature erleben"],
    11: ["Đặt kỳ nghỉ một mình", "Book your solo escape", "솔로 이스케이프 예약", "预订独享之旅", "Забронировать соло-отдых", "Solo-Auszeit buchen"],
    12: ["Đặt gói nghỉ dưỡng một mình", "Book your solo retreat", "솔로 리트릿 예약", "预订独享休养", "Забронировать соло-ретрит", "Solo-Retreat buchen"],
    13: ["Trải nghiệm hành trình riêng", "Experience your solo journey", "나만의 여행 경험하기", "开启独享旅程", "Начать соло-путешествие", "Ihre Solo-Reise erleben"],
}

# 1) new inclusion items (insert before the closing of INC)
add = "".join(f'    {k}: {json.dumps(v, ensure_ascii=False)},\n' for k, v in NEW_INC.items())
i = s.index("  var INC = {") ; j = s.index("\n  };", i)
s = s[:j] + ",\n" + add.rstrip(",\n") + s[j:]
s = s.replace('    premium: ["Hạng phòng cao cấp", "Premium room category", "프리미엄 객실", "高级房型", "Номер премиум-категории", "Premium-Zimmerkategorie"],\n', "")

# 2) inclusion lists per package
for pid, lst in INC_LISTS.items():
    s, n = re.subn(r'(\{ id: %d, .*?inc: )\[[^\]]*\]' % pid, lambda m: m.group(1) + json.dumps(lst), s, count=1, flags=re.S)
    assert n == 1, pid

# 3) description + CTA + inclusion text helper
k = s.index("  P.forEach(function (p) { p.names = NAMES[p.id]; });")
extra = "  var DESC = {\n" + ",\n".join(f"    {pid}: {json.dumps(v, ensure_ascii=False)}" for pid, v in DESC.items()) + "\n  };\n"
extra += "  var CTA = {\n" + ",\n".join(f"    {pid}: {json.dumps(v, ensure_ascii=False)}" for pid, v in CTA.items()) + "\n  };\n"
s = s[:k] + extra + s[k:]
s = s.replace("  P.forEach(function (p) { p.names = NAMES[p.id]; });",
              "  P.forEach(function (p) { p.names = NAMES[p.id]; p.desc = DESC[p.id]; p.cta = CTA[p.id]; });")
s = s.replace("  window.CGP = { INC: INC, P: P, NEWS: NEWS,",
              "  /* Inclusion text with {n} = number of nights, {N} = localized nights label */\n"
              "  function incText(k, p, I) { return I.pick(INC[k]).replace(\"{N}\", I.nights(p.nights)).replace(\"{n}\", p.nights); }\n"
              "  window.CGP = { INC: INC, P: P, NEWS: NEWS, incText: incText,")
open(p, "w", encoding="utf-8").write(s)

# 4) consumers use incText; modal/rate step show description; modal button uses CTA
for f in ["js/main.js", "js/booking.js"]:
    t = open(f, encoding="utf-8").read()
    t = re.sub(r"I\.pick\(C\.INC\[k\]\)", "C.incText(k, p, I)", t)
    open(f, "w", encoding="utf-8").write(t)
t = open("js/main.js", encoding="utf-8").read()
a = "'</h3><p class=\"sub-title\">' + esc(I.pick(p.tag)) + \"</p>\" +"
assert a in t
t = t.replace(a, "'</h3><p class=\"sub-title\">' + esc(I.pick(p.tag)) + \"</p>\" + '<p class=\"modal-desc\">' + esc(I.pick(p.desc)) + \"</p>\" +")
a = "'</p><a class=\"btn\" href=\"' + bookUrl(p.id) + '\">' + I.t(\"btn.book\") + \"</a>\";"
assert a in t
t = t.replace(a, "'</p><a class=\"btn\" href=\"' + bookUrl(p.id) + '\">' + esc(I.pick(p.cta)) + \"</a>\";")
open("js/main.js", "w", encoding="utf-8").write(t)
t = open("js/booking.js", encoding="utf-8").read()
a = "'<div class=\"rate\"><div><h4>' + esc(I.pick(p.tag)) + '</h4>"
assert a in t
t = t.replace(a, "'<div class=\"rate\"><div><h4>' + esc(I.pick(p.tag)) + '</h4><p class=\"rate-desc\">' + esc(I.pick(p.desc)) + '</p>")
t = t.replace("var terms = [1, 2, 3, 4, 5].map(", "var terms = [1, 2, 3, 4, 5, 6, 7, 8].map(")
open("js/booking.js", "w", encoding="utf-8").write(t)

# 5) terms 6-8
t = open("js/i18n.js", encoding="utf-8").read()
terms = {
    "terms.6": ["Quyền lợi giặt ủi và minibar miễn phí áp dụng theo định mức ghi trong xác nhận đặt phòng.", "Complimentary laundry and minibar benefits are subject to the specific allowance stated in the booking confirmation.", "무료 세탁 및 미니바 혜택은 예약 확인서에 명시된 한도에 따릅니다.", "免费洗衣及迷你吧礼遇以预订确认中注明的额度为准。", "Бесплатная стирка и мини-бар предоставляются в объёме, указанном в подтверждении бронирования.", "Kostenloser Wäscheservice und Minibar gelten im in der Buchungsbestätigung angegebenen Umfang."],
    "terms.7": ["Các dịch vụ ăn uống, trà chiều, massage, trang trí phòng và đưa đón có thể cần đặt trước.", "Advance reservation may be required for dining, afternoon tea, massage, room decoration, and transfer services.", "다이닝, 애프터눈 티, 마사지, 객실 장식, 픽업 서비스는 사전 예약이 필요할 수 있습니다.", "餐饮、下午茶、按摩、客房布置及接送服务可能需要提前预约。", "Для питания, послеобеденного чая, массажа, оформления номера и трансфера может потребоваться предварительный заказ.", "Für Restaurant, Afternoon Tea, Massage, Zimmerdekoration und Transfers kann eine Vorabreservierung erforderlich sein."],
    "terms.8": ["Các ưu đãi khuyến mãi hoặc theo mùa có thể áp dụng thêm điều khoản riêng.", "Additional terms and conditions may apply to promotional or seasonal offers.", "프로모션 또는 시즌 혜택에는 추가 약관이 적용될 수 있습니다.", "促销或季节性优惠可能适用附加条款。", "К акционным и сезонным предложениям могут применяться дополнительные условия.", "Für Aktions- oder Saisonangebote können zusätzliche Bedingungen gelten."],
}
a = '    "terms.5": ['
assert a in t
t = t.replace(a, "".join(f'    "{k}": {json.dumps(v, ensure_ascii=False)},\n' for k, v in terms.items()) + a)
open("js/i18n.js", "w", encoding="utf-8").write(t)

css = open("css/home.css", encoding="utf-8").read()
if ".modal-desc" not in css:
    css += "\n.modal-desc { margin: -4px 0 16px; font: 400 15px/22px Arial, sans-serif; color: #444; }\n"
    open("css/home.css", "w", encoding="utf-8").write(css)
b = open("css/booking.css", encoding="utf-8").read()
if ".rate-desc" not in b:
    b += "\n.rate-desc { margin-top: 10px; max-width: 640px; font-size: 14px; line-height: 21px; color: #2f3135; }\n"
    open("css/booking.css", "w", encoding="utf-8").write(b)
print("ok")
