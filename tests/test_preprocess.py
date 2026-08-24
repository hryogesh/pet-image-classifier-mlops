import os
from PIL import Image

from src.data.preprocess import split_and_process


def test_preprocess_creates_structure(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    cat_dir = raw / 'cats'
    dog_dir = raw / 'dogs'
    cat_dir.mkdir()
    dog_dir.mkdir()
    for i in range(5):
        Image.new('RGB', (300, 300), color=(i, 0, 0)).save(cat_dir / f'cat_{i}.jpg')
        Image.new('RGB', (300, 300), color=(0, i, 0)).save(dog_dir / f'dog_{i}.jpg')

    out = tmp_path / 'processed'
    split_and_process(str(raw), str(out), img_size=64)

    assert (out / 'train' / 'cats').exists()
    assert (out / 'train' / 'dogs').exists()
