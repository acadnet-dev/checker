from submission_types import Submission
import time
from threading import Thread, Lock

statuses = {}
lock = Lock()

def update_status(submission_id: str, status: str):
    global statuses
    with lock:
        statuses[submission_id] = status
    
def get_status(submission_id: str):
    global statuses
    with lock:
        if submission_id not in statuses:
            return "not_found"
        return statuses[submission_id]

def _run_submission_async(submission: Submission):
    update_status(submission.get_submission_id(), "finished")


class SubmissionRunner:
    def __init__(self):
        pass

    def run_submission(self, submission: Submission):
        update_status(submission.get_submission_id(), "started")
        Thread(target=_run_submission_async, args=(submission, )).start()

    def get_submission_status(self, submission_id: str):
        return get_status(submission_id)
        