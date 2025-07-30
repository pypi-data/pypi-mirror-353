import os
import pathlib
import numpy as np
from sko.SA import SA
from scipy import stats
from scipy.stats import truncnorm
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

def calculate_threshold(mu1=69.24, mu2=15.42, sigma1=10.22, sigma2=9.47, 
                       w1=0.7, w2=0.3, save_plot=False):
    """计算最优阈值"""
    # 目标函数
    def aim_function(x):
        p1 = w1 * (truncnorm((0 - mu1) / sigma1, (120 - mu1) / sigma1, mu1, sigma1).cdf(x))
        p2 = w2 * (1 - truncnorm((0 - mu2) / sigma2, (100 - mu2) / sigma2, mu2, sigma2).cdf(x))
        num = p1 + p2
        return num

    # 约束条件
    constraint_ueq = [
        lambda x: -x[0],    # x[0] >= 0
        lambda x: x[0] - 140  # x[0] <= 140
    ]

    # 使用模拟退火算法求解
    sa = SA(func=aim_function, x0=[0], T_max=1, T_min=1e-9, L=300, 
            max_stay_counter=150, constraint_ueq=constraint_ueq)
    best_x, best_y = sa.run()
    
    print(f'最佳阈值: {float(best_x[0]):.3f}, 最佳目标函数值: {float(best_y):.3f}')
    
    # 绘制概率密度函数图形
    if save_plot:
        data_dir = get_data_dir()
        plot_path = os.path.join(data_dir, "threshold_plot.png")
        
        t = np.linspace(0, 140, 500)
        p1 = w1 * truncnorm((0 - mu1) / sigma1, (120 - mu1) / sigma1, mu1, sigma1).pdf(t)
        p2 = w2 * truncnorm((0 - mu2) / sigma2, (100 - mu2) / sigma2, mu2, sigma2).pdf(t)
        mix = p1 + p2
        
        plt.figure(figsize=(10, 6))
        plt.plot(t, p1, 'b-', label='分布1')
        plt.plot(t, p2, 'r-', label='分布2')
        plt.plot(t, mix, 'k-', label='混合分布')
        plt.axvline(x=float(best_x[0]), color='g', linestyle='--', label=f'阈值={float(best_x[0]):.3f}')
        plt.title('概率密度函数与最优阈值')
        plt.xlabel('速度')
        plt.ylabel('概率密度')
        plt.legend()
        plt.savefig(plot_path)
        plt.close()
        print(f'图形已保存到: {plot_path}')
    
    return float(best_x[0])

def main(mu1=69.24, mu2=15.42, sigma1=10.22, sigma2=9.47, 
        w1=0.7, w2=0.3, save_plot=False):
    """主函数"""
    return calculate_threshold(mu1, mu2, sigma1, sigma2, w1, w2, save_plot)

if __name__ == "__main__":
    main(save_plot=True)