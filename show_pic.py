import matplotlib.pyplot as plt
import cv2
import numpy as np


def show_colorful_img(image, band_index):
    true_color_image = image[:, :, band_index].astype(np.float32)
    true_color_image = linear_stretch(true_color_image)
    plt.cla()
    plt.imshow(true_color_image)
    plt.axis('off')
    plt.figure(dpi=300)
    plt.show()


def show_single_band(image):
    image = gray_process(image)
    plt.cla()
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.figure(dpi=300)
    plt.show()


def linear_stretch(image):
    r, g, b = cv2.split(image)

    r_p = gray_process(r)
    g_p = gray_process(g)
    b_p = gray_process(b)

    result = cv2.merge((r_p, g_p, b_p))
    return np.uint8(result)


def gray_process(gray, max_out=255, min_out=0):
    truncated_up = np.nanpercentile(gray, 98)  # 计算数据的98%个数，而忽略nan值。
    truncated_down = np.nanpercentile(gray, 2)
    truncated_gray = np.clip(gray, a_min=truncated_down, a_max=truncated_up)  # 将数组中的数限制在a_min与a_max之间
    processed_gray = ((truncated_gray - truncated_down) / (truncated_up - truncated_down)) * (
            max_out - min_out) + min_out
    return processed_gray


def draw_hist(gray_img):
    data = gray_img.flatten()
    n, bins, patches = plt.hist(data, bins=255)
    plt.show()
