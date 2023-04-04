# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import base64
from flask import Flask, render_template, request
import json
import os
import sys
import yaml

global cfg_path
global char_folder
app = Flask(__name__, template_folder=os.path.abspath("./fixer_app/"))


def load_cfg(path):
    with open(path, "r") as f:
        cfg_text = f.read()
        cfg_yaml = yaml.load(cfg_text, Loader=yaml.Loader)
    return cfg_yaml


def write_cfg(path, cfg):
    with open(path, "w") as f:
        yaml.dump(cfg, f)


@app.route("/")
def index():
    global cfg_path
    global char_folder
    cfg = load_cfg(cfg_path)

    base64_img = {"data": ""}
    with open(os.path.join(char_folder, "texture.png"), "rb") as image_file:
        base64_img['data'] = str(base64.b64encode(image_file.read()), "utf-8")

    return render_template('dist/index.html', cfg=cfg, image=base64_img)


@app.route("/annotations/submit", methods=["POST"])
def post_cfg():
    output, message = process(request)
    if output:
        print(output)
    return render_template('submit.html', code=output, message=message)


def process(request):
    try:
        formdata = request.form.get('data')
    except Exception as e:
        return None, f"Error parsing data from request. No JSON data was found: {e}"

    try:
        jsondata = json.loads(formdata)
    except Exception as e:
        return None, f"Error parsing submission data into JSON. Invalid format?: {e}"

    # convert joint locations from floats to ints
    for joint in jsondata['skeleton']:
        joint['loc'][0] = round(joint['loc'][0])
        joint['loc'][1] = round(joint['loc'][1])

    try:
        new_cfg = yaml.dump(jsondata)
    except Exception as e:
        return None, f"Error converting submission to YAML data. Invalid format?: {e}"

    try:
        write_cfg(os.path.join(cfg_path), jsondata)
    except Exception as e:
        return None, f"Error saving down file to `{cfg_path}: {e}`"

    return new_cfg, f"Successfully saved config to `{cfg_path}`"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('char_folder', type=str, help="the location of the character bundle")
    parser.add_argument('--port', type=int, default=5050, help="the port the tool launches on")
    args = parser.parse_args()

    char_folder = args.char_folder
    cfg_path = os.path.join(char_folder, "char_cfg.yaml")

    if not os.path.isfile(cfg_path):
        print(f"[Error] File not found. Expected config file at: {cfg_path}")
        sys.exit(1)
    app.run(port=args.port, debug=False)
