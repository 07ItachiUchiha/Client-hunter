import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

class DatabaseManager:
    """Manages SQLite database operations for business data storage."""
    
    def __init__(self, db_path: str = "data/businesses.db"):
        """Initialize database manager with specified path."""
        self.db_path = db_path
        self.ensure_directory_exists()
        self.init_database()
    
    def ensure_directory_exists(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create businesses table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS businesses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        business_name TEXT NOT NULL,
                        contact TEXT,
                        address TEXT,
                        website TEXT,
                        category TEXT,
                        location TEXT NOT NULL,
                        latitude REAL,
                        longitude REAL,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source TEXT,
                        UNIQUE(business_name, address, location)
                    )
                ''')
                
                # Create scraping_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraping_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT NOT NULL,
                        total_scraped INTEGER DEFAULT 0,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        status TEXT DEFAULT 'running'
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def insert_business(self, business_data: Dict[str, Any]) -> bool:
        """Insert business data into database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO businesses 
                    (business_name, contact, address, website, category, location, 
                     latitude, longitude, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    business_data.get('business_name', ''),
                    business_data.get('contact', ''),
                    business_data.get('address', ''),
                    business_data.get('website', ''),
                    business_data.get('category', ''),
                    business_data.get('location', ''),
                    business_data.get('latitude'),
                    business_data.get('longitude'),
                    business_data.get('source', '')
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logging.error(f"Error inserting business data: {e}")
            return False
    
    def insert_businesses_batch(self, businesses: List[Dict[str, Any]]) -> int:
        """Insert multiple businesses in a single transaction."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data_tuples = [
                    (
                        business.get('business_name', ''),
                        business.get('contact', ''),
                        business.get('address', ''),
                        business.get('website', ''),
                        business.get('category', ''),
                        business.get('location', ''),
                        business.get('latitude'),
                        business.get('longitude'),
                        business.get('source', '')
                    )
                    for business in businesses
                ]
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO businesses 
                    (business_name, contact, address, website, category, location, 
                     latitude, longitude, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data_tuples)
                
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logging.error(f"Error inserting batch businesses: {e}")
            return 0
    
    def get_businesses(self, location: Optional[str] = None, 
                      category: Optional[str] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve businesses with optional filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM businesses WHERE 1=1"
                params = []
                
                if location:
                    query += " AND location LIKE ?"
                    params.append(f"%{location}%")
                
                if category:
                    query += " AND category LIKE ?"
                    params.append(f"%{category}%")
                
                if start_date:
                    query += " AND date(scraped_at) >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND date(scraped_at) <= ?"
                    params.append(end_date)
                
                query += " ORDER BY scraped_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logging.error(f"Error retrieving businesses: {e}")
            return []
    
    def search_businesses(self, search_term: str) -> List[Dict[str, Any]]:
        """Search businesses by name, address, or category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM businesses 
                    WHERE business_name LIKE ? OR address LIKE ? OR category LIKE ?
                    ORDER BY scraped_at DESC
                ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logging.error(f"Error searching businesses: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total businesses
                cursor.execute("SELECT COUNT(*) FROM businesses")
                total_businesses = cursor.fetchone()[0]
                
                # Businesses by location
                cursor.execute('''
                    SELECT location, COUNT(*) as count 
                    FROM businesses 
                    GROUP BY location 
                    ORDER BY count DESC 
                    LIMIT 10
                ''')
                locations = cursor.fetchall()
                
                # Recent scraping activity
                cursor.execute('''
                    SELECT DATE(scraped_at) as date, COUNT(*) as count 
                    FROM businesses 
                    WHERE scraped_at >= date('now', '-7 days')
                    GROUP BY DATE(scraped_at)
                    ORDER BY date DESC
                ''')
                recent_activity = cursor.fetchall()
                
                return {
                    'total_businesses': total_businesses,
                    'locations': [{'location': loc[0], 'count': loc[1]} for loc in locations],
                    'recent_activity': [{'date': act[0], 'count': act[1]} for act in recent_activity]
                }
                
        except Exception as e:
            logging.error(f"Error getting statistics: {e}")
            return {'total_businesses': 0, 'locations': [], 'recent_activity': []}
    
    def create_scraping_session(self, location: str) -> int:
        """Create a new scraping session and return session ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO scraping_sessions (location)
                    VALUES (?)
                ''', (location,))
                
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid is not None else -1
                
        except Exception as e:
            logging.error(f"Error creating scraping session: {e}")
            return -1
    
    def update_scraping_session(self, session_id: int, total_scraped: int, status: str = 'completed'):
        """Update scraping session with results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE scraping_sessions 
                    SET total_scraped = ?, completed_at = CURRENT_TIMESTAMP, status = ?
                    WHERE id = ?
                ''', (total_scraped, status, session_id))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error updating scraping session: {e}")
    
    def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Get statistics for a specific scraping session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT *, 
                           CASE 
                               WHEN completed_at IS NOT NULL 
                               THEN (julianday(completed_at) - julianday(started_at)) * 86400
                               ELSE (julianday('now') - julianday(started_at)) * 86400
                           END as duration_seconds
                    FROM scraping_sessions 
                    WHERE id = ?
                ''', (session_id,))
                
                session = cursor.fetchone()
                
                if session:
                    return {
                        'session_id': session['id'],
                        'location': session['location'],
                        'total_scraped': session['total_scraped'],
                        'status': session['status'],
                        'started_at': session['started_at'],
                        'completed_at': session['completed_at'],
                        'duration': session['duration_seconds'],
                        'success_rate': 100.0 if session['total_scraped'] > 0 else 0.0
                    }
                
                return {}
                
        except Exception as e:
            logging.error(f"Error getting session stats: {e}")
            return {}
    
    def export_to_csv(self, filename: str, location: Optional[str] = None) -> bool:
        """Export businesses to CSV file."""
        try:
            import csv
            
            businesses = self.get_businesses(location=location)
            
            if not businesses:
                return False
            
            filepath = os.path.join("data", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['business_name', 'contact', 'address', 'website', 
                            'category', 'location', 'scraped_at', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for business in businesses:
                    row = {field: business.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            return False
