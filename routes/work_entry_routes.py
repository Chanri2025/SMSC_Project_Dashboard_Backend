from flask import Blueprint, request, jsonify
from models.work_entry import WorkEntry
from models.employee import Employee
from database import db
from datetime import datetime

work_entry_bp = Blueprint('work_entry_bp', __name__)


@work_entry_bp.route('/submit', methods=['POST'])
def submit_entry():
    data = request.get_json()
    required_fields = ['employee_id', 'tasks', 'work_status']

    if any(field not in data or not data[field] for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    employee = Employee.query.filter_by(employee_id=data['employee_id']).first()
    if not employee:
        return jsonify({'message': 'Invalid employee ID'}), 404

    entry = WorkEntry(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        date=datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else datetime.utcnow(),
        expected_date_of_delivery=datetime.strptime(data.get('expected_date_of_delivery'), '%Y-%m-%d') if data.get(
            'expected_date_of_delivery') else None,
        work_status=data['work_status'],
        tasks=data['tasks'],
        issue=data.get('issue', '')
    )

    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.id), 201


@work_entry_bp.route('/all', methods=['GET'])
def get_all_entries():
    entries = (
        db.session.query(WorkEntry, Employee)
        .join(Employee, Employee.employee_id == WorkEntry.employee_id)
        .order_by(WorkEntry.date.desc())
        .all()
    )
    result = [{
        'id': e.id,
        'employee_id': emp.employee_id,
        'full_name': emp.full_name,
        'date': e.date.strftime('%Y-%m-%d'),
        'expected_date_of_delivery': e.expected_date_of_delivery.strftime(
            '%Y-%m-%d') if e.expected_date_of_delivery else None,
        'work_status': e.work_status,
        'tasks': e.tasks,
        'issue': e.issue
    } for e, emp in entries]

    return jsonify(result)


@work_entry_bp.route('/by-employee', methods=['GET'])
def get_entries_by_employee_id():
    employee_id = request.args.get('employee_id')

    if not employee_id:
        return jsonify({'message': 'employee_id is required as a query parameter'}), 400

    entries = (
        db.session.query(WorkEntry, Employee)
        .join(Employee, Employee.employee_id == WorkEntry.employee_id)
        .filter(WorkEntry.employee_id == employee_id)
        .order_by(WorkEntry.date.desc())
        .all()
    )

    result = [{
        'id': e.id,
        'employee_id': emp.employee_id,
        'full_name': emp.full_name,
        'date': e.date.strftime('%Y-%m-%d'),
        'expected_date_of_delivery': e.expected_date_of_delivery.strftime(
            '%Y-%m-%d') if e.expected_date_of_delivery else None,
        'work_status': e.work_status,
        'tasks': e.tasks,
        'issue': e.issue
    } for e, emp in entries]

    return jsonify(result)


@work_entry_bp.route('/edit', methods=['PUT'])
def edit_work_entry():
    data = request.get_json()
    employee_id = data.get('employee_id')
    work_entry_id = data.get('id')  # This is the ID of the work entry to update

    if not employee_id or not work_entry_id:
        return jsonify({'message': 'employee_id and work_entry id are required'}), 400

    work_entry = (
        db.session.query(WorkEntry)
        .filter_by(id=work_entry_id, employee_id=employee_id)
        .first()
    )

    if not work_entry:
        return jsonify({'message': 'Work entry not found'}), 404

    # Update fields if provided
    work_entry.date = datetime.strptime(data.get('date'), '%Y-%m-%d') if data.get('date') else work_entry.date
    work_entry.expected_date_of_delivery = datetime.strptime(data.get('expected_date_of_delivery'),
                                                             '%Y-%m-%d') if data.get(
        'expected_date_of_delivery') else work_entry.expected_date_of_delivery
    work_entry.work_status = data.get('work_status', work_entry.work_status)
    work_entry.tasks = data.get('tasks', work_entry.tasks)
    work_entry.issue = data.get('issue', work_entry.issue)

    db.session.commit()

    return jsonify({'message': 'Work entry updated successfully'})
