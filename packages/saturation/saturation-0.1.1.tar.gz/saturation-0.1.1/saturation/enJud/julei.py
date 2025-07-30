import pandas as pd
import numpy as np
from sklearn.mixture import BayesianGaussianMixture
from sklearn import preprocessing
import matplotlib.pyplot as plt

# 定义文件路径
file_path = r"D:\PycharmProjects\服务区饱和度分析\data\聚类结果.csv"
# file_path = r"E:\魏铨\实验结果\etc\下行\聚类结果_1.csv"
# 读取数据
# data = pd.read_csv(r"E:\魏铨\实验结果\etc\下行\total_1.csv")
data = pd.read_csv(r"D:\PycharmProjects\服务区饱和度分析\data\total.csv")
# 分离训练数据和测试数据，比例为4:1
total_samples = len(data)
test_size = int(total_samples * 0.2)  # 20%的数据作为测试数据
train_data = data.iloc[:test_size]
test_data = data.iloc[test_size:]

# 提取特征
x_train = train_data[['p1', 'p2']]
x_test = test_data[['p1', 'p2']]

# 数据标准化
min_max_scaler = preprocessing.MinMaxScaler()
X_train = min_max_scaler.fit_transform(x_train)
X_test = min_max_scaler.transform(x_test)

# 训练模型
gmm = BayesianGaussianMixture(n_components=2, covariance_type='diag', n_init=5, max_iter=1000).fit(X_train)

# 预测标签
y_pred_train = gmm.predict(X_train)
y_pred_test = gmm.predict(X_test)

# 将标签添加到原始数据中
train_data['label'] = y_pred_train
test_data['label'] = y_pred_test
data['label'] = np.nan  # 先为整个dataframe的'label'列赋值为NaN
data.loc[:len(train_data)-1, 'label'] = train_data['label']  # 填充训练数据的标签
data.loc[len(train_data):, 'label'] = test_data['label']  # 填充测试数据的标签
data.to_csv(file_path, index=False)  # 保存结果

print("聚类方法估计完成，标签已保存！")

# 绘制散点图
plt.figure(figsize=(10, 8))
plt.scatter(x_train.iloc[:, 0], x_train.iloc[:, 1], c=y_pred_train, label='Training Data', alpha=0.7)
plt.scatter(x_test.iloc[:, 0], x_test.iloc[:, 1], c=y_pred_test, label='Test Data', alpha=0.7)
plt.title('Gaussian Mixture Model Clustering Results')
plt.xlabel('Feature p1')
plt.ylabel('Feature p2')
plt.legend()
plt.show()