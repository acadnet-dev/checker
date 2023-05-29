from fastapi import FastAPI, UploadFile, File
import uvicorn
import time

from submission_types import get_new_submission

app = FastAPI()

@app.post("/submission/create/")
async def create_submission(type: str, bucket: str, file: UploadFile = File(...)):
    try:
        submission = get_new_submission(type)
        
        contents = file.file.read().decode("utf-8")

        submission.add_submission_file(file.filename, contents)

        return {"submission_id": submission.get_submission_id()}
    except Exception as e:
        # TODO: log error
        raise e
        return {"error": str(e)}


def run(port):
    uvicorn.run(app, host="0.0.0.0", port=port)