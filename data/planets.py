"""
Модуль содержит информацию о планетах Солнечной системы и экзопланетах.
"""

SOLAR_SYSTEM = {
    "sun": {
        "name": "☀️ Солнце",
        "type": "Звезда главной последовательности",
        "mass": "1.989 × 10^30 кг (333 000 масс Земли)",
        "diameter": "1.392.684 км (109 диаметров Земли)",
        "temperature": "5778K (поверхность), 15.7M K (ядро)",
        "description": "Солнце - центральная звезда Солнечной системы, вокруг которой обращаются планеты. Это самый мощный источник энергии в нашей системе.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/450px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg"
    },
    "mercury": {
        "name": "☿ Меркурий",
        "type": "Планета земной группы",
        "mass": "3.285 × 10^23 кг (0.055 масс Земли)",
        "diameter": "4879 км (0.383 диаметра Земли)",
        "temperature": "-180°C до +430°C",
        "description": "Самая маленькая и ближайшая к Солнцу планета. Не имеет естественных спутников и атмосферы.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Mercury_in_color_-_Prockter07-edit1.jpg/450px-Mercury_in_color_-_Prockter07-edit1.jpg"
    },
    "venus": {
        "name": "♀️ Венера",
        "type": "Планета земной группы",
        "mass": "4.867 × 10^24 кг (0.815 масс Земли)",
        "diameter": "12104 км (0.949 диаметра Земли)",
        "temperature": "+462°C (средняя)",
        "description": "Вторая планета от Солнца. Названа в честь римской богини любви. Самая горячая планета в Солнечной системе.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Venus-real_color.jpg/450px-Venus-real_color.jpg"
    },
    "earth": {
        "name": "🌍 Земля",
        "type": "Планета земной группы",
        "mass": "5.972 × 10^24 кг",
        "diameter": "12742 км",
        "temperature": "15°C (средняя)",
        "description": "Наша планета. Единственное известное место во Вселенной, где существует жизнь.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/450px-The_Earth_seen_from_Apollo_17.jpg"
    },
    "mars": {
        "name": "♂️ Марс",
        "type": "Планета земной группы",
        "mass": "6.39 × 10^23 кг (0.107 масс Земли)",
        "diameter": "6779 км (0.532 диаметра Земли)",
        "temperature": "-63°C (средняя)",
        "description": "Красная планета. Названа в честь древнеримского бога войны. Активно исследуется роботами-марсоходами.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/450px-OSIRIS_Mars_true_color.jpg"
    },
    "jupiter": {
        "name": "♃ Юпитер",
        "type": "Газовый гигант",
        "mass": "1.898 × 10^27 кг (317.8 масс Земли)",
        "diameter": "139820 км (11.209 диаметров Земли)",
        "temperature": "-110°C (облачный слой)",
        "description": "Крупнейшая планета Солнечной системы. Имеет систему колец и множество спутников.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/450px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg"
    },
    "saturn": {
        "name": "♄ Сатурн",
        "type": "Газовый гигант",
        "mass": "5.683 × 10^26 кг (95.16 масс Земли)",
        "diameter": "116460 км (9.449 диаметров Земли)",
        "temperature": "-140°C (облачный слой)",
        "description": "Шестая планета от Солнца. Известна своей обширной системой колец.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/450px-Saturn_during_Equinox.jpg"
    },
    "uranus": {
        "name": "⛢ Уран",
        "type": "Ледяной гигант",
        "mass": "8.681 × 10^25 кг (14.54 масс Земли)",
        "diameter": "50724 км (4.007 диаметров Земли)",
        "temperature": "-195°C (облачный слой)",
        "description": "Седьмая планета от Солнца. Вращается под углом 98° к плоскости орбиты.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Uranus2.jpg/450px-Uranus2.jpg"
    },
    "neptune": {
        "name": "♆ Нептун",
        "type": "Ледяной гигант",
        "mass": "1.024 × 10^26 кг (17.15 масс Земли)",
        "diameter": "49244 км (3.883 диаметров Земли)",
        "temperature": "-200°C (облачный слой)",
        "description": "Восьмая и самая дальняя планета от Солнца. Названа в честь римского бога морей.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Neptune_Full.jpg/450px-Neptune_Full.jpg"
    },
    "pluto": {
        "name": "♇ Плутон",
        "type": "Карликовая планета",
        "mass": "1.303 × 10^22 кг (0.002 масс Земли)",
        "diameter": "2377 км (0.186 диаметра Земли)",
        "temperature": "-230°C (средняя)",
        "description": "Крупнейший объект пояса Койпера. До 2006 года считался девятой планетой Солнечной системы.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Pluto_in_True_Color_-_High-Res.jpg/450px-Pluto_in_True_Color_-_High-Res.jpg"
    }
}

