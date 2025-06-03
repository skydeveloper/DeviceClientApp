# Файл: DeviceClientApp/programmer_interface.py
import time
import random
import logging

# Препоръчително е да използвате логер, вместо print
logger = logging.getLogger("DeviceClientLogger")
if not logger.handlers:  # Конфигурираме логера, само ако не е вече конфигуриран
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def start_actual_task(module_serials, active_slots, item_name):
    """
    Тази функция трябва да съдържа реалната логика за стартиране
    на вашата програма за програмиране/тестване, която управлявате.
    Тя трябва да връща кортеж (bool: успех, str: съобщение за резултата)
    """
    logger.info(f"ProgrammerInterface: Получена заявка за задача.")
    logger.info(f"  Изделие: {item_name}")
    logger.info(f"  Активни гнезда: {active_slots}")
    logger.info(f"  Серийни номера: {module_serials}")

    # --- ВАШАТА ЛОГИКА ТУК ---
    # Това е мястото, където ще извикате вашата .exe програма,
    # ще комуникирате с хардуера, ще четете файлове и т.н.
    #
    # Примерна симулация на работа:
    logger.info("ProgrammerInterface: Симулирам процес на програмиране/тестване...")
    active_module_details = []
    for i, is_active in enumerate(active_slots):
        if is_active and module_serials[i]:
            active_module_details.append(f"Гнездо {i + 1}: {module_serials[i]}")

    if not active_module_details:
        message = "Няма активни модули за обработка."
        logger.warning(f"ProgrammerInterface: {message}")
        return False, message

    status_message = f"Обработка на {item_name} за модули: {'; '.join(active_module_details)}"
    logger.info(status_message)

    # Симулираме време за изпълнение
    time.sleep(random.randint(3, 8))

    # Симулираме резултат
    if random.choice([True, True, False]):  # ~66% шанс за успех
        success_message = f"Задачата за '{item_name}' завърши успешно за модули: {'; '.join(active_module_details)}."
        logger.info(f"ProgrammerInterface: {success_message}")
        return True, success_message
    else:
        error_message = f"Възникна симулирана грешка по време на задачата за '{item_name}'."
        logger.error(f"ProgrammerInterface: {error_message}")
        return False, error_message


def get_device_current_status():
    """
    (Опционално) Връща текущия статус на програматора/тестера, ако има такъв.
    """
    # Засега просто връщаме примерен статичен статус
    return {"status": "idle", "message": "Устройството е готово за нови задачи."}