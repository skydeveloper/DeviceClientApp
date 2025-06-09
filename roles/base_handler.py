# Файл: roles/base_handler.py
import logging

class BaseHandler:
    """
    Базов клас за всички типове "роли" на устройството.
    Дефинира общия интерфейс, който всяка роля трябва да имплементира.
    """
    def __init__(self, role_specific_config):
        self.config = role_specific_config
        self.logger = logging.getLogger("DeviceClientLogger")

    def execute(self, module_serials, active_slots, item_name):
        """
        Този метод трябва да бъде имплементиран от всеки наследник.
        Той съдържа специфичната логика за изпълнение на задачата.
        Трябва да връща речник, съдържащ поне:
        {
            "success": bool,
            "message": str,
            "item_name": str,
            "timestamp": str,
            "slot_results": list
        }
        """
        raise NotImplementedError("Методът 'execute' трябва да бъде имплементиран от наследника!")