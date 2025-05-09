import pandas as pd
import os
import glob

def process_csv_files(directory='spec-csv', combined_output='./result/combined_paper.csv', duplicate_output='./result/duplicate_dois.csv'):
    """
    处理目录中的所有CSV文件，找出重复DOI的行，并合并所有数据
    
    参数:
    directory -- 包含CSV文件的目录
    combined_output -- 合并所有数据的输出文件名
    duplicate_output -- 重复DOI数据的输出文件名
    """
    # 获取指定目录下的所有CSV文件
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    
    if not csv_files:
        print(f"在{directory}目录下没有找到CSV文件")
        return
    
    # 创建一个空的DataFrame来存储所有数据
    all_data = pd.DataFrame()
    
    # 读取并合并所有CSV文件
    for file in csv_files:
        print(f"处理文件: {file}")
        df = pd.read_csv(file)
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    # 保存所有数据到一个新的CSV文件
    all_data.to_csv(combined_output, index=False)
    print(f"所有数据已保存到 {combined_output}")
    
    # 查找重复的DOI
    duplicate_mask = all_data.duplicated(subset=['DOI'], keep=False)
    duplicates = all_data[duplicate_mask]
    
    # 如果存在重复项
    if not duplicates.empty:
        # 保存重复项到新的CSV文件
        duplicates.to_csv(duplicate_output, index=False)
        print(f"发现{len(duplicates)}个重复DOI行，已保存到{duplicate_output}")
    else:
        print("没有发现重复的DOI")

# 执行主函数
if __name__ == "__main__":
    # 可以指定目录，默认为当前目录
    process_csv_files()