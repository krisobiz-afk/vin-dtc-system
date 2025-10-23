from fastapi import APIRouter
from typing import Optional
from sqlalchemy.orm import Session
from vin_dtc_viewer import database, models

router = APIRouter()

@router.get("/vehicles/")
def search_vehicles(
    vin: Optional[str] = None,
    label: Optional[str] = None,
    dtc: Optional[str] = None
):
    """
    Търси по:
    - vin: частично съвпадение
    - label: частично съвпадение
    - dtc: частично съвпадение в кода на грешката
    """
    db: Session = database.SessionLocal()
    query = db.query(models.Vehicle)

    # Ако има DTC филтър, join през релацията errors
    if dtc:
        query = (
            query
            .join(models.Vehicle.errors)
            .filter(models.DTCError.code.ilike(f"%{dtc}%"))
        )

    if vin:
        query = query.filter(models.Vehicle.vin.ilike(f"%{vin}%"))

    if label:
        query = query.filter(models.Vehicle.label.ilike(f"%{label}%"))

    vehicles = query.distinct().all()

    result = []
    for v in vehicles:
        result.append({
            "vin": v.vin,
            "label": v.label,
            "comment": getattr(v, "comment", ""),
            "upload_date": v.upload_date.isoformat() if v.upload_date else ""
        })
    db.close()
    return result


@router.get("/vehicles/{vin}")
def get_vehicle_by_vin(vin: str):
    db: Session = database.SessionLocal()
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vin == vin).first()
    if not vehicle:
        db.close()
        return {"error": "Not found"}

    modules = db.query(models.Module).filter(models.Module.vehicle_id == vehicle.id).all()
    errors  = db.query(models.DTCError).filter(models.DTCError.vehicle_id == vehicle.id).all()
    db.close()

    return {
        "vin": vehicle.vin,
        "label": vehicle.label,
        "comment": getattr(vehicle, "comment", ""),
        "upload_date": vehicle.upload_date.isoformat() if vehicle.upload_date else "",
        "modules": sorted([
            {
                "name": m.name,
                "part_number": m.part_number,
                "calibration_level": m.calibration_level,
                "strategy": m.strategy
            } for m in modules
        ], key=lambda x: x["part_number"]),
        "errors": [
            {
                "code": e.code,
                "description": e.description,
                "status": e.status,
                "date_detected": e.date_detected.isoformat() if e.date_detected else ""
            } for e in errors
        ]
    }


@router.delete("/vehicles/{vin}")
def delete_vehicle(vin: str):
    db: Session = database.SessionLocal()
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.vin == vin).first()
    if not vehicle:
        db.close()
        return {"error": "Not found"}

    db.query(models.DTCError).filter(models.DTCError.vehicle_id == vehicle.id).delete()
    db.query(models.Module).filter(models.Module.vehicle_id == vehicle.id).delete()
    db.delete(vehicle)
    db.commit()
    db.close()
    return {"status": "deleted", "vin": vin}
