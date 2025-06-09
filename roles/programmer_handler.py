# Файл: roles/programmer_handler.py
import random
import time
from datetime import datetime
from .base_handler import BaseHandler
from utils.serial_manager import SerialManager  # Импортираме новия клас


class ProgrammerHandler(BaseHandler):
    def __init__(self, role_specific_config):
        super().__init__(role_specific_config)
        self.relay_controller = None
        self.serial_injector = None

        # Инициализираме серийните портове от конфигурацията
        com_config = self.config.get("com_ports", {})
        if "relay_controller" in com_config:
            cfg = com_config["relay_controller"]
            self.relay_controller = SerialManager(port=cfg["port"], baudrate=cfg["baudrate"])
            self.relay_controller.connect()  # Свързваме се при стартиране

        if "serial_injector" in com_config:
            cfg = com_config["serial_injector"]
            self.serial_injector = SerialManager(port=cfg["port"], baudrate=cfg["baudrate"])
            self.serial_injector.connect()

    def execute(self, module_serials, active_slots, item_name):
        self.logger.info("ProgrammerHandler: Изпълнява се задача за ПРОГРАМИРАНЕ.")

        # --- НОВА ЛОГИКА ЗА RS232 ---
        # Примерна последователност за едно гнездо
        for i, is_active in enumerate(active_slots):
            if is_active and module_serials[i]:
                serial_num = module_serials[i]
                slot_index = i + 1

                self.logger.info(f"--- Обработка на гнездо {slot_index} (SN: {serial_num}) ---")

                # 1. Включваме реле за съответното гнездо
                if self.relay_controller:
                    self.relay_controller.send_command(f"RELAY_ON_{slot_index}")
                    time.sleep(0.5)  # Изчакваме релето да превключи

                # 2. Подаваме серийния номер към Turbovalidator
                if self.serial_injector:
                    self.serial_injector.send_command(serial_num)
                    response = self.serial_injector.read_line()  # Примерно четене на отговор
                    if response != "OK":
                        self.logger.warning(f"Инжекторът за серийни номера върна неочакван отговор: {response}")

                # 3. Тук бихме стартирали Turbovalidator.exe (симулация)
                self.logger.info(f"СИМУЛАЦИЯ: Стартиране на Turbovalidator за SN: {serial_num}")
                time.sleep(2)

                # 4. Изключваме релето
                if self.relay_controller:
                    self.relay_controller.send_command(f"RELAY_OFF_{slot_index}")

                self.logger.info(f"--- Приключи обработката на гнездо {slot_index} ---")

        # Симулираме финалния резултат както преди
        # (Тази част остава същата)
        # ...

        return {
            "success": True,
            "message": f"Задачата за '{item_name}' завърши.",
            "item_name": item_name,
            "timestamp": datetime.now().isoformat(),
            "slot_results": []  # Трябва да се попълни с реалните резултати
        }

    def __del__(self):
        # Важно: затваряме портовете, когато приложението спре
        if self.relay_controller:
            self.relay_controller.disconnect()
        if self.serial_injector:
            self.serial_injector.disconnect()