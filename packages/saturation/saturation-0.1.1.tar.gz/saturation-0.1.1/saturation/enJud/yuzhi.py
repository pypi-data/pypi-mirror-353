#导库
from sko.SA import SA
from scipy import stats
from scipy.stats import truncnorm


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