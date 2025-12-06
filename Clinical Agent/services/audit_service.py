"""Audit logging service for tracking system usage."""

import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from models import AuditEntry
from config import Config


class AuditService:
    """Service for logging and retrieving audit events."""
    
    def __init__(self, db_path: str = None):
        """Initialize audit service with database path."""
        self.db_path = db_path or Config.AUDIT_DB_PATH
        self.init_db_if_needed()
    
    def init_db_if_needed(self):
        """Create audit log table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                patient_id TEXT,
                risk_level TEXT,
                summary_text TEXT,
                raw_json TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_event(
        self,
        event_type: str,
        patient_id: str = "",
        payload: dict = None,
        risk_level: str = None
    ) -> int:
        """
        Log an event to the audit database.
        
        Args:
            event_type: Type of event (Q&A, INTERACTION_CHECK, RISK_SCORE)
            patient_id: Patient identifier
            payload: Dictionary of event data
            risk_level: Risk level if applicable
            
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create summary text
        summary_text = self._create_summary(event_type, payload)
        
        # Serialize payload
        raw_json = json.dumps(payload) if payload else "{}"
        
        # Create audit entry
        entry = AuditEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            patient_id=patient_id,
            risk_level=risk_level,
            summary_text=summary_text,
            raw_json=raw_json
        )
        
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, event_type, patient_id, risk_level, summary_text, raw_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, entry.to_tuple())
        
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        
        return row_id
    
    def _create_summary(self, event_type: str, payload: dict) -> str:
        """Create a human-readable summary of the event."""
        if not payload:
            return f"{event_type} event"
        
        if event_type == "Q&A":
            question = payload.get("question", "")
            return f"Q&A: {question[:100]}..." if len(question) > 100 else f"Q&A: {question}"
        
        elif event_type == "INTERACTION_CHECK":
            num_interactions = payload.get("num_interactions", 0)
            meds = payload.get("medications", [])
            return f"Checked {len(meds)} medication(s), found {num_interactions} interaction(s)"
        
        elif event_type == "RISK_SCORE":
            score = payload.get("score", 0)
            label = payload.get("label", "Unknown")
            return f"Risk assessment: {label} (score: {score})"
        
        return f"{event_type} event"
    
    def get_recent_events(self, limit: int = 100) -> List[AuditEntry]:
        """
        Retrieve recent audit events.
        
        Args:
            limit: Maximum number of events to retrieve
            
        Returns:
            List of AuditEntry objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, event_type, patient_id, risk_level, summary_text, raw_json
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            entry = AuditEntry(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                patient_id=row[3] or "",
                risk_level=row[4],
                summary_text=row[5],
                raw_json=row[6]
            )
            events.append(entry)
        
        return events
    
    def get_events_by_patient(self, patient_id: str, limit: int = 50) -> List[AuditEntry]:
        """
        Retrieve events for a specific patient.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of events
            
        Returns:
            List of AuditEntry objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, event_type, patient_id, risk_level, summary_text, raw_json
            FROM audit_logs
            WHERE patient_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (patient_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            entry = AuditEntry(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                patient_id=row[3] or "",
                risk_level=row[4],
                summary_text=row[5],
                raw_json=row[6]
            )
            events.append(entry)
        
        return events
    
    def get_statistics(self) -> dict:
        """Get summary statistics about audit logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        total = cursor.fetchone()[0]
        
        # Events by type
        cursor.execute("SELECT event_type, COUNT(*) FROM audit_logs GROUP BY event_type")
        by_type = dict(cursor.fetchall())
        
        # Events by risk level
        cursor.execute("SELECT risk_level, COUNT(*) FROM audit_logs WHERE risk_level IS NOT NULL GROUP BY risk_level")
        by_risk = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_events": total,
            "by_type": by_type,
            "by_risk_level": by_risk
        }
    
    def export_to_csv(self, filepath: str, limit: int = None):
        """
        Export audit logs to CSV file.
        
        Args:
            filepath: Path to output CSV file
            limit: Optional limit on number of records
        """
        import csv
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, timestamp, event_type, patient_id, risk_level, summary_text FROM audit_logs ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Timestamp', 'Event Type', 'Patient ID', 'Risk Level', 'Summary'])
            writer.writerows(rows)
