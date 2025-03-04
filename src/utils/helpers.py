def format_text(text):
    return text.strip()

def handle_api_request(url, data=None, method='GET'):
    import requests
    if method == 'GET':
        response = requests.get(url)
    elif method == 'POST':
        response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

def extract_video_id(url):
    import re
    match = re.search(r'(?<=v=|/)([0-9A-Za-z_-]{11})', url)
    return match.group(0) if match else None

def summarize_text(text):
    from gensim.summarization import summarize
    return summarize(text) if len(text.split()) > 20 else text

def clean_summary(summary):
    return summary.replace('\n', ' ').strip()