import tempfile
import os

class SubmissionDirectory:
    def __init__(self, submission_id):
        self.tmpdir = tempfile.mkdtemp()

        # create a directory with the submission id
        self.submission_dir = os.path.join(self.tmpdir, str(submission_id))
        os.mkdir(self.submission_dir)

        print("Submission files path: " + self.submission_dir)

        self.files = []

    def __enter__(self):
        return self.submission_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        for filename in self.files:
            os.remove(os.path.join(self.submission_dir, filename))
        os.rmdir(self.submission_dir)
        os.rmdir(self.tmpdir)

    def add_file(self, filename, content):
        self.files.append(filename)
        with open(os.path.join(self.submission_dir, filename), "w") as f:
            f.write(content)

    def get_file(self, filename):
        with open(os.path.join(self.submission_dir, filename), "r") as f:
            return f.read()

