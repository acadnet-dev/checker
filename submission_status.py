import json
import time

class SubmissionStatus:
    def __init__(self, submission):
        self.test_results = []
        self.status_history = []
        self.submission = submission
        self.build_status = "not built yet"

        self.set_status("created")

    def set_status(self, status):
        self.status = status
        self.status_history.append({ "status": status, "timestamp": time.time()})

    def set_build_status(self, status):
        self.build_status = status

    def add_test_result(self, test_name, passed, status, diff_results, execution_result):
        self.test_results.append({ "test_name": test_name, "passed": passed, "status": status, "diff_results": diff_results, "exec_result": execution_result })

    def json(self):
        return {
            "submission_id": self.submission.get_submission_id(),
            "status": self.status,
            "build_status": self.build_status,
            "test_results": self.test_results,
            "status_history": self.status_history
        }