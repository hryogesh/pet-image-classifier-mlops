import argparse
import json
from pathlib import Path

import requests


def evaluate(base_url, data_dir):
    total = correct = 0
    for label_name, expected in (('cats', 0), ('dogs', 1)):
        for image_path in sorted((Path(data_dir) / label_name).glob('*')):
            if image_path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
                continue
            with image_path.open('rb') as image_file:
                response = requests.post(
                    f'{base_url}/predict',
                    files={'file': (image_path.name, image_file, 'image/jpeg')},
                    timeout=30,
                )
            response.raise_for_status()
            prediction = response.json()
            total += 1
            correct += int(prediction['label'] == expected)
    if total == 0:
        raise RuntimeError(f'No labeled images found in {data_dir}')
    result = {'samples': total, 'correct': correct, 'accuracy': correct / total}
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://localhost:8000')
    parser.add_argument('--data-dir', default='data/processed/test')
    args = parser.parse_args()
    result = evaluate(args.base_url, args.data_dir)
    raise SystemExit(0 if result['samples'] else 1)
