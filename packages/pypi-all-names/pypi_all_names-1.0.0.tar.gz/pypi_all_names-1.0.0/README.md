# pypi_all_names

PyPI에 등록된 모든 패키지 이름을 가져와 파이썬 리스트로 반환하고, 필요시 JSON 또는 TXT 파일로 저장할 수 있는 라이브러리 입니다.

## 설치

### pip로 설치(권장)
```bash
pip install pypi_all_names
```

### git clone하여 설치
```bash
pip install git+https://github.com/gaon12/pypi_all_names
```

## 사용 예시

### 1) 파이썬 코드에서 함수 호출

```python
from pypi_all_names.fetcher import fetch_all_package_names, save_as_json, save_as_txt

# 모든 패키지 이름을 리스트로 가져옴
names = fetch_all_package_names()

# JSON 파일로 저장
save_as_json(names, 'all_packages.json')

# TXT 파일로 저장
save_as_txt(names, 'all_packages.txt')
```

### 2) 커맨드라인에서 사용

- 표준 출력(한 줄씩 패키지 이름 출력):

  ```bash
  pypi-all-names
  ```

- JSON으로 저장:

  ```bash
  pypi-all-names -f json -o all_packages.json
  ```

- TXT로 저장:

  ```bash
  pypi-all-names -f txt -o all_packages.txt
  ```
