import pandas as pd
import re
import os

# 定义要检查的关键词列表
Check_Keywords = [
    "deep learning super-resolution",
    "deep learning super resolution",
    "signal reconstruction",
    "super-resolution", 
    "super resolution",
    "spectral resolution",
    "low-resolution spectra",
    "low resolution",
    "resolution enhancement", 
    "astronomical spectra",
    "high resolution reconstruction",
    "stellar classification",
    "feature extraction",
    "stellar spectroscopy",
    "information recovery",
    "spectral line detection",
    "astronomical data processing",
    "spectral analysis",
    "astronomical parameter prediction",
]

# 确保目标目录存在
os.makedirs("./result", exist_ok=True)

# 读取CSV文件
df = pd.read_csv("./result/combined_paper.csv")

# 转换关键词为小写便于不区分大小写匹配
keywords_lower = [keyword.lower() for keyword in Check_Keywords]

# 定义函数来检查标题是否包含关键词
def contains_keyword(title):
    if not isinstance(title, str):
        return False
    title_lower = title.lower()
    for keyword in keywords_lower:
        if keyword in title_lower:
            return True
    return False

# 筛选包含关键词的行
filtered_df = df[df['Title'].apply(contains_keyword)]

# 保存筛选结果到新文件
filtered_df.to_csv("./result/Screening.csv", index=False)

print(f"筛选完成。找到 {len(filtered_df)} 篇包含关键词的论文。")
print(f"结果已保存至 ./result/Screening.csv") 