from pathlib import Path
from unittest.mock import Mock, patch


def test_download_dataset_copies_kagglehub_contents(tmp_path):
    dataset_root = tmp_path / 'downloaded_dataset'
    (dataset_root / 'cats').mkdir(parents=True)
    (dataset_root / 'cats' / 'cat_1.jpg').write_bytes(b'img')

    target_dir = tmp_path / 'raw'

    with patch('src.data.download_dataset.kagglehub') as mock_kagglehub:
        mock_kagglehub.dataset_download.return_value = str(dataset_root)

        from src.data.download_dataset import download_dataset

        result = download_dataset(
            dataset_name='bhavikjikadara/dog-and-cat-classification-dataset',
            target_dir=str(target_dir),
        )

    assert result == str(target_dir)
    assert (target_dir / 'cats' / 'cat_1.jpg').exists()
