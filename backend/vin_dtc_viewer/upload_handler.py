from .parser import parse_uuw_file, parse_txt_file, parse_dtc_only_file
from .database import SessionLocal
from .models import Vehicle, Module, DTCError

def process_modules_only_upload(modules_content: str, label: str, comment: str):
    """
    Парсира и запазва само модули (от .uuw или .txt файл),
    създава нов Vehicle запис с label и comment.
    """
    # Определяме формат по съдържание
    if modules_content.lstrip().startswith("<?xml"):
        parsed = parse_uuw_file(modules_content)
    else:
        parsed = parse_txt_file(modules_content)

    vin = parsed["vin"]
    modules = parsed["modules"]

    db = SessionLocal()
    # Създаваме нов автомобил
    vehicle = Vehicle(vin=vin, label=label, comment=comment)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    # Записваме всички модули
    for m in modules:
        module = Module(
            name=m.get("name", ""),
            part_number=m.get("part_number", ""),
            calibration_level=m.get("calibration_level", ""),
            strategy=m.get("strategy", ""),
            vehicle_id=vehicle.id
        )
        db.add(module)

    db.commit()
    db.close()
    return vin

def add_dtc_errors(vin: str, dtc_content: str):
    """
    Парсира DTC грешки от отделен .txt файл и ги добавя към вече създадения Vehicle.
    """
    errors = parse_dtc_only_file(dtc_content)
    db = SessionLocal()

    # Намираме автомобила по VIN
    vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()
    if not vehicle:
        db.close()
        return

    # Добавяме всяка грешка
    for e in errors:
        err = DTCError(
            code=e.get("code", ""),
            description=e.get("description", ""),
            status=e.get("status", ""),
            date_detected=e.get("date_detected"),
            vehicle_id=vehicle.id
        )
        db.add(err)

    db.commit()
    db.close()
