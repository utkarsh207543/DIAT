import sqlite3
import json
import os
from datetime import datetime
from neon import neon

class DatabaseManager:
    def __init__(self):
        # Use Neon database if available, otherwise fallback to SQLite
        self.database_url = os.environ.get('DATABASE_URL')
        if self.database_url:
            self.sql = neon(self.database_url)
            self.use_neon = True
            print("✅ Using Neon PostgreSQL database")
        else:
            self.db_path = 'nist_logs.db'
            self.use_neon = False
            print("✅ Using SQLite database")
            self._init_sqlite_db()
    
    def _init_sqlite_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                institution TEXT,
                department TEXT,
                position TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create test_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                original_filename TEXT,
                file_size INTEGER,
                data_length INTEGER,
                file_type TEXT,
                selected_tests TEXT,
                execution_time REAL,
                total_tests INTEGER,
                passed_tests INTEGER,
                failed_tests INTEGER,
                pass_rate REAL,
                overall_assessment TEXT,
                result_file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create file_uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                upload_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, google_id, email, name, institution=None, department=None, position=None, country=None):
        """Add a new user to the database"""
        if self.use_neon:
            result = self.sql('''
                INSERT INTO users (google_id, email, name, institution, department, position, country)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            ''', [google_id, email, name, institution, department, position, country])
            return result[0]['id'] if result else None
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (google_id, email, name, institution, department, position, country)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (google_id, email, name, institution, department, position, country))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
    
    def get_user_by_google_id(self, google_id):
        """Get user by Google ID"""
        if self.use_neon:
            result = self.sql('SELECT * FROM users WHERE google_id = $1', [google_id])
            if result:
                user = result[0]
                return {
                    'id': user['id'],
                    'google_id': user['google_id'],
                    'email': user['email'],
                    'name': user['name'],
                    'institution': user['institution'],
                    'department': user['department'],
                    'position': user['position'],
                    'country': user['country'],
                    'created_at': user['created_at'],
                    'last_login': user['last_login']
                }
            return None
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        if self.use_neon:
            self.sql('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1', [user_id])
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
    
    def log_test_execution(self, user_id, session_id, test_data):
        """Log test execution details"""
        if self.use_neon:
            self.sql('''
                INSERT INTO test_logs (
                    user_id, session_id, original_filename, file_size, data_length,
                    file_type, selected_tests, execution_time, total_tests,
                    passed_tests, failed_tests, pass_rate, overall_assessment,
                    result_file_path
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            ''', [
                user_id, session_id, test_data['original_filename'],
                test_data['file_size'], test_data['data_length'],
                test_data['file_type'], json.dumps(test_data['selected_tests']),
                test_data['execution_time'], test_data['total_tests'],
                test_data['passed_tests'], test_data['failed_tests'],
                test_data['pass_rate'], test_data['overall_assessment'],
                test_data['result_file_path']
            ])
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_logs (
                    user_id, session_id, original_filename, file_size, data_length,
                    file_type, selected_tests, execution_time, total_tests,
                    passed_tests, failed_tests, pass_rate, overall_assessment,
                    result_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, session_id, test_data['original_filename'],
                test_data['file_size'], test_data['data_length'],
                test_data['file_type'], json.dumps(test_data['selected_tests']),
                test_data['execution_time'], test_data['total_tests'],
                test_data['passed_tests'], test_data['failed_tests'],
                test_data['pass_rate'], test_data['overall_assessment'],
                test_data['result_file_path']
            ))
            conn.commit()
            conn.close()
    
    def log_file_upload(self, user_id, session_id, filename, file_size, file_type, upload_path):
        """Log file upload details"""
        if self.use_neon:
            self.sql('''
                INSERT INTO file_uploads (user_id, session_id, original_filename, file_size, file_type, upload_path)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', [user_id, session_id, filename, file_size, file_type, upload_path])
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO file_uploads (user_id, session_id, original_filename, file_size, file_type, upload_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, session_id, filename, file_size, file_type, upload_path))
            conn.commit()
            conn.close()
    
    def get_user_test_history(self, user_id, limit=50):
        """Get user's test execution history"""
        if self.use_neon:
            return self.sql('''
                SELECT * FROM test_logs 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            ''', [user_id, limit])
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM test_logs 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
