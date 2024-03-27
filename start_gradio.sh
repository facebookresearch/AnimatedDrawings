# start_gradio.sh

#!/bin/bash

# check if gradio is installed
pip list | grep gradio &> /dev/null
if [ $? != 0 ]; then
    echo "Gradio not found. Installing Gradio..."
    pip install gradio
fi

# check if python3 is installed
command -v python3 >/dev/null 2>&1 || { 
    echo >&2 "Python3 required but it's not installed. Installing Python3..."; 
    brew install python3;
}

# navigate to the script's directory
cd "$(dirname "$0")"

# start the gradio script
python3 gradio_script.py