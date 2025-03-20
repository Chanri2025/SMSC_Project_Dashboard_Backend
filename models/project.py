from database import db
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from datetime import datetime

class Project(db.Model):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False)
    employee_creator = Column(Integer, ForeignKey('user.id'), nullable=False)
    assigned_empids = Column(JSON, default=[])
    update_logs = Column(JSON, default=[])

    def add_update_log(self, updated_by, message):
        """ Append a new update log entry. """
        if not self.update_logs:
            self.update_logs = []
        self.update_logs.append({
            "updated_by": updated_by,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
