#!/usr/bin/env python3

"""
Simple script to convert NASA ADS BibTeX to CSV format.
"""

import sys
import re

# 强制刷新stdout，确保输出可见
sys.stdout.reconfigure(line_buffering=True)

entries = []
current_entry = {}
reading_entry = False

# 从stderr重定向debug输出
debug_out = sys.stderr

# 读取BibTeX
for line in sys.stdin:
    line = line.strip()
    
    # 开始新条目
    if line.startswith('@'):
        if current_entry and reading_entry:
            entries.append(current_entry)
        current_entry = {}
        reading_entry = True
        continue
    
    # 结束当前条目
    if line == "}" and reading_entry:
        if current_entry:
            entries.append(current_entry)
        current_entry = {}
        reading_entry = False
        continue
    
    # 解析条目中的字段
    if reading_entry and "=" in line:
        try:
            field, value = line.split("=", 1)
            field = field.strip()
            value = value.strip()
            
            # 移除结尾的逗号
            if value.endswith(","):
                value = value[:-1]
            
            # 清理值
            if value.startswith("{") and value.endswith("}"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            current_entry[field] = value
        except Exception as e:
            print(f"Error parsing line: {line}", file=debug_out)
            print(f"Exception: {e}", file=debug_out)

print(f"Processed {len(entries)} entries", file=debug_out)

# 输出CSV头部 - 添加DOI字段
print("Author,Title,Year,Publication,DOI", flush=True)

# 处理每个条目
csv_lines = []
for entry in entries:
    try:
        # 作者
        author = "Unknown"
        if "author" in entry:
            # 清理作者格式
            auth = entry["author"]
            # 移除大括号
            auth = re.sub(r'\{|\}', '', auth)
            author = auth
        
        # 标题
        title = "Unknown"
        if "title" in entry:
            # 清理标题格式
            title = entry["title"]
            title = re.sub(r'\{|\}', '', title)
            title = re.sub(r'^"|"$', '', title)
        
        # 年份
        year = "Unknown"
        if "year" in entry:
            year = entry["year"]
        
        # 出版物
        publication = "Unknown"
        if "journal" in entry:
            journal = entry["journal"]
            # 处理LaTeX格式的期刊名
            if journal.startswith("\\"):
                # 替换常见的LaTeX期刊缩写
                journal_map = {
                    "\\mnras": "Monthly Notices of the Royal Astronomical Society",
                    "\\apj": "The Astrophysical Journal",
                    "\\aap": "Astronomy and Astrophysics",
                    "\\aj": "The Astronomical Journal"
                }
                if journal in journal_map:
                    journal = journal_map[journal]
                else:
                    journal = journal.replace("\\", "")
            
            # 移除大括号
            journal = re.sub(r'\{|\}', '', journal)
            publication = journal
        
        # DOI
        doi = ""
        if "doi" in entry:
            # 添加DOI前缀
            doi_value = entry["doi"].strip()
            if doi_value:
                doi = f"https://doi.org/{doi_value}"
        
        # 转义CSV中的双引号
        author = author.replace('"', '""')
        title = title.replace('"', '""')
        publication = publication.replace('"', '""')
        doi = doi.replace('"', '""')
        
        # 准备CSV行 - 包含DOI
        csv_line = f'"{author}","{title}","{year}","{publication}","{doi}"'
        csv_lines.append(csv_line)
        
    except Exception as e:
        print(f"Error processing entry: {entry}", file=debug_out)
        print(f"Exception: {e}", file=debug_out)

# 输出所有CSV行
for line in csv_lines:
    print(line, flush=True)

# 确认脚本执行完成
print(f"CSV conversion completed with {len(csv_lines)} entries", file=debug_out)

