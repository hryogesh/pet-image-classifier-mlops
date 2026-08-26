import os
import argparse
import random
from PIL import Image


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)


def gather_images(input_dir):
    cats = []
    dogs = []
    for root, dirs, files in os.walk(input_dir):
        lname = os.path.basename(root).lower()
        if 'cat' in lname:
            cats += [os.path.join(root, f) for f in files]
        elif 'dog' in lname:
            dogs += [os.path.join(root, f) for f in files]
    if not cats and not dogs:
        for f in os.listdir(input_dir):
            lf = f.lower()
            if 'cat' in lf:
                cats.append(os.path.join(input_dir, f))
            elif 'dog' in lf:
                dogs.append(os.path.join(input_dir, f))
    return cats, dogs


def resize_and_copy(files, dst_dir, img_size=224):
    ensure_dir(dst_dir)
    for i, p in enumerate(files):
        try:
            img = Image.open(p).convert('RGB')
            img = img.resize((img_size, img_size))
            img.save(os.path.join(dst_dir, f'{i}.jpg'))
        except Exception:
            continue


def split_and_process(input_dir, output_dir, img_size=224, seed=42):
    cats, dogs = gather_images(input_dir)
    random.seed(seed)
    random.shuffle(cats)
    random.shuffle(dogs)

    def split_list(lst):
        n = len(lst)
        n_train = int(n * 0.8)
        n_val = int(n * 0.1)
        return lst[:n_train], lst[n_train:n_train + n_val], lst[n_train + n_val:]

    cats_train, cats_val, cats_test = split_list(cats)
    dogs_train, dogs_val, dogs_test = split_list(dogs)

    for split in ['train', 'val', 'test']:
        ensure_dir(os.path.join(output_dir, split, 'cats'))
        ensure_dir(os.path.join(output_dir, split, 'dogs'))

    resize_and_copy(cats_train, os.path.join(output_dir, 'train', 'cats'), img_size)
    resize_and_copy(cats_val, os.path.join(output_dir, 'val', 'cats'), img_size)
    resize_and_copy(cats_test, os.path.join(output_dir, 'test', 'cats'), img_size)

    resize_and_copy(dogs_train, os.path.join(output_dir, 'train', 'dogs'), img_size)
    resize_and_copy(dogs_val, os.path.join(output_dir, 'val', 'dogs'), img_size)
    resize_and_copy(dogs_test, os.path.join(output_dir, 'test', 'dogs'), img_size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--img_size', type=int, default=224)
    args = parser.parse_args()
    split_and_process(args.input_dir, args.output_dir, img_size=args.img_size)
