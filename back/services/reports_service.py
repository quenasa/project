"""
Citizen Reports Service
Handles citizen environmental reports storage and retrieval
"""
from datetime import datetime


class ReportsService:
    """Service for managing citizen environmental reports"""
    
    def __init__(self):
        """Initialize the reports service"""
        # In-memory storage (TODO: Replace with database)
        self.reports = []
    
    def get_all_reports(self, report_type=None):
        """
        Get all citizen reports, optionally filtered by type
        
        Args:
            report_type (str, optional): Filter by report type
            
        Returns:
            list: List of reports
        """
        if report_type:
            return [r for r in self.reports if r['type'] == report_type]
        return self.reports
    
    def get_report_by_id(self, report_id):
        """
        Get a specific report by ID
        
        Args:
            report_id (int): Report ID
            
        Returns:
            dict: Report data or None if not found
        """
        return next((r for r in self.reports if r['id'] == report_id), None)
    
    def create_report(self, report_data):
        """
        Create a new citizen report
        
        Args:
            report_data (dict): Report information
                - type: Report type (illegal_dump, deforestation, etc.)
                - location: {lat, lon, name}
                - description: Report description
                - reporter (optional): Reporter name
                
        Returns:
            dict: Created report with ID and timestamp
        """
        # Validate location coordinates
        location = report_data.get('location', {})
        if 'lat' not in location or 'lon' not in location:
            raise ValueError("Location must include 'lat' and 'lon' coordinates for OpenStreetMap")
        
        report = {
            "id": len(self.reports) + 1,
            "type": report_data['type'],
            "location": location,
            "description": report_data['description'],
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            "reporter": report_data.get('reporter', 'anonymous')
        }
        
        self.reports.append(report)
        return report
    
    def update_report_status(self, report_id, status):
        """
        Update the status of a report
        
        Args:
            report_id (int): Report ID
            status (str): New status (pending, verified, resolved)
            
        Returns:
            dict: Updated report or None if not found
        """
        report = self.get_report_by_id(report_id)
        if report:
            report['status'] = status
            report['updated_at'] = datetime.now().isoformat()
        return report
