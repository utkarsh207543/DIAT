import os
import uuid
import tempfile
import hashlib
from werkzeug.utils import secure_filename
from Tools import Tools

class LargeFileHandler:
    def __init__(self):
        self.chunk_size = 50 * 1024 * 1024  # 50MB chunks
        self.max_file_size = 100 * 1024 * 1024 * 1024  # 100GB
        self.upload_dir = 'uploads'
        self.temp_dir = 'temp'
        
        # Create directories if they don't exist
        for directory in [self.upload_dir, self.temp_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def generate_session_id(self):
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    def process_large_file_upload(self, file, file_type, session_id, db_manager):
        """Process large file upload with chunking"""
        try:
            original_filename = secure_filename(file.filename)
            file_size = 0
            
            # Create temporary file for processing
            temp_file_path = os.path.join(self.temp_dir, f"{session_id}_{original_filename}")
            
            # Save uploaded file
            file.save(temp_file_path)
            file_size = os.path.getsize(temp_file_path)
            
            if file_size > self.max_file_size:
                os.remove(temp_file_path)
                return {
                    'success': False,
                    'error': f'File size ({file_size:,} bytes) exceeds maximum allowed size ({self.max_file_size:,} bytes)'
                }
            
            # Process file based on type
            if file_type == 'binary':
                binary_data = self._process_binary_file(temp_file_path)
            else:
                binary_data = self._process_text_file(temp_file_path)
            
            # Limit binary data for processing (1M bits max for web interface)
            if len(binary_data) > 1000000:
                binary_data = binary_data[:1000000]
            
            # Clean up temporary file
            os.remove(temp_file_path)
            
            return {
                'success': True,
                'binary_data': binary_data,
                'original_filename': original_filename,
                'file_size': file_size
            }
            
        except Exception as e:
            # Clean up on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return {
                'success': False,
                'error': f'File processing error: {str(e)}'
            }
    
    def _process_binary_file(self, file_path):
        """Process binary file and extract binary data"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().strip()
        
        # Remove whitespace and validate
        binary_data = ''.join(content.split())
        
        if not all(bit in '01' for bit in binary_data):
            raise ValueError('Binary file must contain only 0s and 1s')
        
        return binary_data
    
    def _process_text_file(self, file_path):
        """Process text file and convert to binary"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Convert text to binary using Tools
        binary_data = Tools.string_to_binary(content)
        return binary_data
    
    def cleanup_old_files(self, days_old=7):
        """Clean up old temporary and upload files"""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        for directory in [self.upload_dir, self.temp_dir]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_time = os.path.getmtime(file_path)
                        if file_time < cutoff_time:
                            try:
                                os.remove(file_path)
                                print(f"🗑️ Cleaned up old file: {filename}")
                            except Exception as e:
                                print(f"❌ Error cleaning up {filename}: {str(e)}")
