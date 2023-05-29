from abc import ABC, abstractmethod
from uuid import uuid4
from tempfile import SpooledTemporaryFile
from file_processor import SubmissionDirectory
import asyncio

from s3 import S3API
from sandbox_adapter import SandboxAdapter

class Submission(ABC):
    @abstractmethod
    def __init__(self, submission_id):
        pass

    @abstractmethod
    def get_submission_id(self):
        pass
    
    @abstractmethod
    def add_submission_file(self, filename, content):
        pass

    @abstractmethod
    def download_tests(self, bucket, s3api: S3API):
        pass

    @abstractmethod
    def init_sandbox(self, endpoint):
        pass

    @abstractmethod
    def run_tests(self):
        pass


class SimpleAcadnetIS(Submission):
    def __init__(self, submission_id):
        self.submission_id = submission_id
        self.submission_dir = SubmissionDirectory(submission_id)
        self.submission_filename = None
        self.tests = []

    def get_submission_id(self):
        return str(self.submission_id)
    
    def add_submission_file(self, filename, content):
        if self.submission_filename is not None:
            raise Exception("[SimpleAcadnetIS] - Submission file already exists")
        self.submission_dir.add_file(filename, content)
        self.submission_filename = filename

    def download_tests(self, bucket, s3api: S3API):
        files_in_bucket = s3api.get_files_in_bucket(bucket)

        # remove all files that do not end with .in or .ref
        files_in_bucket = [filename for filename in files_in_bucket if filename.endswith(".in") or filename.endswith(".ref")]

        # count the number of files that end with .in
        num_in_files = len([filename for filename in files_in_bucket if filename.endswith(".in")])

        # count the number of files that end with .ref
        num_ref_files = len([filename for filename in files_in_bucket if filename.endswith(".ref")])

        # check if the number of .in files is equal to the number of .ref files
        if num_in_files != num_ref_files:
            raise Exception("[SimpleAcadnetIS] - Number of .in files is not equal to the number of .ref files")

        for filename in files_in_bucket:
            self.submission_dir.add_file(filename, s3api.download_file(bucket, filename).decode("utf-8"))
        
        self.tests = files_in_bucket

    def init_sandbox(self, endpoint):
        self.sandbox = SandboxAdapter(endpoint)

    def run_tests(self):
        # upload submission file
        self.sandbox.upload_file(self.submission_dir.submission_dir + "/" + self.submission_filename)

        # compile submission
        res = self.sandbox.run_command(f"g++ {self.submission_filename} -o main")
        if res["returncode"] != 0:
            raise Exception("[SimpleAcadnetIS] - Compilation error")

        # upload tests
        in_files = [filename for filename in self.tests if filename.endswith(".in")]

        for in_file in in_files:
            self.sandbox.upload_file(self.submission_dir.submission_dir + "/" + in_file)

            # run test
            res = self.sandbox.run_command(f"./main < {in_file}")
            print(res)



def get_new_submission(type: str) -> Submission:
    if type == "SimpleAcadnetIS":
        return SimpleAcadnetIS(uuid4())
    
    raise Exception("Invalid submission type")