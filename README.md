# signal-export
[![cicd](https://github.com/carderne/signal-export/actions/workflows/cicd.yml/badge.svg)](https://github.com/carderne/signal-export/actions/workflows/cicd.yml)
[![PyPI version](https://badge.fury.io/py/signal-export.svg)](https://pypi.org/project/signal-export/)

**⚠️ WARNING: Because the latest versions of Signal Desktop protect the database encryption key, this tool currently only works on macOS and Linux.
Solutions for Windows will hopefully come soon from the community.
Discussion happening in [this thread](https://github.com/carderne/signal-export/issues/133).**

Export chats from the [Signal](https://www.signal.org/) [Desktop app](https://www.signal.org/download/) to Markdown and HTML files with attachments. Each chat is exported as an individual .md/.html file and the attachments for each are stored in a separate folder. Attachments are linked from the Markdown files and displayed in the HTML (pictures, videos, voice notes).

Currently this seems to be the only way to get chat history out of Signal!

Adapted from [mattsta/signal-backup](https://github.com/mattsta/signal-backup), which I suspect will be hard to get working now.

## Example
An export for a group conversation looks as follows:
```markdown
[2019-05-29, 15:04] Me: How is everyone?
[2019-05-29, 15:10] Aya: We're great!
[2019-05-29, 15:20] Jim: I'm not.
```

Images are attached inline with `![name](path)` while other attachments (voice notes, videos, documents) are included as links like `[name](path)` so a click will take you to the file.

This is converted to HTML at the end so it can be opened with any web browser. The stylesheet `.css` is still very basic but I'll get to it sooner or later.

## 🪟 Installation: Windows
If you need step-by-step instructions on things like enabling WSL2, please see the dedicated [Windows Installation](./INSTALLATION.md) instructions.

In order to use this tool, you'll need to install WSL2, Docker and Python.
The steps to do this are below.
(**NB:** Improvements to these instructions are welcome.)

1. Enable Windows WSL2 feature
2. Install [Docker Desktop](https://docs.docker.com/get-docker/) with the WSL2 backend
3. Install Python 3.12 via Windows Store
4. In a PowerShell terminal, run
```bash
pip install signal-export
```
5. Run the script like this (you can enter any directory, it will be created)
```bash
sigexport C:\Temp\SignalExport
```
Run it without any arguments to get instructions about other options
```bash
sigexport
```

**NB** You may get an error like `term 'sigexport' is not recognized`, in which case you can use the following:
```bash
python -m sigexport.main ~/signal-chats
```

## 🐧 Installation: Linux
1. [Install Docker](https://docs.docker.com/get-docker/) (including following the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) for managing Docker as a non-root user).  
2. Make sure you have Python installed.

3. Install this package:
```bash
pip install signal-export
```

4. Then run the script! It will do some Docker stuff under the hood to get your data out of the encrypted database.
```bash
sigexport ~/signal-chats
# output will be saved to the supplied directory
```

### Linux without Docker
1. Install the required libraries.
```bash
sudo apt install libsqlite3-dev tclsh libssl-dev
```

2. Then clone [sqlcipher](https://github.com/sqlcipher/sqlcipher) and install it:
```bash
git clone https://github.com/sqlcipher/sqlcipher.git
cd sqlcipher
./configure --enable-tempstore=yes CFLAGS="-DSQLITE_HAS_CODEC" LDFLAGS="-lcrypto -lsqlite3"
make && sudo make install
```

3. Then you can install and run signal-export without Docker:
```bash
pip install 'signal-export[sql]'
sigexport --no-use-docker ...
```

## 🍏 Installation: macOS
To use it with Docker, just follow the standard Linux instructions above.

### macOS without Docker
1. Install [Homebrew](https://brew.sh).
2. Run `brew install openssl sqlcipher`
3. Export some needed env vars:
```bash
export C_INCLUDE_PATH="$(brew --prefix sqlcipher)/include"
export LIBRARY_PATH="$(brew --prefix sqlcipher)/lib"
```

4. Then you can install and run signal-export without Docker:
```bash
pip install 'signal-export[sql]'
sigexport --no-use-docker ...
```

## 🚀 Usage
Please fully exit your Signal app before proceeding, otherwise you will likely encounter an `I/O disk` error, due to the message database being made read-only, as it was being accessed by the app.

See the full help info:
```bash
sigexport --help
```

Disable pagination on HTML:
```bash
sigexport --paginate=0 ~/signal-chats
```

List available chats and exit:
```bash
sigexport --list-chats
```

Export only the selected chats:
```bash
sigexport --chats=Jim,Aya ~/signal-chats
```

You can add `--source /path/to/source/dir/` if the script doesn't manage to find the Signal config location.
Default locations per OS are below.
The directory should contain a folder called `sql` with `db.sqlite` inside it.
- Linux: `~/.config/Signal/`
- macOS: `~/Library/Application Support/Signal/`
- Windows: `~/AppData/Roaming/Signal/`

You can also use `--old /previously/exported/dir/` to merge the new export with a previous one.
_Nothing will be overwritten!_
It will put the combined results in whatever output directory you specified and leave your previos export untouched.
Exercise is left to the reader to verify that all went well before deleting the previous one.

## 🗻 No-Python install
I don't recommend this, and you will have issues with file-ownership and other stuff.
You can also run the Docker image directly, it just requires copy-pasting a much-longer command and being careful with volume mounts.

First set the appropriate environment variables for your OS:
```bash
# Only enter one of these!
SIGNAL_INPUT="$HOME/.config/Signal"                             # Linux
SIGNAL_INPUT="$HOME/snap/signal-desktop/current/.config/Signal" # Snap
SIGNAL_INPUT="$HOME/Library/Application Support/Signal"         # macOS
SIGNAL_INPUT="$HOME/AppData/Roaming/Signal"                     # Powershell

# And your output location (must be an absolute path)
SIGNAL_OUTPUT="$HOME/Downloads/signal-output"
```

Then run the below command, which pulls in the environment variables you set above.
```bash
# Note that the --overwrite flag is necessary when running like this
# careful where you point it!
docker run --rm \
  --net none \
  -v "$SIGNAL_INPUT:/Signal:ro" \
  -v "$SIGNAL_OUTPUT:/output" \
    carderne/sigexport:latest \
    --overwrite /output \         # this line is obligatory!
    --chats Jim                   # this line isn't
```

Then you should be able to use the [Usage instructions](#usage) as above.

## Development
```bash
git clone https://github.com/carderne/signal-export.git
cd signal-export
rye sync --no-lock
```

Various dev commands:
```bash
rye fmt         # format
rye lint        # lint
rye run check   # typecheck
rye run test    # test
rye run sig     # run signal-export
```

## Similar things
- [signal-backup-decode](https://github.com/pajowu/signal-backup-decode) might be easier if you use Android!
- [signal2html](https://github.com/GjjvdBurg/signal2html) also Android only
