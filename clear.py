import os
import shutil

if __name__ == '__main__':
    if os.path.isdir('images'):
        shutil.rmtree('images')
        print('remove images')
    if os.path.exists('crawled_dataset.json'):
        os.remove('crawled_dataset.json')
        print('remove crawled_dataset.json')