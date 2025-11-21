import requests
import os

import time

def test_api():
    # The old /convert endpoint was removed/replaced by async flow in main.py?
    # Wait, I kept it in the file? Let me check main.py content.
    # Ah, I see in main.py I commented out "Keep the old endpoint... I'll remove it".
    # So /convert might be gone. Let's check main.py.
    # It seems I overwrote main.py and did NOT include /convert.
    # So I should update this test to use the new flow.

    base_url = "http://127.0.0.1:8000"
    pdf_path = os.path.join(os.path.dirname(__file__), 'test.pdf')

    try:
        # 1. Upload
        upload_url = f"{base_url}/api/upload"
        files = {'file': ('test.pdf', open(pdf_path, 'rb'), 'application/pdf')}
        print("Uploading...")
        response = requests.post(upload_url, files=files)

        if response.status_code != 200:
            print(f"Upload Failed: {response.status_code}")
            print(response.text)
            return

        job_id = response.json()['job_id']
        print(f"Job ID: {job_id}")

        # 2. Poll
        status_url = f"{base_url}/api/status/{job_id}"
        while True:
            res = requests.get(status_url)
            data = res.json()
            status = data['status']
            print(f"Status: {status} ({data['progress']}%)")

            if status == 'completed':
                break
            if status == 'failed':
                print(f"Job failed: {data.get('error')}")
                return
            time.sleep(1)

        # 3. Download
        download_url = f"{base_url}/api/download/{job_id}"
        print("Downloading...")
        res = requests.get(download_url)

        if res.status_code == 200:
            with open('output.epub', 'wb') as f:
                f.write(res.content)
            print("Success: output.epub created")
        else:
            print(f"Download Failed: {res.status_code}")


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
