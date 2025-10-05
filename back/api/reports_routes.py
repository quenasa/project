"""
Citizen reports API routes
"""
from flask import Blueprint, jsonify, request
from services.reports_service import ReportsService

reports_bp = Blueprint('reports', __name__)
reports_service = ReportsService()


@reports_bp.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    """
    GET: Retrieve citizen environmental reports
    POST: Submit a new environmental report (with location coordinates for OpenStreetMap)
    """
    if request.method == 'GET':
        report_type = request.args.get('type')
        reports = reports_service.get_all_reports(report_type)
        return jsonify({
            "data": reports,
            "count": len(reports)
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['type', 'location', 'description']
            if not all(field in data for field in required_fields):
                return jsonify({
                    "error": "Missing required fields",
                    "required": required_fields
                }), 400
            
            # Create report
            report = reports_service.create_report(data)
            
            return jsonify({
                "message": "Report submitted successfully",
                "report": report
            }), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@reports_bp.route('/api/reports/<int:report_id>', methods=['GET', 'PUT'])
def handle_report(report_id):
    """
    GET: Retrieve a specific report
    PUT: Update report status
    """
    if request.method == 'GET':
        report = reports_service.get_report_by_id(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(report)
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            status = data.get('status')
            
            if not status:
                return jsonify({"error": "Status field is required"}), 400
            
            report = reports_service.update_report_status(report_id, status)
            
            if not report:
                return jsonify({"error": "Report not found"}), 404
            
            return jsonify({
                "message": "Report updated successfully",
                "report": report
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
