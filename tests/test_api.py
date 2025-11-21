import requests
import os

def test_api():
    url = "http://127.0.0.1:8000/convert"
    # Look for test.pdf in the same directory
    pdf_path = os.path.join(os.path.dirname(__file__), 'test.pdf')
    files = {'file': ('test.pdf', open(pdf_path, 'rb'), 'application/pdf')}

    try:
        response = requests.post(url, files=files)

        if response.status_code == 200:
            with open('output.epub', 'wb') as f:
                f.write(response.content)
            print("Success: output.epub created")
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
