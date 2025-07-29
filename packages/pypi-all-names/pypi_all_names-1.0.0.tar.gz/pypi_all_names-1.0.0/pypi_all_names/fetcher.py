import requests
from bs4 import BeautifulSoup

def fetch_all_package_names():
    """
    https://pypi.org/simple/ 페이지를 스크래핑하여 등록된 모든 패키지 이름을 리스트로 반환한다.
    """
    url = 'https://pypi.org/simple/'
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    # <a> 태그의 텍스트가 패키지 이름
    package_names = [a.get_text(strip=True) for a in soup.find_all('a')]
    return package_names

def save_as_json(package_list, output_path):
    """
    package_list(리스트)를 JSON 형태로 output_path에 저장한다.
    """
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(package_list, f, ensure_ascii=False, indent=2)

def save_as_txt(package_list, output_path):
    """
    package_list(리스트)를 한 줄에 하나씩 출력하는 텍스트 파일로 저장한다.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for name in package_list:
            f.write(name + '\n')
