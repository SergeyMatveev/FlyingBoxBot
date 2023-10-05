TOKEN = '6204132043:AAGsy6mKP485rFaBVGeeg6p1dSknDo76jlc'
DATABASE_NAME = 'flyingbox_database'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'flyingbox'
DATABASE_HOST = '34.22.206.231'
DATABASE_PORT = '5432'
KNOWN_COUNTRIES = [
    "афганистан", "албания", "алжир", "андорра", "ангола",
    "антигуа и барбуда", "аргентина", "армения", "австралия", "австрия",
    "азербайджан", "багамы", "бахрейн", "бангладеш", "барбадос",
    "беларусь", "бельгия", "белиз", "бенин", "бутан",
    "боливия", "босния и герцеговина", "ботсвана", "бразилия", "бруней",
    "болгария", "буркина-фасо", "бурунди", "вануату", "ватикан",
    "великобритания", "венгрия", "венесуэла", "вьетнам", "габон",
    "гаити", "гайана", "гамбия", "гана", "гватемала",
    "гвинея", "гвинея-бисау", "германия", "гондурас", "гренада",
    "греция", "грузия", "дания", "джибути", "доминика",
    "доминиканская республика", "египет", "замбия", "зимбабве", "израиль",
    "индия", "индонезия", "иордания", "ирак", "иран",
    "ирландия", "исландия", "испания", "италия", "йемен",
    "кабо-верде", "казахстан", "камбоджа", "камерун", "канада",
    "катар", "кения", "кипр", "киргизия", "кирибати",
    "китай", "колумбия", "коморы", "конго", "корея северная",
    "корея южная", "коста-рика", "кот-д'ивуар", "куба", "кувейт",
    "лаос", "латвия", "лесото", "либерия", "ливан",
    "ливия", "литва", "лихтенштейн", "люксембург", "маврикий",
    "мавритания", "мадагаскар", "малави", "малайзия", "мали",
    "мальдивы", "мальта", "марокко", "маршалловы острова", "мексика",
    "мозамбик", "молдова", "монако", "монголия", "мьянма",
    "намибия", "науру", "непал", "нигер", "нигерия",
    "нидерланды", "никарагуа", "новая зеландия", "норвегия", "оаэ",
    "оман", "пакистан", "палау", "панама", "папуа - новая гвинея",
    "парагвай", "перу", "польша", "португалия", "россия",
    "руанда", "румыния", "сальвадор", "самоа", "сан-марино",
    "сан-томе и принсипи", "саудовская аравия", "свазиленд", "северная македония", "сейшелы",
    "сенегал", "сент-винсент и гренадины", "сент-китс и невис", "сент-люсия", "сербия",
    "сирия", "словакия", "словения", "соломоновы острова", "сомали",
    "судан", "суринам", "сша", "сьерра-леоне", "таджикистан",
    "таиланд", "танзания", "того", "тонга", "тринидад и тобаго",
    "тувалу", "тунис", "туркмения", "турция", "уганда",
    "узбекистан", "украина", "уругвай", "фиджи", "филиппины",
    "финляндия", "франция", "хорватия", "центральноафриканская республика", "чад",
    "черногория", "чехия", "чили", "швейцария", "швеция",
    "шри-ланка", "эквадор", "экваториальная гвинея", "эритрея", "эсватини",
    "эстония", "эфиопия", "юар", "ямайка", "япония"
]

KNOWN_CITIES = [
    "абердин", "алгеро", "александруполис", "алматы", "альба",
    "альмерия", "амстердам", "анапа", "анкара", "антверпен",
    "анталья", "атена", "афины", "баку", "балчик",
    "барселона", "бари", "белград", "белфаст", "бельско-бяла",
    "бергамо", "берген", "берлин", "берн", "билбао",
    "бирмингем", "бишкек", "блэкпул", "бодрум", "болонья",
    "бордо", "братислава", "бремен", "бристоль", "брно",
    "брюссель", "будапешт", "бухарест", "валенсия", "варна",
    "варшава", "вена", "венеция", "верона", "вильнюс",
    "витебск", "вроцлав", "гаага", "галле", "гамбург",
    "гданьск", "генуя", "глазго", "гоа", "гронинген",
    "гётеборг", "дебрецен", "донецк", "дортмунд", "дрезден",
    "дублин", "дубровник", "дюссельдорф", "евпатория", "единбург",
    "екатеринбург", "елизово", "ессен", "женева", "загреб",
    "запорожье", "зёльден", "иннсбрук", "инсбрук", "иркутск",
    "испарта", "истанбул", "йошкар-ола", "кавала", "кагул",
    "казань", "калининград", "калуга", "кандава", "караганда",
    "карловы вары", "картахена", "касабланка", "катовице", "каунас",
    "киев", "кил", "клагенфурт", "копенгаген", "кордова",
    "кос", "косице", "краснодар", "красноярск", "кривой рог",
    "крым", "кушадасы", "ла-корунья", "ларнака", "ларнака",
    "левадия", "лейпциг", "лилль", "лима", "лимассол",
    "лиссабон", "лиф", "лондон", "лубек", "любек",
    "любляна", "люксембург", "люцерн", "мадрид", "майорка",
    "македония", "малага", "мальта", "манчестер", "марбелья",
    "марсель", "милан", "минск", "монако", "монте-карло",
    "москва", "мюнхен", "нант", "наполи", "нижневартовск",
    "нижнекамск", "нижний новгород", "ницца", "новосибирск", "норвич",
    "нюрнберг", "одесса", "олбия", "осло", "остенде",
    "пафос", "пекин", "пермь", "петербург", "петрозаводск",
    "пирс", "пловдив", "подгорица", "познань", "порту",
    "прага", "прибой", "рейкьявик", "ретимнон", "рим",
    "рига", "родос", "ростов-на-дону", "роттердам", "салоники",
    "самара", "самсун", "санкт-петербург", "сантьяго", "сараево",
    "саратов", "севилья", "севастополь", "сент-этьен", "сергиев посад",
    "симферополь", "сицилия", "скопье", "смоленск", "софия",
    "сплит", "стамбул", "стокгольм", "страсбург", "стутгарт",
    "таллинн", "тампере", "тбилиси", "тессалоники", "тирана",
    "тольятти", "трабзон", "триест", "трондхейм", "тунис",
    "улан-батор", "улан-удэ", "ульяновск", "уфа", "фаро",
    "фессалоники", "флоренция", "франкфурт", "фукуока", "хабаровск",
    "ханой", "харьков", "хельсинки", "херсон", "хургада",
    "цюрих", "чебоксары", "челябинск", "черкассы", "чернигов",
    "черновцы", "чишмы", "шанхай", "шарм-эль-шейх", "шереметьево",
    "шимкент", "эдинбург", "эйндховен", "эрзурум", "ярославль"
]
