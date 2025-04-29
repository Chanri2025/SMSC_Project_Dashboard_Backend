from flask import Blueprint, request, jsonify
from models.work_day_entry import WorkDayEntry
from sqlalchemy import or_, and_
from models.project import Project
from database import db
from datetime import datetime

work_day_entry_bp = Blueprint('work_day_entry_bp', __name__)


# ✅ Create a new work entry
@work_day_entry_bp.route('/create', methods=['POST'])
def create_work_entry():
    data = request.get_json()

    required_fields = ['user_id', 'hours_elapsed', 'project_name', 'project_subpart', 'assigned_by', 'assigned_to']

    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    if data['hours_elapsed'] > 8:
        return jsonify({'message': 'hours_elapsed cannot be more than 8'}), 400

    new_entry = WorkDayEntry(
        user_id=data['user_id'],
        work_date=datetime.strptime(data['work_date'], "%Y-%m-%d") if data.get('work_date') else datetime.utcnow(),
        hours_elapsed=data['hours_elapsed'],
        project_name=data['project_name'],
        project_subpart=data['project_subpart'],
        issues=data.get('issues', []),
        is_done=data.get('is_done', False),
        assigned_by=data['assigned_by'],
        assigned_to=data['assigned_to']
    )

    db.session.add(new_entry)

    # ✅ Update related project hours
    project = Project.query.filter_by(project_name=data['project_name']).first()
    if project:
        project.total_elapsed_hrs = (project.total_elapsed_hrs or 0) + data['hours_elapsed']

        updated_subparts = []
        for subpart in project.project_subparts:
            if subpart['project_subpart_name'] == data['project_subpart']:
                subpart['hours_elapsed'] = (subpart.get('hours_elapsed') or 0) + data['hours_elapsed']
            updated_subparts.append(subpart)

        project.project_subparts = updated_subparts
    print(project)

    db.session.commit()

    return jsonify({'message': 'Work Day Entry created successfully', 'id': new_entry.id}), 201


# ✅ Get all work entries
@work_day_entry_bp.route('/all', methods=['GET'])
def get_all_work_entries():
    entries = WorkDayEntry.query.order_by(WorkDayEntry.work_date.desc()).all()

    result = [{
        'id': e.id,
        'user_id': e.user_id,
        'work_date': e.work_date.strftime('%Y-%m-%d'),
        'hours_elapsed': e.hours_elapsed,
        'project_name': e.project_name,
        'project_subpart': e.project_subpart,
        'issues': e.issues,
        'is_done': e.is_done,
        'assigned_by': e.assigned_by,
        'assigned_to': e.assigned_to,
        'created_at': e.created_at,
        'updated_at': e.updated_at
    } for e in entries]

    return jsonify({'entries': result, 'total_entries': len(result)}), 200


# ✅ Update a work entry
@work_day_entry_bp.route('/update/<int:entry_id>', methods=['PUT'])
def update_work_entry(entry_id):
    entry = WorkDayEntry.query.get(entry_id)
    if not entry:
        return jsonify({'message': 'Work entry not found'}), 404

    data = request.get_json()
    old_hours = entry.hours_elapsed

    if 'hours_elapsed' in data:
        if data['hours_elapsed'] > 8:
            return jsonify({'message': 'hours_elapsed cannot be more than 8'}), 400
        entry.hours_elapsed = data['hours_elapsed']

    if 'project_name' in data:
        entry.project_name = data['project_name']

    if 'project_subpart' in data:
        entry.project_subpart = data['project_subpart']

    if 'issues' in data:
        entry.issues = data['issues']

    if 'is_done' in data:
        entry.is_done = data['is_done']

    db.session.commit()

    # ✅ After updating the work entry, update the related project
    project = Project.query.filter_by(project_name=entry.project_name).first()
    if project:
        diff = (entry.hours_elapsed or 0) - (old_hours or 0)
        project.total_elapsed_hrs = (project.total_elapsed_hrs or 0) + diff

        updated_subparts = []
        for subpart in project.project_subparts:
            if subpart['project_subpart_name'] == entry.project_subpart:
                subpart['hours_elapsed'] = (subpart.get('hours_elapsed') or 0) + diff
            updated_subparts.append(subpart)

        project.project_subparts = updated_subparts
        db.session.commit()

    return jsonify({'message': 'Work entry updated successfully'}), 200


