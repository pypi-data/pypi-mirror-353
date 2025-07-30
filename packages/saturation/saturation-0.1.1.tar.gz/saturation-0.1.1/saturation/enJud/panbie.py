import pandas as pd

# 指定文件路径
input_file_path = r"E:\魏铨\实验结果\etc\下行\speed_current_1.csv"
output_file_path = r"E:\魏铨\实验结果\etc\下行\速度判别数据_1.csv"

# 读取CSV文件
df = pd.read_csv(input_file_path)

# 定义速度阈值
speed_threshold_0 = 66.268
speed_threshold_1 = 39.582

# 根据vehicletype_x的值和v_b的值来计算flag列
df['flag'] = df.apply(lambda row: 1 if (row['vehicletype_x'] == 0 and row['v'] < speed_threshold_0) or
                                           (row['vehicletype_x'] == 1 and row['v'] < speed_threshold_1)
                       else 0, axis=1)

# 将结果保存到新的CSV文件
df.to_csv(output_file_path, index=False)

print(f'Results have been saved to {output_file_path}')