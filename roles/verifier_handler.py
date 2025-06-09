# Файл: roles/verifier_handler.py
import random
import time
from datetime import datetime
from .base_handler import BaseHandler


class VerifierHandler(BaseHandler):
    def execute(self, module_serials, active_slots, item_name):
        self.logger.info("VerifierHandler: Изпълнява се задача за ВЕРИФИКАЦИЯ И УСПИВАНЕ.")

        turbovalidator_path = self.config.get("turbovalidator_path", "turbovalidator.exe")
        active_serials = [s for i, s in enumerate(module_serials) if active_slots[i] and s]

        if not active_serials:
            return self._create_error_result("Няма активни модули със серийни номера за верификация.")

        command_to_execute = f'"{turbovalidator_path}" --verify --sleep --serials {" ".join(active_serials)}'
        self.logger.info(f"СИМУЛАЦИЯ (Верификация): Команда: {command_to_execute}")

        time.sleep(random.randint(2, 5))  # Верификацията е по-бърза

        # Симулираме резултати
        slot_results = []
        for i, is_active in enumerate(active_slots):
            if is_active and module_serials[i]:
                slot_results.append({
                    "slot_index": i + 1, "is_active": True,
                    "serial_number": module_serials[i], "status": "PASS",
                    "message": "Верификация и 'sleep' успешни."
                })

        return {
            "success": True,
            "message": f"Верификацията за '{item_name}' завърши успешно.",
            "item_name": item_name,
            "timestamp": datetime.now().isoformat(),
            "slot_results": slot_results
        }

    def _create_error_result(self, message):
        # ... (същата като в другия handler)
        pass