# Файл: utils/serial_manager.py
import serial
import time
import logging


class SerialManager:
    """
    Помощен клас за управление на една серийна връзка (COM порт).
    """

    def __init__(self, port, baudrate, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.logger = logging.getLogger("DeviceClientLogger")

    def connect(self):
        """Опитва да отвори серийния порт."""
        if self.ser and self.ser.is_open:
            self.logger.info(f"Порт {self.port} е вече отворен.")
            return True
        try:
            self.logger.info(f"Опитвам да отворя порт {self.port} със скорост {self.baudrate}...")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Изчакваме малко, за да се инициализира хардуера
            if self.ser.is_open:
                self.logger.info(f"Порт {self.port} е отворен успешно.")
                return True
            else:
                self.logger.error(f"Неуспешно отваряне на порт {self.port}.")
                return False
        except serial.SerialException as e:
            self.logger.error(f"Грешка при отваряне на порт {self.port}: {e}")
            self.ser = None
            return False

    def disconnect(self):
        """Затваря серийния порт, ако е отворен."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.logger.info(f"Порт {self.port} е затворен успешно.")
            except Exception as e:
                self.logger.error(f"Грешка при затваряне на порт {self.port}: {e}")
        self.ser = None

    def send_command(self, command, add_newline=True):
        """Изпраща команда към серийния порт."""
        if not self.ser or not self.ser.is_open:
            self.logger.warning(f"Порт {self.port} не е отворен. Командата не е изпратена.")
            return False

        try:
            full_command = command + ('\n' if add_newline else '')
            self.ser.write(full_command.encode('utf-8'))
            self.logger.info(f"Към {self.port} изпратено: '{full_command.strip()}'")
            return True
        except Exception as e:
            self.logger.error(f"Грешка при изпращане към {self.port}: {e}")
            return False

    def read_line(self):
        """Чете един ред от серийния порт."""
        if not self.ser or not self.ser.is_open:
            self.logger.warning(f"Порт {self.port} не е отворен. Не може да се чете.")
            return None

        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line:
                self.logger.info(f"От {self.port} прочетено: '{line}'")
            return line
        except Exception as e:
            self.logger.error(f"Грешка при четене от {self.port}: {e}")
            return None