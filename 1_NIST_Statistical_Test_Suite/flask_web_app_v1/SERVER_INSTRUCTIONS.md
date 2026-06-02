# NIST 800-22 Server Control Instructions

## 📁 Server Control Files

### 🚀 **start_server.bat**
- **Purpose**: Starts the NIST 800-22 Flask server
- **Usage**: Double-click to run
- **Features**:
  - Checks Python installation
  - Installs dependencies automatically
  - Shows server URLs (local and network)
  - Colored console output
  - Error handling

### 🛑 **stop_server.bat**
- **Purpose**: Stops the running NIST server
- **Usage**: Double-click to run
- **Features**:
  - Safely terminates Flask processes
  - Kills Python processes running the server
  - Confirmation message

### 🔄 **restart_server.bat**
- **Purpose**: Restarts the server (stop + start)
- **Usage**: Double-click to run
- **Features**:
  - Combines stop and start operations
  - Useful for applying changes

### 📦 **install_dependencies.bat**
- **Purpose**: Installs required Python packages
- **Usage**: Run this first if you have issues
- **Features**:
  - Checks Python and pip installation
  - Installs Flask, NumPy, SciPy
  - Error handling and validation

### 📊 **check_server_status.bat**
- **Purpose**: Checks if server is running
- **Usage**: Double-click to check status
- **Features**:
  - Lists running Python processes
  - Tests connection to localhost:5000
  - Network connectivity check

## 🔧 Setup Instructions

### 1. **First Time Setup**
\`\`\`
1. Run install_dependencies.bat
2. Wait for installation to complete
3. Run start_server.bat
\`\`\`

### 2. **Daily Usage**
\`\`\`
- Start: Double-click start_server.bat
- Stop: Double-click stop_server.bat
- Check: Double-click check_server_status.bat
\`\`\`

### 3. **Troubleshooting**
\`\`\`
- If server won't start: Run install_dependencies.bat
- If server won't stop: Run stop_server.bat twice
- If unsure about status: Run check_server_status.bat
\`\`\`

## 🌐 Access URLs

- **Local Access**: http://localhost:5000
- **Network Access**: http://[YOUR_IP]:5000
- **Find Your IP**: Run `ipconfig` in Command Prompt

## ⚠️ Important Notes

1. **Keep files together**: All .bat files should be in the same folder as app.py
2. **Python required**: Install Python 3.7+ from python.org
3. **Firewall**: Windows may ask for firewall permission - click "Allow"
4. **Port 5000**: Make sure port 5000 is not used by other applications

## 🚨 Troubleshooting

### Server Won't Start
- Run install_dependencies.bat
- Check if Python is installed: `python --version`
- Check if port 5000 is free: `netstat -an | find "5000"`

### Can't Access from Network
- Check Windows Firewall settings
- Ensure you're using the correct IP address
- Try accessing from localhost first

### Server Won't Stop
- Run stop_server.bat
- If still running, restart your computer
- Check Task Manager for python.exe processes
