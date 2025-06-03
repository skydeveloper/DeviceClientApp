# Файл: DeviceClientApp/device_client_app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import logging
from threading import Thread

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
ASMG_REPORT_URL = "http://localhost:5000/api/device_report"  # URL на ASMg
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


def report_to_asmg(status_code, message_detail, task_id=None):
    """Изпраща доклад към ASMg сървъра."""
    payload = {"device_id": DEVICE_ID, "status": status_code, "message": message_detail}
    if task_id: payload["task_id"] = task_id

    logger.info(f"Изпращане на доклад към ASMg: {payload}")
    try:
        response = requests.post(ASMG_REPORT_URL, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Отговор от ASMg: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Грешка при докладване към ASMg: {e}")


def execute_task_and_report(serials, slots, item):
    """Обвиваща функция за изпълнение на задачата и докладване."""
    global current_task_info
    current_task_info["is_busy"] = True
    current_task_info["status_message"] = f"Обработка на '{item}'..."
    current_task_info["error_message"] = ""

    success, message = programmer_interface.start_actual_task(serials, slots, item)

    current_task_info["is_busy"] = False
    if success:
        current_task_info["status_message"] = message
        report_to_asmg("task_completed_success", message)
    else:
        current_task_info["status_message"] = "Задачата не завърши успешно."
        current_task_info["error_message"] = message
        report_to_asmg("task_completed_fail", message)


@app.route('/', methods=['GET', 'POST'])
def device_client_index():
    global current_task_info
    if request.method == 'POST':
        if current_task_info["is_busy"]:
            current_task_info["error_message"] = "Устройството е заето, моля изчакайте."
        else:
            # Вземане на данни от формата
            current_task_info["item_name"] = request.form.get('item_name', '')
            serials = [request.form.get(f'serial_num_{i + 1}', '') for i in range(4)]
            slots = [request.form.get(f'slot_{i + 1}_active') == 'on' for i in range(4)]

            current_task_info["module_serial_numbers"] = serials
            current_task_info["active_slots"] = slots

            logger.info("Ръчно стартирана задача от интерфейса на Device Client.")

            # Стартираме задачата в отделна нишка, за да не блокираме UI
            task_thread = Thread(target=execute_task_and_report, args=(serials, slots, current_task_info["item_name"]))
            task_thread.start()
            # Веднага пренасочваме, за да се види началния статус "Обработка..."
            return redirect(url_for('device_client_index'))

    return render_template('device_client_index.html', task_info=current_task_info, device_id=DEVICE_ID)


@app.route('/api/start_task', methods=['POST'])
def api_start_task_from_asmg():
    global current_task_info
    data = request.get_json()

    logger.info(f"DeviceClient: Получена команда от ASMg: {data}")
    current_task_info["last_asmg_command"] = data

    if not data or not all(k in data for k in ["module_serial_numbers", "active_slots", "item_name"]):
        logger.error(f"DeviceClient: Липсващи данни от ASMg: {data}")
        report_to_asmg("command_error_asmg", "Липсващи данни в командата от ASMg.")
        return jsonify({"status": "error", "message": "Липсват данни"}), 400

    if current_task_info["is_busy"]:
        logger.warning(f"DeviceClient: Устройството е заето, командата от ASMg е отказана.")
        report_to_asmg("device_busy_asmg", f"{DEVICE_ID} е зает.")
        return jsonify({"status": "error", "message": f"{DEVICE_ID} е зает в момента."}), 409

    # Приемаме данните от ASMg
    current_task_info["item_name"] = data.get("item_name", "")
    current_task_info["module_serial_numbers"] = data.get("module_serial_numbers", ["", "", "", ""])
    current_task_info["active_slots"] = data.get("active_slots", [False, False, False, False])
    current_task_info["status_message"] = f"Задача от ASMg: Обработка на '{current_task_info['item_name']}'..."
    current_task_info["error_message"] = ""

    report_to_asmg("task_received_asmg", current_task_info["status_message"])

    task_thread = Thread(target=execute_task_and_report, args=(
        current_task_info["module_serial_numbers"],
        current_task_info["active_slots"],
        current_task_info["item_name"]
    ))
    task_thread.start()

    return jsonify({"status": "task_accepted_by_device_client", "device_id": DEVICE_ID}), 200


if __name__ == '__main__':
    logger.info(f"Стартиране на Device Client '{DEVICE_ID}' на порт 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)  # Различен порт от ASMg