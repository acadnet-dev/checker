from abc import ABC, abstractmethod
from uuid import uuid4
from tempfile import SpooledTemporaryFile
from file_processor import SubmissionDirectory
import asyncio

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


class SimpleAcadnetIS(Submission):
    def __init__(self, submission_id):
        self.submission_id = submission_id
        self.submission_dir = SubmissionDirectory(submission_id)

    def get_submission_id(self):
        return self.submission_id
    
    def add_submission_file(self, filename, content):
        print("Adding file to SimpleAcadnetIS submission")
        print(filename)

        self.submission_dir.add_file(filename, content)

def get_new_submission(type: str) -> Submission:
    if type == "SimpleAcadnetIS":
        return SimpleAcadnetIS(uuid4())
    
    raise Exception("Invalid submission type")