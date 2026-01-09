# gemini_api.py
import os
import google.generativeai as genai

# Получение API-ключа Gemini из переменных окружения.
# Это обеспечивает безопасность ключа, не допуская его коммита в репозиторий.
os.environ['GOOGLE_API_KEY'] = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def get_gemini_response(user_message: str, system_prompt: str = "", chat_history: list = None) -> str:
    """
    Отправляет запрос к Google Gemini API и возвращает сгенерированный ответ.
    
    Параметры:
        user_message (str): Сообщение пользователя.
        system_prompt (str): Системный промт, определяющий роль и поведение AI (по умолчанию пусто).
        chat_history (list): Список предыдущих сообщений для поддержания контекста диалога.
                             Каждый элемент списка - это словарь с ключами 'role' и 'parts'.
                             Например: [{'role': 'user', 'parts': ['Привет']},
                                          {'role': 'model', 'parts': ['Привет, чем могу помочь?']}]
                                          
    Возвращает:
        str: Сгенерированный ответ от Gemini.
    
    Исключения:
        ValueError: Если не установлен API-ключ Gemini.
        Exception: В случае других ошибок при взаимодействии с Gemini API.
    """
    
    # Проверяем наличие API-ключа.
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("API-ключ Gemini не установлен. Пожалуйста, установите переменную окружения GEMINI_API_KEY.")

    try:
        # Инициализация модели Gemini.
        # Мы используем модель 'gemini-pro' для текстовых задач.
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Формирование сообщений для истории чата, если она есть.
        # Gemini API ожидает историю в формате: [user_message, model_response, user_message, ...]
        messages = []
        if system_prompt:
            # Системный промт передается как первое сообщение от пользователя
            messages.append({'role': 'user', 'parts': [system_prompt]})
            messages.append({'role': 'model', 'parts': ["ОК."]}) # Ответ модели на системный промт
            
        if chat_history:
            for entry in chat_history:
                messages.append(entry)

        # Добавляем текущее сообщение пользователя в историю.
        messages.append({'role': 'user', 'parts': [user_message]})

        # Отправка запроса к Gemini API.
        # Если история не пуста, используем chat.send_message, иначе model.generate_content
        if len(messages) > 1: # Проверяем, есть ли что-то кроме текущего сообщения пользователя
            # Начинаем чат с первого системного промта и истории.
            chat = model.start_chat(history=messages[:-1]) # Передаем всю историю, кроме последнего сообщения пользователя
            response = chat.send_message(user_message)
        else:
            response = model.generate_content(user_message)
        
        # Возвращаем текстовый ответ.
        return response.text

    except Exception as e:
        print(f"Ошибка при обращении к Gemini API: {e}")
        # Можно добавить более детализированную обработку ошибок в зависимости от их типа.
        return f"Извините, произошла ошибка при получении ответа от AI: {e}"


