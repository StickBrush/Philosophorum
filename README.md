# Pylosophorum
Python Orchestrator for the Dámaso project (DSH)

This project contains a Python program that orchestrates different events of the Damaso Ubicom project for the subject Hardware System Description (DSH) using the MQTT protocol.

## Requirements

- Python 3.7+
- Pip for Python 3
- Mosquitto message protocol

## Installing Pylosophorum

1. Clone this Git repository.
2. Install packages in `requirements.txt` using Pip.

You can do it easily with these commands (under GNU/Linux):
```bash
git clone https://github.com/StickBrush/Pylosophorum.git
cd Pylosophorum
pip3 install -r requirements.txt
```

## Executing Pylosophorum

1. Run Mosquitto in the background.
2. Run `launch.py`

If you have Mosquitto running in the background already, you can simply do this:

```bash
python3 launch.py
```

## Options

To show the debug output, pass `--DEBUG` as an argument to `launch.py`.

## How to use

In a practical use case, Kodi should be modified to be executed at system startup (it is supported by Kodi in its configuration files) and so should Pylosophorum be. It is recommended to add a script that runs `launch.py` to a `crontab` file so that `cron` executes it on the background at system startup. It is also good practice to run it as `python3 launch.py --DEBUG > /path/to/logfile 2>&1`.
