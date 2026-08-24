# Dataset download and placement

This project expects the Kaggle Cats & Dogs dataset to be downloaded and placed under
`data/raw/` in one of the following layouts:

- Preferred (already categorized):

```
data/raw/cats/*.jpg
data/raw/dogs/*.jpg
```

- Or: flat folder of images with filenames containing `cat` or `dog`.

To download from Kaggle CLI (you need to configure `kaggle` credentials):

```
kaggle datasets download -d bhavikjikadara/dog-and-cat-classification-dataset
unzip dog-and-cat-classification-dataset.zip -d data/raw
```
