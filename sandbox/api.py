from fastapi import FastAPI, UploadFile, File
import uvicorn
import tempfile
import os

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

def run():
    uvicorn.run(app, host="0.0.0.0", port=2999)