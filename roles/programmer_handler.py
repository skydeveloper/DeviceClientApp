# Файл: roles/programmer_handler.py
import random
import time
from datetime import datetime
from .base_handler import BaseHandler


class ProgrammerHandler(BaseHandler):
    def execute(self, module_serials, active_slots, item_name):
        self.logger.info("ProgrammerHandler: Изпълнява се задача за ПРОГРАМИРАНЕ.")

        turbovalidator_path = self.config.get("turbovalidator_path", "turbovalidator.exe")
        active_serials = [s for i, s in enumerate(module_serials) if active_slots[i] and s]

        if not active_serials:
            return self._create_error_result("Няма активни модули със серийни номера за програмиране.")

        command_to_execute = f'"{turbovalidator_path}" --program --item "{item_name}" --serials {" ".join(active_serials)}'
        self.logger.info(f"СИМУЛАЦИЯ (Програмиране): Команда: {command_to_execute}")

        time.sleep(random.randint(4, 9))

        # --- ПОПЪЛНЕНА ЛОГИКА ЗА РЕЗУЛТАТИ ---
        slot_results = []
        overall_success = True
        active_module_count = 0

        for i, is_active in enumerate(active_slots):
            result = {
                "slot_index": i + 1,
                "is_active": is_active,
                "serial_number": module_serials[i],
                "status": "N/A",
                "message": "Гнездото не е активно."
            }
            if is_active:
                active_module_count += 1
                if not module_serials[i]:
                    result["status"] = "FAIL"
                    result["message"] = "Гнездото е активно, но липсва сериен номер."
                    overall_success = False
                else:
                    if random.choice([True, True, True, False]):  # ~75% шанс за успех
                        result["status"] = "PASS"
                        result["message"] = f"Програмиране успешно. Фърмуер: {random.randint(1, 3)}.0"
                    else:
                        result["status"] = "FAIL"
                        result["message"] = "Грешка при верификация на записа."
                        overall_success = False
            slot_results.append(result)

        if active_module_count == 0:
            overall_success = False
            final_message = "Няма активни модули за обработка."
        elif overall_success:
            final_message = f"Задачата за '{item_name}' завърши успешно."
        else:
            final_message = f"Задачата за '{item_name}' завърши с грешки."

        self.logger.info(f"ProgrammerHandler: {final_message}")

        return {
            "success": overall_success,
            "message": final_message,
            "item_name": item_name,
            "timestamp": datetime.now().isoformat(),
            "slot_results": slot_results
        }

    def _create_error_result(self, message):
        return {
            "success": False, "message": message, "item_name": "N/A",
            "timestamp": datetime.now().isoformat(), "slot_results": []
        }