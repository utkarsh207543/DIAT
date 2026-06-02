#!/usr/bin/env python3
"""
Cleanup utility for NIST application
Removes old files, cleans up database, and manages storage
"""

import os
import sqlite3
import time
from datetime import datetime, timedelta
import argparse

class CleanupUtility:
    def __init__(self, db_path='nist_logs.db'):
        self.db_path = db_path
        self.uploads_dir = 'uploads'
        self.results_dir = 'results'
    
    def cleanup_old_files(self, days_old=30):
        """Remove files older than specified days"""
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0
        
        # Clean uploads directory
        if os.path.exists(self.uploads_dir):
            for filename in os.listdir(self.uploads_dir):
                filepath = os.path.join(self.uploads_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                        print(f"Removed old upload: {filename}")
                    except Exception as e:
                        print(f"Error removing {filename}: {e}")
        
        # Clean results directory
        if os.path.exists(self.results_dir):
            for filename in os.listdir(self.results_dir):
                filepath = os.path.join(self.results_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                        print(f"Removed old result: {filename}")
                    except Exception as e:
                        print(f"Error removing {filename}: {e}")
        
        return removed_count
    
    def cleanup_database(self, days_old=90):
        """Remove old database entries"""
        if not os.path.exists(self.db_path):
            print("Database not found")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Remove old file chunks
        cursor.execute('DELETE FROM file_chunks WHERE created_at < ?', (cutoff_date,))
        chunks_removed = cursor.rowcount
        
        # Remove old test logs (keep user data)
        cursor.execute('DELETE FROM test_logs WHERE created_at < ?', (cutoff_date,))
        logs_removed = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"Removed {chunks_removed} old file chunks")
        print(f"Removed {logs_removed} old test logs")
        
        return chunks_removed + logs_removed
    
    def get_storage_stats(self):
        """Get storage usage statistics"""
        stats = {
            'uploads_size': 0,
            'uploads_count': 0,
            'results_size': 0,
            'results_count': 0,
            'database_size': 0
        }
        
        # Check uploads directory
        if os.path.exists(self.uploads_dir):
            for filename in os.listdir(self.uploads_dir):
                filepath = os.path.join(self.uploads_dir, filename)
                if os.path.isfile(filepath):
                    stats['uploads_size'] += os.path.getsize(filepath)
                    stats['uploads_count'] += 1
        
        # Check results directory
        if os.path.exists(self.results_dir):
            for filename in os.listdir(self.results_dir):
                filepath = os.path.join(self.results_dir, filename)
                if os.path.isfile(filepath):
                    stats['results_size'] += os.path.getsize(filepath)
                    stats['results_count'] += 1
        
        # Check database size
        if os.path.exists(self.db_path):
            stats['database_size'] = os.path.getsize(self.db_path)
        
        return stats
    
    def format_size(self, size_bytes):
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

def main():
    parser = argparse.ArgumentParser(description='NIST Application Cleanup Utility')
    parser.add_argument('--files', type=int, default=30, 
                       help='Remove files older than N days (default: 30)')
    parser.add_argument('--database', type=int, default=90,
                       help='Remove database entries older than N days (default: 90)')
    parser.add_argument('--stats', action='store_true',
                       help='Show storage statistics only')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned without actually doing it')
    
    args = parser.parse_args()
    
    cleanup = CleanupUtility()
    
    if args.stats:
        print("Storage Statistics:")
        print("=" * 50)
        stats = cleanup.get_storage_stats()
        print(f"Uploads: {stats['uploads_count']} files, {cleanup.format_size(stats['uploads_size'])}")
        print(f"Results: {stats['results_count']} files, {cleanup.format_size(stats['results_size'])}")
        print(f"Database: {cleanup.format_size(stats['database_size'])}")
        total_size = stats['uploads_size'] + stats['results_size'] + stats['database_size']
        print(f"Total: {cleanup.format_size(total_size)}")
        return
    
    if args.dry_run:
        print("DRY RUN - No files will be actually removed")
        print("=" * 50)
    
    print(f"Cleaning up files older than {args.files} days...")
    if not args.dry_run:
        files_removed = cleanup.cleanup_old_files(args.files)
        print(f"Removed {files_removed} old files")
    
    print(f"Cleaning up database entries older than {args.database} days...")
    if not args.dry_run:
        db_entries_removed = cleanup.cleanup_database(args.database)
        print(f"Removed {db_entries_removed} old database entries")
    
    print("\nCurrent storage statistics:")
    stats = cleanup.get_storage_stats()
    print(f"Uploads: {stats['uploads_count']} files, {cleanup.format_size(stats['uploads_size'])}")
    print(f"Results: {stats['results_count']} files, {cleanup.format_size(stats['results_size'])}")
    print(f"Database: {cleanup.format_size(stats['database_size'])}")

if __name__ == '__main__':
    main()