EXOPLANETS = {
    "kepler_452b": {
        "name": "🌎 Kepler-452b",
        "distance": "1400 световых лет",
        "star": "Kepler-452 (жёлтый карлик, похож на Солнце)",
        "type": "Суперземля",
        "mass": "5 масс Земли (предполагаемая)",
        "year": "385 земных дней",
        "description": "Известна как «Земля 2.0». Находится в обитаемой зоне звезды, похожей на Солнце.",
        "atmosphere": "Предположительно плотная, богатая водородом и гелием с примесью водяного пара",
        "esi": 0.83,
        "image": "https://media.sketchfab.com/models/fa77ec86529e4591b50234946d2f147b/thumbnails/e685fea970994690869f6360d058c447/1024.jpeg"
    },
    "proxima_b": {
        "name": "🌍 Proxima Centauri b",
        "distance": "4.2 световых года",
        "star": "Proxima Centauri (красный карлик)",
        "type": "Скалистая планета",
        "mass": "1.17 масс Земли",
        "year": "11.2 земных дня",
        "description": "Ближайшая к нам экзопланета, находится у ближайшей к Солнцу звезды.",
        "atmosphere": "Возможно тонкая атмосфера, состав неизвестен",
        "esi": 0.87,
        "image": "https://disgustingmen.com/wp-content/uploads/2016/08/proxima-b.jpg"
    },
    "trappist_1e": {
        "name": "🌎 TRAPPIST-1e",
        "distance": "39 световых лет",
        "star": "TRAPPIST-1 (ультрахолодный красный карлик)",
        "type": "Землеподобная планета",
        "mass": "0.772 масс Земли",
        "year": "6.1 земных дня",
        "description": "Одна из семи планет системы TRAPPIST-1. Наиболее вероятный кандидат на наличие жидкой воды.",
        "atmosphere": "Возможно имеет атмосферу земного типа с преобладанием азота и CO2",
        "esi": 0.92,
        "image": "https://static.wikia.nocookie.net/solarsmash/images/9/9c/Trappist-1e.jpg/revision/latest?cb=20240302082536"
    },
    "k2_18b": {
        "name": "🌍 K2-18b",
        "distance": "124 световых года",
        "star": "K2-18 (красный карлик)",
        "type": "Суперземля",
        "mass": "8.6 масс Земли",
        "year": "33 земных дня",
        "description": "В атмосфере планеты обнаружены водяной пар и облака. Находится в обитаемой зоне.",
        "atmosphere": "Водородно-гелиевая с значительным содержанием водяного пара и метана",
        "esi": 0.71,
        "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTkk_E361JEA_a4DTdAgWsAe2NtbN4CeCDVtw&s"
    },
    "teegarden_b": {
        "name": "🌎 Teegarden's Star b",
        "distance": "12.5 световых лет",
        "star": "Звезда Тигардена (ультрахолодный красный карлик)",
        "type": "Землеподобная планета",
        "mass": "1.05 масс Земли",
        "year": "4.9 земных дня",
        "description": "Одна из самых похожих на Землю планет по массе. Имеет высокий индекс подобия Земле.",
        "atmosphere": "Предположительно тонкая атмосфера земного типа",
        "esi": 0.95,
        "image": "https://astrophotographylens.com/cdn/shop/articles/Teegardens_Star_b.jpg?v=1709477289"
    },
    "ross_128b": {
        "name": "🌍 Ross 128 b",
        "distance": "11 световых лет",
        "star": "Ross 128 (красный карлик)",
        "type": "Суперземля",
        "mass": "1.35 масс Земли",
        "year": "9.9 земных дня",
        "description": "Вторая ближайшая к нам потенциально обитаемая планета после Proxima b.",
        "atmosphere": "Возможно имеет умеренную атмосферу земного типа",
        "esi": 0.86,
        "image": "https://assets.science.nasa.gov/dynamicimage/assets/science/astro/exo-explore/assets/content/planets/superearth-7.jpg"
    },
    "lhs_1140b": {
        "name": "🌎 LHS 1140 b",
        "distance": "49 световых лет",
        "star": "LHS 1140 (красный карлик)",
        "type": "Суперземля",
        "mass": "6.98 масс Земли",
        "year": "24.7 земных дня",
        "description": "Скалистая суперземля в обитаемой зоне. Вероятно имеет плотную атмосферу.",
        "atmosphere": "Предположительно плотная атмосфера с преобладанием CO2 и водяного пара",
        "esi": 0.78,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/LHS_1140_System.jpg/640px-LHS_1140_System.jpg"
    },
    "gj_257d": {
        "name": "🌍 GJ 257d",
        "distance": "37 световых лет",
        "star": "GJ 257 (красный карлик)",
        "type": "Суперземля",
        "mass": "7.0 масс Земли",
        "year": "55.7 земных дня",
        "description": "Находится в оптимистичной обитаемой зоне своей звезды. Потенциально может иметь жидкую воду.",
        "atmosphere": "Возможно имеет плотную атмосферу с парниковым эффектом",
        "esi": 0.75,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/GJ_357_d.jpg/960px-GJ_357_d.jpg"
    }
}
