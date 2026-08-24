import argparse
import shutil
from pathlib import Path

try:
    import kagglehub
except ModuleNotFoundError:  # pragma: no cover - handled explicitly in the CLI
    kagglehub = None


DEFAULT_DATASET = 'bhavikjikadara/dog-and-cat-classification-dataset'


def download_dataset(dataset_name=DEFAULT_DATASET, target_dir='data/raw'):
    if kagglehub is None:
        raise ModuleNotFoundError(
            'kagglehub is required. Install it with: pip install kagglehub'
        )

    downloaded_path = Path(kagglehub.dataset_download(dataset_name))
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    if downloaded_path.exists() and downloaded_path.resolve() != target_path.resolve():
        for item in downloaded_path.iterdir():
            destination = target_path / item.name
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destination)

    return str(target_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download the Kaggle Cats & Dogs dataset into the project data folder.')
    parser.add_argument(
        '--dataset_name',
        default=DEFAULT_DATASET,
        help='Kaggle dataset slug in the format owner/dataset-name.',
    )
    parser.add_argument(
        '--target_dir',
        default='data/raw',
        help='Local folder to copy the downloaded files into.',
    )
    args = parser.parse_args()

    path = download_dataset(dataset_name=args.dataset_name, target_dir=args.target_dir)
    print(f'Dataset downloaded to: {path}')
