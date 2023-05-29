from fastapi import FastAPI, UploadFile, File
import uvicorn
import tempfile
import os
from pydantic import BaseModel
import subprocess
import json
import utils

tmpdir = tempfile.mkdtemp()

app = FastAPI()

@app.post("/upload_file")
def hello(file: UploadFile = File(...)):
    try:
        # save file to tmpdir
        with open(os.path.join(tmpdir, file.filename), "wb") as f:
            f.write(file.file.read())

        # list files in tmpdir
        print("files in tmpdir:")
        for f in os.listdir(tmpdir):
            print(f)

        return "ok"
    except Exception as e:
        return {"error": str(e)}

class Cmd(BaseModel):
    cmd: str

@app.post("/run")
def run_command(cmd: Cmd):
    try:
        # run command in tmpdir and return output
        print(cmd.cmd)

        cmd = subprocess.run(cmd.cmd, shell=True, cwd=tmpdir, capture_output=True)

        return {
            "stdout": cmd.stdout,
            "stderr": cmd.stderr,
        }
    except subprocess.CalledProcessError as e:
        return {"error": utils.subprocess_error_to_json(e)}

def run():
    uvicorn.run(app, host="0.0.0.0", port=2999)