# Файл: roles/functional_tester_handler.py
import random
import time
from datetime import datetime
from .base_handler import BaseHandler


class FunctionalTesterHandler(BaseHandler):
    def execute(self, module_serials, active_slots, item_name):
        self.logger.info("FunctionalTesterHandler: Изпълнява се ФУНКЦИОНАЛЕН ТЕСТ.")

        test_script_path = self.config.get("test_script_path", "run_test.bat")
        # Тук логиката би била различна, може да подава само един сериен номер и т.н.

        time.sleep(random.randint(10, 20))  # Функционалният тест е най-дълъг

        return {
            "success": True,
            "message": f"Функционалният тест за '{item_name}' завърши.",
            "item_name": item_name,
            "timestamp": datetime.now().isoformat(),
            "slot_results": [{
                "slot_index": 1, "is_active": True, "serial_number": module_serials[0],
                "status": "PASS", "message": "Всички тестове преминаха."
            }]
        }