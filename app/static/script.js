async function startConversion() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a PDF file first.");
        return;
    }

    document.getElementById('convertBtn').disabled = true;
    document.getElementById('progressSection').classList.remove('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        pollStatus(data.job_id);

    } catch (error) {
        showError(error.message);
    }
}

async function pollStatus(jobId) {
    const statusText = document.getElementById('statusText');
    const progressBar = document.getElementById('progressBar');

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${jobId}`);
            const data = await response.json();

            if (data.status === 'processing' || data.status === 'queued') {
                statusText.innerText = `Status: ${data.status} (${data.progress}%)`;
                progressBar.style.width = `${data.progress}%`;
            } else if (data.status === 'completed') {
                clearInterval(interval);
                progressBar.style.width = '100%';
                showResult(jobId);
            } else if (data.status === 'failed') {
                clearInterval(interval);
                showError(data.error);
            }
        } catch (e) {
            clearInterval(interval);
            showError("Connection error");
        }
    }, 1000);
}

function showResult(jobId) {
    document.getElementById('progressSection').classList.add('hidden');
    document.getElementById('resultSection').classList.remove('hidden');
    const link = document.getElementById('downloadLink');
    link.href = `/api/download/${jobId}`;
}

function showError(msg) {
    document.getElementById('progressSection').classList.add('hidden');
    document.getElementById('errorSection').classList.remove('hidden');
    document.getElementById('errorText').innerText = msg;
    document.getElementById('convertBtn').disabled = false;
}

function resetUI() {
    document.getElementById('fileInput').value = '';
    document.getElementById('convertBtn').disabled = false;
    document.getElementById('resultSection').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');
    document.getElementById('progressBar').style.width = '0%';
}
