from show_pic import gray_process
from pylab import *
import matplotlib.pyplot as plt
#
# Pan_dataset = landsat8('E:\\RSImg\\High_resolution')
# pan_img = Pan_dataset.read_envi()
# PCA_dataset = landsat8('E:\\RSImg\\pca_1')
# ref = PCA_dataset.read_envi()


def hist_eq(img):
    n_bins = int(np.nanpercentile(img, 100))
    img_hist, bins = np.histogram(img.flatten(), n_bins, normed=True)
    cdf = img_hist.cumsum()
    plt.plot(cdf)
    cdf = (n_bins - 1) * cdf / cdf[-1]
    plt.show()
    im2 = np.interp(img.flatten(), bins[:-1], cdf)
    # np.interp(x, xp, fp) 一维线性插值. 返回离散数据的一维分段线性插值结果.
    # x:待插入数据的横坐标. xp:原始数据点的横坐标. fp:原始数据点的纵坐标，和xp序列等长.
    # bins[:-1] 等价于bins[0:len(s)]，除了最后一个元素的切片
    return im2.reshape(img.shape), cdf


def get_cdf(img):
    n_bins = int(np.nanpercentile(img, 100))
    img_hist, bins = np.histogram(img.flatten(), n_bins, normed=True)
    cdf = img_hist.cumsum()

    return img_hist, cdf


def hist_match(img, ref):
    img = gray_process(img, percent=0, max_out=np.nanpercentile(ref, 100), min_out=0)
    ref = gray_process(ref, percent=0, max_out=np.nanpercentile(ref, 100), min_out=0)
    img = img.astype(np.int32)
    ref = ref.astype(np.int32)
    img_eq, img_cdf = get_cdf(img)
    ref_eq, ref_cdf = get_cdf(ref)

    new_index = []
    out = np.zeros_like(img)
    for i in img_cdf:
        diff = list(abs(np.array(ref_cdf - i)))
        closest_index = diff.index((min(diff)))
        new_index.append(closest_index)

    new_index = np.array(new_index)
    out[:, :] = new_index[img[:, :]-1]
    out = gray_process(out, percent=0, max_out=np.nanpercentile(ref, 100), min_out=np.nanpercentile(ref, 0))

    return out
