# Файл: DeviceClientApp/programmer_interface.py
import time
import random
import logging
from datetime import datetime

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
    Тя трябва да връща речник с детайли за изпълнението.
    """
    logger.info(f"ProgrammerInterface: Получена заявка за задача.")
    logger.info(f"  Изделие: {item_name}")
    logger.info(f"  Активни гнезда: {active_slots}")
    logger.info(f"  Серийни номера: {module_serials}")

    # --- ВАШАТА ЛОГИКА ТУК ---
    # Примерна симулация на работа:
    logger.info("ProgrammerInterface: Симулирам процес на програмиране/тестване...")
    time.sleep(random.randint(3, 8)) # Симулираме време за изпълнение

    slot_results = []
    overall_success = True
    active_module_count = 0

    for i, is_active in enumerate(active_slots):
        result = {
            "slot_index": i + 1,
            "is_active": is_active,
            "serial_number": module_serials[i],
            "status": "N/A", # Not Active
            "message": "Гнездото не е активно."
        }
        if is_active:
            active_module_count += 1
            if not module_serials[i]:
                result["status"] = "FAIL"
                result["message"] = "Гнездото е активно, но липсва сериен номер."
                overall_success = False
            else:
                # Симулираме индивидуален резултат за всяко активно гнездо
                if random.choice([True, True, False]): # ~66% шанс за успех на гнездо
                    result["status"] = "PASS"
                    result["message"] = f"Програмиране успешно. Версия: {random.randint(1, 3)}.0"
                else:
                    result["status"] = "FAIL"
                    result["message"] = "Грешка при верификация на паметта."
                    overall_success = False
        slot_results.append(result)

    if active_module_count == 0:
        overall_success = False
        final_message = "Няма активни модули за обработка."
    elif overall_success:
        final_message = f"Задачата за '{item_name}' завърши успешно."
    else:
        final_message = f"Задачата за '{item_name}' завърши с грешки."

    logger.info(f"ProgrammerInterface: {final_message}")
    return {
        "success": overall_success,
        "message": final_message,
        "item_name": item_name,
        "timestamp": datetime.now().isoformat(),
        "slot_results": slot_results
    }


def get_device_current_status():
    """
    (Опционално) Връща текущия статус на програматора/тестера, ако има такъв.
    """
    # Засега просто връщаме примерен статичен статус
    return {"status": "idle", "message": "Устройството е готово за нови задачи."}