from flask import Blueprint, request, jsonify
from models.attendance_log import AttendanceLog
from database import db

attendance_bp = Blueprint("attendance_bp", __name__)

@attendance_bp.route("/submit", methods=["POST"])
def submit_attendance():
    data = request.json.get("rows", [])
    try:
        for row in data:
            log = AttendanceLog(
                title=row.get("title"),
                date=row.get("date_text"),
                month=row.get("month"),
                employee_id=row.get("employee_id"),
                name=row.get("name"),
                in_time=row.get("in_time"),
                out_time=row.get("out_time"),
                working_hours=row.get("working_hours"),
            )
            db.session.add(log)
        db.session.commit()
        return jsonify({"message": "Attendance logs saved."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error saving logs", "error": str(e)}), 500

@attendance_bp.route("/all", methods=["GET"])
def get_attendance():
    logs = AttendanceLog.query.all()
    return jsonify([{
        "id": log.id,
        "title": log.title,
        "date": log.date,
        "month": log.month,
        "employee_id": log.employee_id,
        "name": log.name,
        "in_time": log.in_time,
        "out_time": log.out_time,
        "working_hours": log.working_hours
    } for log in logs])

@attendance_bp.route("/delete/<int:log_id>", methods=["DELETE"])
def delete_attendance(log_id):
    try:
        log = AttendanceLog.query.get(log_id)
        if not log:
            return jsonify({"message": "Log not found"}), 404
        db.session.delete(log)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting log", "error": str(e)}), 500
