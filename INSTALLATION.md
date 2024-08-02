# Windows Installation
## Overview
- You need to install Python to be able to run the Python executable "sigexport.exe"
- The Python executable "sigexport.exe" is downloaded from the Python Package Index (an online repository).

## Steps
### 1. Install of Windows WSL2
- Go to the Start menu and search for "Turn Windows features on or off".
- Select "Windows Subsystem for Linux" and click OK.
- Open a PowerShell prompt and install WSL2 with:
```powershell
wsl --install
```

### 2. Install Python
- Go to the Start menu and open the Microsoft Store
- In the Microsoft Store, search for "Python"
- Click on "Python 3.12" (or later) and then "Get"
	
### 3. Install signal-export
- Open a PowerShell prompt
- Download the package from the online repository with:
```powershell
pip install --user signal-export
```

### 4. Run the executable to extract chat history
- Run the command below, the target directory will be automatically created:
```powershell
python -m sigexport C:\Temp\MySignalExport
```

- To see all options:
```powershell
python -m sigexport --help
```

## Troubleshooting
### WSL Issues
You might need to manually update WSL in some circumstances. If so, use the link below:
- [Install WSL 2 Kernel Update](https://learn.microsoft.com/en-us/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package)
