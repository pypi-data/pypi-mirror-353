import pandas as pd
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

def classify_by_speed(input_filename="speed_current1.csv", output_filename="速度判别数据.csv",
                     speed_threshold_0=66.268, speed_threshold_1=39.582, 
                     speed_column='v_b'):
    """根据速度阈值进行判别分析"""
    data_dir = get_data_dir()
    
    # 定义文件路径
    input_path = os.path.join(data_dir, input_filename)
    output_path = os.path.join(data_dir, output_filename)
    
    # 读取CSV文件
    df = pd.read_csv(input_path)
    
    # 根据vehicletype_x的值和速度值来计算flag列
    df['flag'] = df.apply(
        lambda row: 1 if (row['vehicletype_x'] == 0 and row[speed_column] < speed_threshold_0) or
                          (row['vehicletype_x'] == 1 and row[speed_column] < speed_threshold_1)
                  else 0, 
        axis=1
    )
    
    # 将结果保存到新的CSV文件
    df.to_csv(output_path, index=False)
    
    print(f'速度判别结果已保存到：{output_path}')
    return output_path

def main(input_filename="speed_current1.csv", output_filename="速度判别数据.csv",
        speed_threshold_0=66.268, speed_threshold_1=39.582,
        speed_column='v_b'):
    """主函数"""
    return classify_by_speed(input_filename, output_filename, 
                           speed_threshold_0, speed_threshold_1, 
                           speed_column)

if __name__ == "__main__":
    main()