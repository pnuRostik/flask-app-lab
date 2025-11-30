"""
Скрипт для додавання тестових даних для спортивних подій
Використовуйте: flask shell < add_sport_data.py
або: python -c "from app import create_app, db; from app.models import *; app = create_app(); app.app_context().push(); exec(open('add_sport_data.py').read())"
"""
from app.models import SportType, SportEvent, User
from app import db
from datetime import datetime, timedelta

# Створюємо види спорту
sport_types_data = [
    {
        "name": "Футбол",
        "description": "Командний вид спорту, де дві команди змагаються за м'яч",
        "category": "Командний"
    },
    {
        "name": "Баскетбол",
        "description": "Командний вид спорту з м'ячем, мета - закинути м'яч у кошик суперника",
        "category": "Командний"
    },
    {
        "name": "Теніс",
        "description": "Індивідуальний або парний вид спорту з ракетками та м'ячем",
        "category": "Індивідуальний"
    },
    {
        "name": "Плавання",
        "description": "Водний вид спорту, змагання на різних дистанціях та стилях",
        "category": "Індивідуальний"
    },
    {
        "name": "Волейбол",
        "description": "Командний вид спорту, де команди перекидають м'яч через сітку",
        "category": "Командний"
    },
    {
        "name": "Легка атлетика",
        "description": "Набір видів спорту, що включає біг, стрибки, метання",
        "category": "Індивідуальний"
    }
]

print("Створення видів спорту...")
for sport_data in sport_types_data:
    # Перевіряємо чи не існує вже такий вид спорту
    existing = SportType.query.filter_by(name=sport_data["name"]).first()
    if not existing:
        sport_type = SportType(**sport_data)
        db.session.add(sport_type)
        print(f"  ✓ Додано: {sport_data['name']}")
    else:
        print(f"  - Вже існує: {sport_data['name']}")

db.session.commit()
print("Види спорту створені!\n")

# Отримуємо першого користувача для створення подій
user = User.query.first()
if not user:
    print("Помилка: Немає користувачів у базі даних. Спочатку створіть користувача через реєстрацію.")
    exit(1)

print(f"Використовуємо користувача: {user.username}\n")

# Створюємо спортивні події
events_data = [
    {
        "name": "Чемпіонат міста з футболу",
        "description": "Щорічний чемпіонат міста з футболу серед аматорських команд. Запрошуємо всіх бажаючих!",
        "event_date": datetime.now() + timedelta(days=30),
        "location": "Стадіон 'Олімпійський', вул. Спортивна, 1",
        "price": 150.00,
        "sport_type_name": "Футбол"
    },
    {
        "name": "Турнір з баскетболу 'Весняний кубок'",
        "description": "Відкритий турнір з баскетболу для команд різного рівня. Призи та нагороди!",
        "event_date": datetime.now() + timedelta(days=45),
        "location": "Спортивний комплекс 'Арена', вул. Баскетбольна, 5",
        "price": 200.00,
        "sport_type_name": "Баскетбол"
    },
    {
        "name": "Відкритий турнір з тенісу",
        "description": "Турнір з тенісу для гравців усіх рівнів. Реєстрація обов'язкова.",
        "event_date": datetime.now() + timedelta(days=20),
        "location": "Тенісний клуб 'Ас', вул. Тенісна, 10",
        "price": 300.00,
        "sport_type_name": "Теніс"
    },
    {
        "name": "Змагання з плавання 'Вільний стиль'",
        "description": "Змагання з плавання на різних дистанціях. Відкрито для всіх вікових груп.",
        "event_date": datetime.now() + timedelta(days=15),
        "location": "Бассейн 'Аква', вул. Водна, 3",
        "price": 100.00,
        "sport_type_name": "Плавання"
    },
    {
        "name": "Товариський матч з волейболу",
        "description": "Товариський матч між командами. Безкоштовний вхід для глядачів!",
        "event_date": datetime.now() + timedelta(days=10),
        "location": "Спортивна зала 'Волейбол', вул. Спортивна, 15",
        "price": None,  # Безкоштовно
        "sport_type_name": "Волейбол"
    },
    {
        "name": "Марафон 'Міський біг'",
        "description": "Щорічний марафон по місту. Дистанції: 5км, 10км, 21км, 42км.",
        "event_date": datetime.now() + timedelta(days=60),
        "location": "Старт: Центральна площа міста",
        "price": 250.00,
        "sport_type_name": "Легка атлетика"
    }
]

print("Створення спортивних подій...")
for event_data in events_data:
    sport_type_name = event_data.pop("sport_type_name")
    sport_type = SportType.query.filter_by(name=sport_type_name).first()
    
    if sport_type:
        event_data["sport_type_id"] = sport_type.id
        event_data["user_id"] = user.id
        
        # Перевіряємо чи не існує вже така подія
        existing = SportEvent.query.filter_by(
            name=event_data["name"],
            event_date=event_data["event_date"]
        ).first()
        
        if not existing:
            event = SportEvent(**event_data)
            db.session.add(event)
            print(f"  ✓ Додано: {event_data['name']} ({sport_type_name})")
        else:
            print(f"  - Вже існує: {event_data['name']}")
    else:
        print(f"  ✗ Помилка: Вид спорту '{sport_type_name}' не знайдено")

db.session.commit()
print("\nСпортивні події створені!")
print(f"\nВсього видів спорту: {SportType.query.count()}")
print(f"Всього подій: {SportEvent.query.count()}")

