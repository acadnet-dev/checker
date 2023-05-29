from fastapi import FastAPI, UploadFile, File
import uvicorn
import time

from submission_types import get_new_submission
from s3 import S3API
from config import Config
from runner import SubmissionRunner

config = Config("config.json")
app = FastAPI()
s3api = S3API(config)
runner = SubmissionRunner()

@app.post("/submission/create/")
async def create_submission(type: str, bucket: str, file: UploadFile = File(...)):
    try:
        # create submission
        submission = get_new_submission(type)
        
        # add uploaded file to submission
        submission.add_submission_file(file.filename, file.file.read().decode("utf-8"))

        # download tests from s3 bucket
        submission.download_tests(bucket, s3api)

        # init sandbox
        # TODO: change this to launch new sandbox instance for each submission
        submission.init_sandbox(config.sandbox_endpoint)

        # run submission
        runner.run_submission(submission)

        return {"submission_id": submission.get_submission_id()}
    except Exception as e:
        # TODO: log error
        raise e
        return {"error": str(e)}

@app.get("/submission/status/")
def get_submission_status(submission_id: str):
    return {"status": runner.get_submission_status(submission_id)}


def run():
    uvicorn.run(app, host="0.0.0.0", port=config.port)