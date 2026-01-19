# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from gemini_api import get_gemini_response # Импортируем функцию для работы с Gemini API

# Инициализация Flask-приложения
app = Flask(__name__)
CORS(app) # Включение CORS для всего приложения

# --- Модель данных для персон и диалогов (хранение в памяти) ---
# Каждая персона имеет:
# - 'system_prompt': Начальный промт для AI, определяющий его роль.
# - 'rules': Список динамически добавляемых правил.
# - 'chat_history': История диалога в формате, ожидаемом Gemini API.
personas = {
    "дефолт": {
        "system_prompt": "Ты - полезный и дружелюбный AI-ассистент, готовый помочь пользователю с любыми вопросами.",
        "rules": [],
        "chat_history": []
    },
    "афина": {
        "system_prompt": "Ты - опытный и знающий помощник программиста. Твоя задача - давать четкие, технически грамотные и полезные советы по программированию на различных языках и фреймворках. Будь лаконичной, но исчерпывающей.",
        "rules": [],
        "chat_history": []
    },
    "фортуна": {
        "system_prompt": "Ты - веселый и остроумный юморист. Твоя задача - поднимать настроение пользователя шутками, анекдотами и забавными историями. Используй иронию и сарказм уместно.",
        "rules": [],
        "chat_history": []
    }
}

# Переменная для отслеживания текущей активной персоны по умолчанию
current_persona = "дефолт"

def detect_persona(message: str) -> str:
    """
    Определяет, к какой персоне адресовано сообщение.
    Ищет имя персоны в начале сообщения (без учета регистра) и возвращает её.
    Если имя персоны не найдено, возвращает "дефолт".

    Параметры:
        message (str): Сообщение пользователя.

    Возвращает:
        str: Имя активной персоны.
    """
    global current_persona # Объявляем, что будем изменять глобальную переменную

    # Проверяем, начинается ли сообщение с имени одной из персон
    for persona_name in personas.keys():
        if message.lower().startswith(persona_name.lower() + ","):
            # Если найдено, устанавливаем эту персону как текущую
            current_persona = persona_name
            return persona_name
    
    # Если имя персоны не найдено, возвращаем текущую (по умолчанию "дефолт")
    return current_persona

def add_rule(persona_name: str, rule_text: str) -> None:
    """
    Добавляет новое правило для указанной персоны.

    Параметры:
        persona_name (str): Имя персоны, для которой добавляется правило.
        rule_text (str): Текст правила.
    """
    if persona_name in personas:
        personas[persona_name]["rules"].append(rule_text)
    else:
        print(f"Предупреждение: Персона '{persona_name}' не найдена. Правило не добавлено.")


# Простой тестовый эндпоинт для проверки работы Flask
@app.route('/')
def hello_world():
    """
    Тестовый эндпоинт, который возвращает приветственное сообщение.
    Используется для проверки того, что Flask-приложение запущено и работает.
    """
    return 'Привет, Bessonniy Oracle Backend!'


@app.route('/chat', methods=['POST'])
def chat():
    """
    Эндпоинт для обработки сообщений пользователя и возврата ответов от AI-ассистента.
    
    Принимает:
        JSON-тело с полем 'message' (string) - сообщение пользователя.
    Возвращает:
        JSON-тело с полем 'response' (string) - ответ ассистента.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message field is required"}), 400

    # Определяем активную персону
    active_persona_name = detect_persona(user_message)
    active_persona = personas[active_persona_name]

    # Проверяем, является ли сообщение командой для добавления правила
    rule_command_prefix = f"{active_persona_name}, запомни вот такое правило "
    if user_message.lower().startswith(rule_command_prefix.lower()):
        rule_text = user_message[len(rule_command_prefix):].strip()
        if rule_text:
            add_rule(active_persona_name, rule_text)
            return jsonify({"response": f"Поняла, {active_persona_name}. Я запомнила правило: \"{rule_text}\"."})
        else:
            return jsonify({"response": "Пожалуйста, укажите текст правила после команды 'запомни вот такое правило'."})

    # Собираем все промты и правила для текущей персоны
    system_prompt = active_persona["system_prompt"]
    if active_persona["rules"]:
        system_prompt += "\nДополнительные правила: " + "; ".join(active_persona["rules"])
    
    # Получаем ответ от Gemini API
    try:
        assistant_response = get_gemini_response(user_message, system_prompt=system_prompt, chat_history=active_persona["chat_history"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Произошла внутренняя ошибка сервера: {e}"}), 500

    # Сохраняем сообщение пользователя и ответ ассистента в истории диалога
    active_persona["chat_history"].append({'role': 'user', 'parts': [user_message]})
    active_persona["chat_history"].append({'role': 'model', 'parts': [assistant_response]})

    return jsonify({"response": assistant_response})


@app.route('/rules', methods=['GET', 'POST'])
def rules():
    """
    Эндпоинт для управления правилами AI-ассистента.
    В текущей реализации является заглушкой.
    ---
    GET: Возвращает список всех правил.
    POST: Добавляет новое правило.
    """
    if request.method == 'GET':
        # Заглушка для получения правил
        return jsonify({"message": "Список правил (заглушка)", "rules": []})
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        data = request.get_json()
        new_rule = data.get('rule')
        if not new_rule:
            return jsonify({"error": "Rule field is required"}), 400
        # Заглушка для добавления правила
        return jsonify({"message": f"Правило '{new_rule}' добавлено (заглушка)", "rule": new_rule}), 201

if __name__ == '__main__':
    # Запуск Flask-приложения в режиме отладки.
    # В продакшене следует использовать более надежный WSGI-сервер (например, Gunicorn, uWSGI).
    app.run(debug=True)

