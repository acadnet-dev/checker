from abc import ABC, abstractmethod
from uuid import uuid4
from tempfile import SpooledTemporaryFile
from file_processor import SubmissionDirectory
import asyncio

from s3 import S3API

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


class SimpleAcadnetIS(Submission):
    def __init__(self, submission_id):
        self.submission_id = submission_id
        self.submission_dir = SubmissionDirectory(submission_id)

    def get_submission_id(self):
        return str(self.submission_id)
    
    def add_submission_file(self, filename, content):
        self.submission_dir.add_file(filename, content)

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


def get_new_submission(type: str) -> Submission:
    if type == "SimpleAcadnetIS":
        return SimpleAcadnetIS(uuid4())
    
    raise Exception("Invalid submission type")