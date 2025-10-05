"""
Country Data API Routes - Datos pre-calculados
Sirve datos desde SQLite ultra-rápido (< 10ms)
"""
from flask import Blueprint, jsonify, request
import sqlite3
import json
import os
from datetime import datetime

country_bp = Blueprint('country', __name__)

def get_country_data_from_db(iso3):
    """Obtener datos de un país desde SQLite (< 10ms)"""
    db_path = 'data/country_indicators.db'
    
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data_json, last_updated, next_update FROM country_indicators WHERE iso3 = ?',
            (iso3.upper(),)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row[0])
            data['cache_info'] = {
                'last_updated': row[1],
                'next_update': row[2],
                'source': 'sqlite'
            }
            return data
        return None
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return None

def get_country_data_from_json(iso3):
    """Fallback: obtener datos desde JSON"""
    json_path = 'data/country_indicators.json'
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            if iso3.upper() in data:
                country_data = data[iso3.upper()]
                country_data['cache_info'] = {
                    'source': 'json_fallback',
                    'last_updated': country_data.get('metadata', {}).get('last_updated')
                }
                return country_data
        except Exception as e:
            print(f"[ERROR] JSON error: {e}")
    
    return None

@country_bp.route('/api/country/<iso3>')
def get_country_data(iso3):
    """
    Obtener todos los indicadores de un país (< 10ms)
    
    Args:
        iso3 (str): Código ISO3 del país (ej: EGY, NGA)
        
    Returns:
        JSON con todos los indicadores del país
    """
    if not iso3 or len(iso3) != 3:
        return jsonify({'error': 'ISO3 code must be 3 characters'}), 400
    
    # Intentar SQLite primero (más rápido)
    data = get_country_data_from_db(iso3)
    
    # Fallback a JSON si SQLite falla
    if data is None:
        data = get_country_data_from_json(iso3)
    
    if data is None:
        return jsonify({
            'error': f'Country {iso3.upper()} not found',
            'available_countries': get_available_countries()
        }), 404
    
    return jsonify(data)

@country_bp.route('/api/countries')
def get_available_countries():
    """Listar todos los países disponibles"""
    try:
        # Intentar SQLite primero
        db_path = 'data/country_indicators.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT iso3, country_name, last_updated FROM country_indicators')
            rows = cursor.fetchall()
            conn.close()
            
            return {
                'countries': [
                    {
                        'iso3': row[0],
                        'name': row[1],
                        'last_updated': row[2]
                    } for row in rows
                ],
                'total': len(rows),
                'source': 'sqlite'
            }
        
        # Fallback a JSON
        json_path = 'data/country_indicators.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return {
                'countries': [
                    {
                        'iso3': iso3,
                        'name': country_data.get('country_name', iso3),
                        'last_updated': country_data.get('metadata', {}).get('last_updated')
                    } for iso3, country_data in data.items()
                ],
                'total': len(data),
                'source': 'json'
            }
        
        return {'countries': [], 'total': 0, 'error': 'No data available'}
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@country_bp.route('/api/health')
def health_check():
    """Check system status"""
    db_available = os.path.exists('data/country_indicators.db')
    json_available = os.path.exists('data/country_indicators.json')
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_sources': {
            'sqlite': db_available,
            'json': json_available
        },
        'message': 'Country data API running'
    })