from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn import model_selection
import show_pic
from sklearn import svm
from landsat8 import landsat8

test = landsat8('E:\\RSImg\\class_test.dat')
d = test.read_envi()


def Iris_label(s):
    it = {b'veg': 0, b'non_veg': 1}
    return it[s]


def RFC_training(sample):
    """
    训练模型
    :param sample: 样本数据
    :return: 训练结果
    """
    data = np.loadtxt(sample, dtype=float, delimiter=',', converters={7: Iris_label})
    x, y = np.split(data, indices_or_sections=(7,), axis=1)
    x = x[:, 0:7]
    train_data, test_data, train_label, test_label = \
        model_selection.train_test_split(x, y, random_state=1, train_size=0.9, test_size=0.1)
    classifier = RandomForestClassifier(n_estimators=100,
                                        bootstrap=True,
                                        max_features='sqrt')
    classifier.fit(train_data, train_label.ravel())

    print("训练集：", classifier.score(train_data, train_label))
    print("测试集：", classifier.score(test_data, test_label))

    return classifier


def SVM_training(sample):
    """
    训练模型
    :param sample: 样本数据
    :return: 训练结果
    """
    data = np.loadtxt(sample, dtype=float, delimiter=',', converters={7: Iris_label})
    x, y = np.split(data, indices_or_sections=(7,), axis=1)
    x = x[:, 0:7]
    train_data, test_data, train_label, test_label = \
        model_selection.train_test_split(x, y, random_state=1, train_size=0.9, test_size=0.1)
    classifier = svm.SVC(C=1, kernel='rbf', gamma=2, decision_function_shape='ovo')
    classifier.fit(train_data, train_label.ravel())

    print("训练集：", classifier.score(train_data, train_label))
    print("测试集：", classifier.score(test_data, test_label))

    return classifier


def RFCClass(dataset, sample):
    """
    随机森林分类
    :param dataset: 需要分类的数据集
    :param sample: 监督分类样本
    :return: 分类后图像
    """
    rf_model = RFC_training(sample)
    m, n, bands = dataset.shape

    data = np.zeros((m * n, bands))
    for i in range(bands):
        data[:, i] = dataset[:, :, i].flatten()

    pred = rf_model.predict(data)

    pred = pred.reshape(m, n) * 255
    pred = pred.astype(np.uint8)

    return pred


res = RFCClass(d, 'data.csv')
show_pic.show_single_band(res)
