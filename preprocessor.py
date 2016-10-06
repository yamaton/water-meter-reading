import cv2
import numpy as np
import matplotlib.pyplot as plt
import pathlib


class OCRError(Exception):
    pass


def get_contours(img):
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(img, 235, 250, apertureSize=3, L2gradient=True)
    # print('edges:', edges)
    images, contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # images, contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return filter_(contours)


def filter_(contours):
    contours_dict = dict()
    for cont in contours:
        x, y, w, h = cv2.boundingRect(cont)
        area = cv2.contourArea(cont)
        if 10 < area and 10 < w and h > 5:
            contours_dict[(x, y, w, h)] = cont
    return sorted(contours_dict.values(), key=cv2.boundingRect)


def to_contours_image(contours, ref_image):
    blank_background = np.zeros_like(ref_image)
    img_contours = cv2.drawContours(blank_background, contours, -1, (255, 255, 255), thickness=2)
    return img_contours


def is_overlapping_horizontally(box1, box2):
    x1, _, w1, _ = box1
    x2, _, _, _ = box2
    if x1 > x2:
        return is_overlapping_horizontally(box2, box1)
    return (x2 - x1) < w1


def merge(box1, box2):
    assert is_overlapping_horizontally(box1, box2)
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    x = min(x1, x2)
    w = max(x1 + w1, x2 + w2) - x
    y = min(y1, y2)
    h = max(y1 + h1, y2 + h2) - y
    return x, y, w, h


def get_windows(contours):
    """return List[Tuple[x: Int, y: Int, w: Int, h: Int]]"""
    boxes = []
    for cont in contours:
        box = cv2.boundingRect(cont)
        if not boxes:
            boxes.append(box)
        else:
            if is_overlapping_horizontally(boxes[-1], box):
                last_box = boxes.pop()
                merged_box = merge(box, last_box)
                boxes.append(merged_box)
            else:
                boxes.append(box)
    return boxes


def to_digit_images(img):
    contours = get_contours(img)
    image_contours = to_contours_image(contours, img)
    windows = get_windows(contours)
    if len(windows) != 7:
        raise OCRError
    xs = [image_contours[y:y+h, x:x+w] for (x, y, w, h) in windows]
    return xs


def file2files(fpath):
    img = cv2.imread(fpath.as_posix(), cv2.IMREAD_GRAYSCALE)
    print('img.shape', img.shape)
    rois = to_digit_images(img)
    for i, digit_img in enumerate(rois):
        outfilepath = fpath.with_name(fpath.stem + ('_%d' % i) + '.png')
        cv2.imwrite(outfilepath.as_posix(), digit_img)


def batch(data_dir='/Users/yamato/OneDrive/MyCode/WaterMeterReading/trainset_extra'):
    p = pathlib.Path(data_dir)
    paths = p.glob('*.jpg')
    for fpath in paths:
        print('  ...processing', fpath.name)
        try:
            file2files(fpath)
        except OCRError:
            print('     [OCR ERROR]', fpath)
            continue


if __name__ == '__main__':
    batch()
