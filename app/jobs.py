import uuid
import os
import threading
import time
from typing import Dict, Optional

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        with self.lock:
            self.jobs[job_id] = {
                "status": "queued",
                "progress": 0,
                "result_path": None,
                "error": None,
                "created_at": time.time()
            }
        return job_id

    def update_progress(self, job_id: str, progress: int):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["progress"] = progress
                self.jobs[job_id]["status"] = "processing"

    def set_complete(self, job_id: str, result_path: str):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["progress"] = 100
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["result_path"] = result_path

    def set_error(self, job_id: str, error_msg: str):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = error_msg

    def get_job(self, job_id: str) -> Optional[Dict]:
        with self.lock:
            return self.jobs.get(job_id)

    def cleanup_old_jobs(self, max_age=3600):
        # Ideally run this periodically
        pass

job_manager = JobManager()
