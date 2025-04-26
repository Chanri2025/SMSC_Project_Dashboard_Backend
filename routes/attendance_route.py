from flask import Blueprint, request, jsonify
from models.attendance_log import AttendanceLog
from database import db

attendance_bp = Blueprint("attendance_bp", __name__, url_prefix='/attendance')


@attendance_bp.route("/", methods=["POST"])
def create_attendance():
    data = request.get_json() or {}
    required = ["employee_id", "date", "in_time", "out_time"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    log = AttendanceLog(
        employee_id=data["employee_id"],
        date=data["date"],
        in_time=data["in_time"],
        out_time=data["out_time"]
    )
    try:
        db.session.add(log)
        db.session.commit()
        return jsonify(log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating log", "error": str(e)}), 500


@attendance_bp.route("/all", methods=["GET"])
def get_attendance():
    logs = AttendanceLog.query.all()
    return jsonify([
        {
            "id": log.id,
            "employee_id": log.employee_id,
            "date": log.date,
            "in_time": log.in_time,
            "out_time": log.out_time
        }
        for log in logs
    ]), 200


@attendance_bp.route("/<int:log_id>", methods=["GET"])
def get_attendance_log(log_id):
    log = AttendanceLog.query.get_or_404(log_id)
    return jsonify({
        "id": log.id,
        "employee_id": log.employee_id,
        "date": log.date,
        "in_time": log.in_time,
        "out_time": log.out_time
    }), 200


@attendance_bp.route("/<int:log_id>", methods=["PUT"])
def update_attendance(log_id):
    data = request.get_json() or {}
    log = AttendanceLog.query.get_or_404(log_id)
    try:
        # Only update the fields that actually exist
        log.employee_id = data.get("employee_id", log.employee_id)
        log.date = data.get("date", log.date)
        log.in_time = data.get("in_time", log.in_time)
        log.out_time = data.get("out_time", log.out_time)

        db.session.commit()
        return jsonify({"message": "Attendance log updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating log", "error": str(e)}), 500


@attendance_bp.route("/delete/<int:log_id>", methods=["DELETE"])
def delete_attendance(log_id):
    try:
        log = AttendanceLog.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting log", "error": str(e)}), 500


@attendance_bp.route("/employee/<string:employee_id>", methods=["GET"])
def get_attendance_by_employee(employee_id):
    logs = AttendanceLog.query.filter_by(employee_id=employee_id).all()
    return jsonify([
        {
            "id": log.id,
            "employee_id": log.employee_id,
            "date": log.date,
            "in_time": log.in_time,
            "out_time": log.out_time
        }
        for log in logs
    ]), 200
