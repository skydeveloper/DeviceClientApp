# Файл: DeviceClientApp/device_client_app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import logging
from threading import Thread
from collections import deque

# Импортираме модула за реалната работа
import programmer_interface

# Конфигурация на логера (същата като в programmer_interface.py за консистентност)
logger = logging.getLogger("DeviceClientLogger")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

app = Flask(__name__)
app.secret_key = "device_client_super_secret_key"  # Променете за продукция!

# Настройки
ASMG_REPORT_URL = "http://localhost:5000/api/device/report"  # URL на новия REST API ендпойнт в ASMg
DEVICE_ID = "Програматор_Участък_Б_01"  # Уникално ID за този клиент

# Глобално състояние на Device Client
current_task_info = {
    "module_serial_numbers": ["", "", "", ""],
    "active_slots": [False, False, False, False],
    "item_name": "",
    "status_message": "Готов за нова задача",
    "error_message": "",
    "is_busy": False,
    "last_asmg_command": None
}
# История на последните 20 задачи (използваме deque за ефективност)
task_history = deque(maxlen=20)


def report_to_asmg(report_type, message, payload=None):
    """Изпраща структуриран доклад към новия REST API на ASMg сървъра."""
    if payload is None:
        payload = {}

    full_payload = {
        "device_id": DEVICE_ID,
        "report_type": report_type,
        "message": message,
        "payload": payload
    }
    logger.info(f"Изпращане на доклад към ASMg: {full_payload}")
    try:
        response = requests.post(ASMG_REPORT_URL, json=full_payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Отговор от ASMg: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Грешка при докладване към ASMg: {e}")


def execute_task_and_report(serials, slots, item):
    """Обвиваща функция за изпълнение на задачата и докладване."""
    global current_task_info, task_history
    current_task_info["is_busy"] = True
    current_task_info["status_message"] = f"Обработка на '{item}'..."
    current_task_info["error_message"] = ""

    # Извикваме реалната задача и получаваме детайлен резултат
    result_data = programmer_interface.start_actual_task(serials, slots, item)

    current_task_info["is_busy"] = False
    current_task_info["status_message"] = result_data["message"]
    if not result_data["success"]:
        current_task_info["error_message"] = "Проверете детайлите в историята на тестовете."

    # Добавяме резултата в началото на историята
    task_history.appendleft(result_data)

    # Изпращаме детайлния резултат към ASMg
    report_to_asmg(
        report_type="test_result",
        message=result_data["message"],
        payload=result_data
    )


@app.route('/', methods=['GET', 'POST'])
def device_client_index():
    global current_task_info
    if request.method == 'POST':
        if current_task_info["is_busy"]:
            current_task_info["error_message"] = "Устройството е заето, моля изчакайте."
        else:
            current_task_info["item_name"] = request.form.get('item_name', '')
            serials = [request.form.get(f'serial_num_{i + 1}', '') for i in range(4)]
            slots = [request.form.get(f'slot_{i + 1}_active') == 'on' for i in range(4)]

            current_task_info["module_serial_numbers"] = serials
            current_task_info["active_slots"] = slots

            logger.info("Ръчно стартирана задача от интерфейса на Device Client.")
            task_thread = Thread(target=execute_task_and_report, args=(serials, slots, current_task_info["item_name"]))
            task_thread.start()
            return redirect(url_for('device_client_index'))

    return render_template('device_client_index.html', task_info=current_task_info, device_id=DEVICE_ID,
                           task_history=list(task_history))


@app.route('/api/start_task', methods=['POST'])
def api_start_task_from_asmg():
    global current_task_info
    data = request.get_json()

    logger.info(f"DeviceClient: Получена команда от ASMg: {data}")
    current_task_info["last_asmg_command"] = data

    if not data or not all(k in data for k in ["module_serial_numbers", "active_slots", "item_name"]):
        logger.error(f"DeviceClient: Липсващи данни от ASMg: {data}")
        report_to_asmg("error_report", "Липсващи данни в командата от ASMg.", data)
        return jsonify({"status": "error", "message": "Липсват данни"}), 400

    if current_task_info["is_busy"]:
        logger.warning(f"DeviceClient: Устройството е заето, командата от ASMg е отказана.")
        report_to_asmg("error_report", f"{DEVICE_ID} е зает и не може да приеме нова задача.", data)
        return jsonify({"status": "error", "message": f"{DEVICE_ID} е зает в момента."}), 409

    current_task_info["item_name"] = data.get("item_name", "")
    current_task_info["module_serial_numbers"] = data.get("module_serial_numbers", ["", "", "", ""])
    current_task_info["active_slots"] = data.get("active_slots", [False, False, False, False])
    current_task_info["status_message"] = f"Задача от ASMg: Обработка на '{current_task_info['item_name']}'..."
    current_task_info["error_message"] = ""

    report_to_asmg("task_received", current_task_info["status_message"], data)

    task_thread = Thread(target=execute_task_and_report, args=(
        current_task_info["module_serial_numbers"],
        current_task_info["active_slots"],
        current_task_info["item_name"]
    ))
    task_thread.start()

    return jsonify({"status": "task_accepted_by_device_client", "device_id": DEVICE_ID}), 200


@app.route('/api/results', methods=['GET'])
def get_results():
    """Нов REST API ендпойнт за извличане на историята с резултати."""
    return jsonify(list(task_history))


if __name__ == '__main__':
    logger.info(f"Стартиране на Device Client '{DEVICE_ID}' на порт 8001...")
    # Уверете се, че debug=True НЕ се използва в продукционна среда!
    app.run(host='0.0.0.0', port=8001, debug=True)