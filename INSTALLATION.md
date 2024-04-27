# Installation
## Windows
### Overview
- You need to install Python to be able to run the Python executable "sigexport.exe"
- The Python executable "sigexport.exe" is downloaded from the Python Package Index (an online repository). The Python executable requires Docker Desktop to function, and it will automatically download a Docker image that is used in the process of extracting the Signal chat data.
- Docker Desktop needs the Windows feature WSL2 (Windows Subsystem for Linux) to work.

### Steps
#### 1. Installation of Windows WSL2
- Go to the Start menu and search for "Turn Windows features on or off".
- Select "Windows Subsystem for Linux" and click OK.
- Open a PowerShell prompt and install WSL2 with:
```powershell
wsl --install
```

#### 2. Install Docker Desktop
- Download [Docker Desktop from here](https://docs.docker.com/get-docker/)
- Run the Docker setup file
- Select the option "Use WSL 2 instead of Hyper-V (recommended)"

#### 3. Install Python
- Go to the Start menu and open the Microsoft Store
- In the Microsoft Store, search for "Python"
- Click on "Python 3.12" (or later) and then "Get"
	
#### 4. Install signal-export
- Open a PowerShell prompt
- Download the package from the online repository with:
```powershell
pip install --user signal-export
```

#### 5. Run the executable to extract chat history
- Run the command below, the target directory will be automatically created:
```powershell
python -m sigexport C:\Temp\MySignalExport
```

- To see all options:
```powershell
python -m sigexport --help
```

### Troubleshooting
#### WSL Issues
You might need to manually update WSL in some circumstances. If so, use the link below:
- [Install WSL 2 Kernel Update](https://learn.microsoft.com/en-us/windows/wsl/install-manual#step-4---download-the-linux-kernel-update-package)

### Running sigexport
**Note:** Any improvements to these instructions would be great.

If the approach above doesn't work, you might need to try locating the `sigexport` script manually.

You're looking for a path something like the one below, you might need to go hunting for it under `\Local\Packages`.
Once you've found it, open PowerShell and `cd` to the directory:
```powershell
cd C:\Users\<MyUserName>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.XX_<random-letters>\LocalCache\local-packages\Python3XX\Scripts\
```

Then you can run the script like this:
```powershell
.\sigexport.exe C:\Temp\MySignalExport
```
