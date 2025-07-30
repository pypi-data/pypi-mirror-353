# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# 导入必要的库
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from scipy import stats
import datetime
from scipy.stats import truncnorm
from sklearn.cluster import MiniBatchKMeans, KMeans
from sko.SA import SA
import os
import pathlib

def get_data_dir():
    """获取数据目录的绝对路径"""
    # 获取当前文件所在目录
    current_dir = pathlib.Path(__file__).parent.absolute()
    # 向上两级获取项目根目录
    project_root = current_dir.parent.parent
    # 数据目录
    data_dir = os.path.join(project_root, "result")
    return data_dir

def em(h,mu1,sigmal,w1,mu2,sigma2,w2):
    d=1
    n = len(h)  # 样本长度
    # E-step
    #计算响应
    # p1=w1*flot(stats.norm(mu1,sigmal))
    p1 =w1*stats.norm(mu1, sigmal).pdf(h)    
    p2=w2*stats.truncnorm((0 - mu2) / sigma2, (140 - mu2) / sigma2,mu2,sigma2).pdf(h)
    #p1, p2权重 
    P=p1+p2
    R1i = p1 / P
    R2i= p2 / P
    # M-step
    #mu1的更新
    mu1=np.sum(R1i*h)/np.sum(R1i)
    #mu2的更新
    m=n*w2*stats.norm.cdf(-mu2/sigma2)*(1-stats.norm.cdf(-mu2/sigma2))
    x2=np.sum(R2i * h) / np.sum(R2i)
    s2=np.sum(R2i*np.square(h-mu2))/(d*np.sum(R2i))
    u2=mu2
    mu2 = (1/(n*w2+m))*(n*w2*x2 + m*(u2-sigma2*(stats.norm.pdf(-u2/sigma2)/stats.norm.cdf(-u2/sigma2))) )
    #sigmal1的更新
    sigmal=np.sqrt(np.sum(R1i*np.square(h-mu1))/(d*np.sum(R1i)))
    #sigmal2的更新
    sigma2 = np.sqrt((1/(n*w2+m))*( n*w2*(s2+(x2-u2)*(x2-u2))+ m*sigma2*sigma2*(1-(u2/s2)*(stats.norm.pdf(-u2/sigma2)/stats.norm.cdf(-u2/sigma2)) )) )
    #w1的更新
    w1 = np.sum(R1i) / n
    #w2的更新
    w2 = np.sum(R2i) / n
    return mu1,sigmal,w1,mu2,sigma2,w2

# 获取数据目录
data_dir = get_data_dir()

# 读取CSV文件
file_path = os.path.join(data_dir, "speed_current.csv")
df = pd.read_csv(file_path)

# 筛选vehicletype_x列中值为1, 2, 3, 4的行
df_ke = df[df['vehicletype_x'].isin([1, 2, 3, 4])]
# 筛选vehicletype_x列中值为11, 12, 13, 14, 15, 16的行
df_huo = df[df['vehicletype_x'].isin([11, 12, 13, 14, 15, 16])]

h=df_huo['v_b'].values
l=len(h)
X=h.reshape(l,1)
k_means = KMeans( n_clusters=2, n_init=30) 
cls = k_means.fit(X) 
df.index = range(len(df))
df['lable']=pd.DataFrame(cls.labels_,columns=['label'])
df=df[['v_b','lable']]
df1=df[df['lable']==1]
df2=df[df['lable']==0]
df1=df1[['v_b']]
df2=df2[['v_b']]

#GMM的构造
#Step 1.首先对两种分布的均值、方差和权值进行初始化
mu1=float(df1.mean());sigmal=float(df1.std());w1=float(len(df1)/196025) #进入服务区的
mu2=float(df2.mean());sigma2=float(df2.std());w2=float(len(df2)/196025) #

d=1
n = len(h)  # 样本长度
m1=pd.Series(h).hist(bins=100,weights = np.zeros_like(h) + 1 / len(h))
m1.plot()

# 开始EM算法的主循环
for iteration in range(60):
    mu1,sigmal,w1,mu2,sigma2,w2=em(h,mu1,sigmal,w1,mu2,sigma2,w2)

#是否进入服务区以及混合后身高的概率密度曲线
t=np.linspace( 0,160,50)#500个
m = stats.norm.pdf(t,loc=mu1, scale=sigmal) # 不进入服务区分布的预测
f = stats.norm.pdf(t,loc=mu2, scale=sigma2) # 进入服务区分布的预测
mix=w1*m+w2*f#混合后
print(mu1)
print(mu2)
print(sigmal)
print(sigma2)
print(w1)
print(w2)
plt.plot(t, m, color='b')
plt.plot(t, f, color='r')
plt.plot(t, mix, color='k')

#计算阈值
# 目标函数
def aimFunction(x):
    mu1 = 69.24
    mu2 = 15.42
    sigma1 = 10.22
    sigma2 = 9.47
    p1 = 0.7* ( truncnorm((0 - mu1) / sigma1, (120 - mu1) / sigma1,mu1,sigma1).cdf(x)  )
    p2 = 0.3 * (1- truncnorm((0 - mu2) / sigma2, (100 - mu2) / sigma2,mu2,sigma2).cdf(x)   )
    l=len(x)
    num = p1 + p2
    return num

constraint_ueq = [
    lambda x:  - x[0] ,
    lambda x: x[0]  - 140
]

sa = SA(func=aimFunction, x0=[0], T_max=1, T_min=1e-9, L=300, max_stay_counter=150,constraint_ueq=constraint_ueq)
best_x, best_y = sa.run()
print('best_x:', best_x, 'best_y', best_y)