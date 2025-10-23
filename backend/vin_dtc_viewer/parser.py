import xml.etree.ElementTree as ET
from datetime import datetime  # ✅ коректен импорт

def parse_txt_file(content: str):
    lines = content.splitlines()
    vin = ""
    modules = []
    errors = []
    current_module = None

    for line in lines:
        line = line.strip()
        if line.startswith("VIN:"):
            vin = line.split("VIN:")[-1].strip()
        elif " - " in line and line[0].isupper():
            if current_module:
                modules.append(current_module)
            current_module = {"name": line.split(" - ")[0].strip(),
                              "part_number": "",
                              "calibration_level": "",
                              "strategy": ""}
        elif line.lower().startswith("part number:") and current_module:
            current_module["part_number"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("calibration level:") and current_module:
            current_module["calibration_level"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("strategy:") and current_module:
            current_module["strategy"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DTC:"):
            parts = line[4:].split(" - ", 1)
            code = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            errors.append({
                "code": code,
                "description": description,
                "status": "active",
                "date_detected": datetime.utcnow()
            })

    if current_module:
        modules.append(current_module)

    return {
        "vin": vin,
        "modules": modules,
        "errors": errors
    }


def parse_uuw_file(content: str):
    root = ET.fromstring(content)
    vin = root.attrib.get("VIN", "")

    modules = []
    for m in root.findall("m"):
        module_name = m.attrib.get("module", "")
        data_map = {d.attrib.get("DID"): d.attrib.get("Data") for d in m.findall("d")}
        modules.append({
            "name": module_name,
            "part_number": data_map.get("F113", ""),
            "calibration_level": data_map.get("F10A", ""),
            "strategy": data_map.get("F188", "")
        })

    return {
        "vin": vin,
        "modules": modules,
        "errors": []
    }


# backend/vin_dtc_viewer/parser.py
from datetime import datetime
import xml.etree.ElementTree as ET

# ... (другите parse_* функции)

def parse_dtc_only_file(content: str):
    """
    Парсира DTC грешки от .txt файл, извличайки код и описание.
    Поддържа:
      - Редове 'DTC: P0420 - описание'
      - Редове 'Code: P0420 - описание'
    """
    lines = content.splitlines()
    errors = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        code = None
        description = ""
        # Формат 'DTC: P0420 - desc'
        if line.upper().startswith("DTC:"):
            parts = line[4:].split(" - ", 1)
            code = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
        # Формат 'Code: P1632 - desc'
        elif line.startswith("Code:"):
            parts = line.split("Code:", 1)[1].split(" - ", 1)
            code = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
        # Формат '===... DTC P1632:...==='
        elif " DTC " in line and "===" in line:
            # Извличаме кода между 'DTC ' и следващия ':'
            try:
                segment = line.split(" DTC ",1)[1]
                code = segment.split(":",1)[0].strip()
            except:
                code = None

        if code:
            errors.append({
                "code": code,
                "description": description,
                "status": "active",
                "date_detected": datetime.utcnow()
            })

    return errors

