import argparse
import sys
from .fetcher import fetch_all_package_names, save_as_json, save_as_txt

def main():
    parser = argparse.ArgumentParser(
        prog='pypi-all-names',
        description='PyPI에 등록된 모든 패키지 이름을 가져와 JSON 또는 TXT 파일로 저장하거나, 표준 출력으로 확인한다.'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'txt'],
        default=None,
        help='출력 형식 (json 또는 txt). 지정하지 않으면 패키지 이름을 표준 출력으로 한 줄씩 찍는다.'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='저장할 파일 경로. 형식을 지정하지 않으면 무시된다.'
    )

    args = parser.parse_args()

    try:
        names = fetch_all_package_names()
    except Exception as e:
        print(f"패키지 이름을 가져오는 중 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)

    # 출력을 파일에 저장할지, 아니면 표준 출력할지 결정
    if args.format:
        if not args.output:
            print("형식을 지정했으면 출력 파일 경로를 -o/--output 으로 꼭 지정해야 합니다.", file=sys.stderr)
            sys.exit(1)

        if args.format == 'json':
            save_as_json(names, args.output)
            print(f"모든 패키지 이름을 JSON으로 '{args.output}' 에 저장했습니다.")
        elif args.format == 'txt':
            save_as_txt(names, args.output)
            print(f"모든 패키지 이름을 TXT로 '{args.output}' 에 저장했습니다.")
    else:
        # 형식을 지정하지 않으면 한 줄씩 표준 출력
        for pkg in names:
            print(pkg)
