"""
Модуль содержит информацию о марсоходах и их камерах.
"""

ROVERS = {
    "curiosity": {
        "name": "Curiosity",
        "landing_date": "2012-08-06",
        "description": "Самый большой и технологически продвинутый марсоход NASA. Исследует кратер Гейла.",
        "cameras": {
            "FHAZ": {
                "name": "Front Hazard Avoidance Camera",
                "description": "Передние камеры для обнаружения препятствий"
            },
            "RHAZ": {
                "name": "Rear Hazard Avoidance Camera",
                "description": "Задние камеры для обнаружения препятствий"
            },
            "MAST": {
                "name": "Mast Camera",
                "description": "Основные камеры для съемки пейзажей и геологических особенностей"
            },
            "CHEMCAM": {
                "name": "Chemistry and Camera Complex",
                "description": "Анализирует химический состав пород с помощью лазера"
            },
            "NAVCAM": {
                "name": "Navigation Camera",
                "description": "Камеры для навигации и планирования маршрута"
            }
        }
    },
    "perseverance": {
        "name": "Perseverance",
        "landing_date": "2021-02-18",
        "description": "Новейший марсоход NASA, ищет следы древней микробной жизни в кратере Езеро.",
        "cameras": {
            "FHAZ": {
                "name": "Front Hazard Avoidance Camera",
                "description": "Передние камеры для обнаружения препятствий"
            },
            "RHAZ": {
                "name": "Rear Hazard Avoidance Camera",
                "description": "Задние камеры для обнаружения препятствий"
            },
            "MAST": {
                "name": "Mastcam-Z",
                "description": "Стереоскопические зум-камеры для детальной съемки поверхности"
            },
            "CHEMCAM": {
                "name": "SuperCam",
                "description": "Усовершенствованная версия ChemCam для анализа пород"
            },
            "NAVCAM": {
                "name": "Navigation Camera",
                "description": "Камеры для навигации и планирования маршрута"
            }
        }
    }
}
