import pandas as pd
import numpy as np
import os
import pathlib
from sklearn.mixture import BayesianGaussianMixture
from sklearn import preprocessing
import matplotlib.pyplot as plt

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def perform_clustering(input_filename="total.csv", output_filename="聚类结果.csv", 
                     n_components=2, test_size=0.2, plot=True):
    """执行聚类分析"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    # 读取数据
    data = pd.read_csv(input_path)
    
    # 分离训练数据和测试数据，比例为4:1
    total_samples = len(data)
    test_samples = int(total_samples * test_size)  # 20%的数据作为测试数据
    train_data = data.iloc[:test_samples]
    test_data = data.iloc[test_samples:]
    
    # 提取特征
    x_train = train_data[['p1', 'p2']]
    x_test = test_data[['p1', 'p2']]
    
    # 数据标准化
    min_max_scaler = preprocessing.MinMaxScaler()
    X_train = min_max_scaler.fit_transform(x_train)
    X_test = min_max_scaler.transform(x_test)
    
    # 训练模型
    gmm = BayesianGaussianMixture(n_components=n_components, 
                                covariance_type='diag', 
                                n_init=5, 
                                max_iter=1000).fit(X_train)
    
    # 预测标签
    y_pred_train = gmm.predict(X_train)
    y_pred_test = gmm.predict(X_test)
    
    # 将标签添加到原始数据中
    train_data['label'] = y_pred_train
    test_data['label'] = y_pred_test
    data['label'] = np.nan  # 先为整个dataframe的'label'列赋值为NaN
    data.loc[:len(train_data)-1, 'label'] = train_data['label']  # 填充训练数据的标签
    data.loc[len(train_data):, 'label'] = test_data['label']  # 填充测试数据的标签
    
    # 保存结果
    data.to_csv(output_path, index=False)
    
    print(f"聚类方法估计完成，标签已保存到：{output_path}")
    
    # 绘制散点图
    if plot:
        plt.figure(figsize=(10, 8))
        plt.scatter(x_train.iloc[:, 0], x_train.iloc[:, 1], c=y_pred_train, label='Training Data', alpha=0.7)
        plt.scatter(x_test.iloc[:, 0], x_test.iloc[:, 1], c=y_pred_test, label='Test Data', alpha=0.7)
        plt.title('Gaussian Mixture Model Clustering Results')
        plt.xlabel('Feature p1')
        plt.ylabel('Feature p2')
        plt.legend()
        plt.show()
    
    return output_path

def main(input_filename="total.csv", output_filename="聚类结果.csv", 
        n_components=2, test_size=0.2, plot=False):
    """主函数"""
    return perform_clustering(input_filename, output_filename, 
                            n_components, test_size, plot)

if __name__ == "__main__":
    main()