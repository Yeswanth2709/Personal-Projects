"""
Audit logging service.
Logs all clinical queries, interactions, and risk assessments for compliance.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sqlite3
from pathlib import Path
from models import AuditLog
from config import BASE_DIR


class AuditService:
    """Service for logging clinical system events."""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = BASE_DIR / "audit.db"
        
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create audit log table if it doesn't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                risk_level TEXT,
                summary TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        
        # Create index on timestamp for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON audit_logs(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type 
            ON audit_logs(event_type)
        """)
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type: str, summary: str, details: Dict[str, Any],
                  user_id: str = "demo-user", risk_level: Optional[str] = None) -> int:
        """
        Log an event to the audit database.
        
        Args:
            event_type: Type of event (qa, interaction_check, risk_assessment, error)
            summary: Brief summary of the event
            details: Detailed event data
            user_id: User identifier
            risk_level: Optional risk level
        
        Returns:
            Log entry ID
        """
        audit_log = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id,
            event_type=event_type,
            risk_level=risk_level,
            summary=summary,
            details=details
        )
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, user_id, event_type, risk_level, summary, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            audit_log.timestamp.isoformat(),
            audit_log.user_id,
            audit_log.event_type,
            audit_log.risk_level,
            audit_log.summary,
            json.dumps(audit_log.details)
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def log_qa_event(self, question: str, answer: str, patient_context: Optional[Dict] = None,
                     retrieved_docs: Optional[List[str]] = None, user_id: str = "demo-user") -> int:
        """
        Log a clinical Q&A event.
        
        Args:
            question: User's question
            answer: System's answer
            patient_context: Optional patient context
            retrieved_docs: Optional list of retrieved document sources
            user_id: User identifier
        
        Returns:
            Log entry ID
        """
        details = {
            "question": question,
            "answer": answer,
            "answer_length": len(answer),
            "patient_context": patient_context or {},
            "retrieved_docs": retrieved_docs or []
        }
        
        summary = f"Clinical Q&A: {question[:100]}..."
        return self.log_event("qa", summary, details, user_id)
    
    def log_interaction_check(self, medications: List[str], interactions_found: int,
                             high_severity: int, patient_id: str = "demo-patient",
                             user_id: str = "demo-user") -> int:
        """
        Log a drug interaction check event.
        
        Args:
            medications: List of medications checked
            interactions_found: Number of interactions found
            high_severity: Number of high severity interactions
            patient_id: Patient identifier
            user_id: User identifier
        
        Returns:
            Log entry ID
        """
        details = {
            "medications": medications,
            "medication_count": len(medications),
            "interactions_found": interactions_found,
            "high_severity_count": high_severity,
            "patient_id": patient_id
        }
        
        risk_level = "high" if high_severity > 0 else ("medium" if interactions_found > 0 else "low")
        summary = f"Interaction check: {len(medications)} medications, {interactions_found} interactions"
        
        return self.log_event("interaction_check", summary, details, user_id, risk_level)
    
    def log_risk_assessment(self, risk_score: float, risk_level: str,
                           patient_id: str = "demo-patient",
                           contributing_factors: Optional[List[Dict]] = None,
                           user_id: str = "demo-user") -> int:
        """
        Log a risk assessment event.
        
        Args:
            risk_score: Calculated risk score
            risk_level: Risk level (Low/Moderate/High)
            patient_id: Patient identifier
            contributing_factors: List of contributing factors
            user_id: User identifier
        
        Returns:
            Log entry ID
        """
        details = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "patient_id": patient_id,
            "contributing_factors": contributing_factors or []
        }
        
        summary = f"Risk assessment: {risk_level} risk (score: {risk_score:.1f})"
        
        return self.log_event("risk_assessment", summary, details, user_id, risk_level.lower())
    
    def log_error(self, error_message: str, error_type: str = "general",
                  context: Optional[Dict] = None, user_id: str = "demo-user") -> int:
        """
        Log an error event.
        
        Args:
            error_message: Error message
            error_type: Type of error
            context: Optional error context
            user_id: User identifier
        
        Returns:
            Log entry ID
        """
        details = {
            "error_message": error_message,
            "error_type": error_type,
            "context": context or {}
        }
        
        summary = f"Error: {error_type} - {error_message[:100]}"
        
        return self.log_event("error", summary, details, user_id)
    
    def get_recent_logs(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve recent audit logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            event_type: Optional filter by event type
        
        Returns:
            List of audit log entries
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if event_type:
            cursor.execute("""
                SELECT * FROM audit_logs 
                WHERE event_type = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (event_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            log = dict(row)
            log['details'] = json.loads(log['details'])
            logs.append(log)
        
        return logs
    
    def get_logs_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retrieve logs within a date range.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
        
        Returns:
            List of audit log entries
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_logs 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            log = dict(row)
            log['details'] = json.loads(log['details'])
            logs.append(log)
        
        return logs
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged events.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        total_events = cursor.fetchone()[0]
        
        # Events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count 
            FROM audit_logs 
            GROUP BY event_type
        """)
        events_by_type = dict(cursor.fetchall())
        
        # High risk events
        cursor.execute("""
            SELECT COUNT(*) FROM audit_logs 
            WHERE risk_level = 'high'
        """)
        high_risk_events = cursor.fetchone()[0]
        
        # Recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM audit_logs 
            WHERE datetime(timestamp) > datetime('now', '-1 day')
        """)
        recent_activity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_events": total_events,
            "events_by_type": events_by_type,
            "high_risk_events": high_risk_events,
            "recent_activity_24h": recent_activity
        }
    
    def export_to_csv(self, output_path: Path, event_type: Optional[str] = None):
        """
        Export audit logs to CSV file.
        
        Args:
            output_path: Path to output CSV file
            event_type: Optional filter by event type
        """
        import csv
        
        logs = self.get_recent_logs(limit=10000, event_type=event_type)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not logs:
                return
            
            # Get all possible fields
            fieldnames = ['id', 'timestamp', 'user_id', 'event_type', 'risk_level', 'summary']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in logs:
                row = {k: log.get(k, '') for k in fieldnames if k != 'details'}
                writer.writerow(row)


# Singleton instance
_audit_service_instance = None


def get_audit_service() -> AuditService:
    """Get or create the audit service singleton."""
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService()
    return _audit_service_instance


if __name__ == "__main__":
    # Test the service
    service = AuditService()
    
    # Test logging different event types
    log_id = service.log_qa_event(
        question="What is the dosage for aspirin?",
        answer="Typical dosage is 81-325mg daily. Consult your physician.",
        patient_context={"age": 65, "medications": ["Warfarin"]}
    )
    print(f"Logged Q&A event with ID: {log_id}")
    
    log_id = service.log_interaction_check(
        medications=["Warfarin", "Aspirin"],
        interactions_found=1,
        high_severity=1
    )
    print(f"Logged interaction check with ID: {log_id}")
    
    # Get recent logs
    recent = service.get_recent_logs(limit=5)
    print(f"\nRecent logs: {len(recent)}")
    
    # Get statistics
    stats = service.get_statistics()
    print(f"\nStatistics: {stats}")
