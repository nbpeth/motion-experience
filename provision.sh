echo "Provisioning the environment"

PYTHON="${PYTHON:-/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14}"
"$PYTHON" -m venv ./venv

echo "Activating the virtual environment"
source ./venv/bin/activate

echo "Installing dependencies"
pip3 install -r requirements.txt