# ✅ Filter work entries

# ─── 1. CONFIGURE YOUR FILTERABLE FIELDS ──────────────────────────────────────
# key = query-param name
# col = the model column
# type= a function to coerce the string → the right Python type
# op  = "eq" for == or "ilike" for case-insensitive partial match
FILTERS = {
    'user_id':        {'col': WorkDayEntry.user_id,       'type': int,      'op': 'eq'},
    'assigned_by':    {'col': WorkDayEntry.assigned_by,   'type': int,      'op': 'eq'},
    'assigned_to':    {'col': WorkDayEntry.assigned_to,   'type': int,      'op': 'eq'},
    'is_done':        {'col': WorkDayEntry.is_done,       'type': lambda v: v.lower() == 'true', 'op': 'eq'},
    'project_name':   {'col': WorkDayEntry.project_name,  'type': str,      'op': 'ilike'},
    'project_subpart':{'col': WorkDayEntry.project_subpart,'type': str,      'op': 'ilike'},
    'work_date':      {'col': WorkDayEntry.work_date,     'type': lambda v: datetime.strptime(v, '%Y-%m-%d').date(), 'op': 'eq'},
    # → in future just add, e.g. 'hours_elapsed': {'col': WorkDayEntry.hours_elapsed, 'type': float, 'op': 'eq'}
}

@work_day_entry_bp.route('/filter', methods=['GET'])
def filter_work_entries():
    # ─── 2. PULL OUT YOUR ARGS ────────────────────────────────────────────────
    args = request.args.to_dict()

    # default AND logic
    match_any = args.pop('match_any', 'false').lower() == 'true'

    # if both user_id & assigned_to present without explicit match_any, auto-OR them
    if 'user_id' in args and 'assigned_to' in args and 'match_any' not in request.args:
        match_any = True

    # ─── 3. BUILD UP CONDITIONS ───────────────────────────────────────────────
    conditions = []
    for key, raw in args.items():
        cfg = FILTERS.get(key)
        if not cfg or raw == '':
            continue
        try:
            val = cfg['type'](raw)
        except Exception:
            # failed to parse, skip
            continue

        col = cfg['col']
        if cfg['op'] == 'eq':
            conditions.append(col == val)
        elif cfg['op'] == 'ilike':
            conditions.append(col.ilike(f"%{val}%"))

    # ─── 4. APPLY FILTERS, DISTINCT & SORT ───────────────────────────────────
    query = WorkDayEntry.query
    if conditions:
        if match_any:
            query = query.filter(or_(*conditions))
        else:
            query = query.filter(and_(*conditions))

    entries = (
        query
        .distinct()
        .order_by(WorkDayEntry.work_date.desc())
        .all()
    )

    # ─── 5. SERIALIZE ─────────────────────────────────────────────────────────
    result = []
    for e in entries:
        result.append({
            'id':               e.id,
            'user_id':          e.user_id,
            'work_date':        e.work_date.strftime('%Y-%m-%d'),
            'hours_elapsed':    e.hours_elapsed,
            'project_name':     e.project_name,
            'project_subpart':  e.project_subpart,
            'issues':           e.issues,
            'is_done':          e.is_done,
            'assigned_by':      e.assigned_by,
            'assigned_to':      e.assigned_to,
            'created_at':       e.created_at.isoformat(),
            'updated_at':       e.updated_at.isoformat(),
        })

    return jsonify({'entries': result, 'total_entries': len(result)}), 200
