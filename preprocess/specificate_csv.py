#!/usr/bin/env python3

"""
脚本用于处理CSV文件和TXT文件，提取标题、作者、出版物和DOI信息
"""

import sys
import csv
import re
import os

# 强制刷新stdout，确保输出可见
sys.stdout.reconfigure(line_buffering=True)

# 从stderr重定向debug输出
debug_out = sys.stderr

def process_csv_file(file_path):
    """处理CSV文件，提取标题、作者、出版物和DOI信息"""
    entries = []
    
    try:
        print(f"尝试打开文件: {file_path}", file=debug_out)
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}", file=debug_out)
            return []
            
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            # 使用csv.reader处理CSV文件
            csv_reader = csv.reader(file)
            
            # 读取表头以确定字段位置
            headers = next(csv_reader, None)
            if not headers:
                print("警告: CSV文件为空或无法读取表头", file=debug_out)
                return []
                
            print(f"CSV表头: {headers}", file=debug_out)
            
            # 确定所需字段的索引位置
            title_idx = -1
            author_idx = -1
            publication_idx = -1
            doi_idx = -1
            year_idx = -1
            
            # 根据常见的表头名称查找索引
            for i, header in enumerate(headers):
                header_lower = header.lower().strip()
                if "title" in header_lower and "document" in header_lower:
                    title_idx = i
                elif "authors" in header_lower and "affiliation" not in header_lower:
                    author_idx = i
                elif "publication" in header_lower and "title" in header_lower:
                    publication_idx = i
                elif "doi" in header_lower:
                    doi_idx = i
                elif "year" in header_lower or ("publication" in header_lower and "year" in header_lower):
                    year_idx = i
            
            print(f"字段索引 - 标题:{title_idx}, 作者:{author_idx}, 出版物:{publication_idx}, DOI:{doi_idx}, 年份:{year_idx}", file=debug_out)
            
            # 如果找不到关键字段，尝试使用默认位置
            if title_idx == -1:
                title_idx = 0
                print(f"未找到标题字段，使用默认位置 {title_idx}", file=debug_out)
            if author_idx == -1:
                author_idx = 1
                print(f"未找到作者字段，使用默认位置 {author_idx}", file=debug_out)
            if publication_idx == -1:
                publication_idx = 3
                print(f"未找到出版物字段，使用默认位置 {publication_idx}", file=debug_out)
            
            # 处理每一行
            row_count = 1  # 从1开始，因为第0行是表头
            for row in csv_reader:
                row_count += 1
                
                try:
                    # 打印前几行用于调试
                    if row_count <= 5:
                        print(f"第{row_count}行: {row}", file=debug_out)
                    
                    # 确保行有足够的列
                    if not row or len(row) < max(title_idx, author_idx, publication_idx) + 1:
                        print(f"警告: 第{row_count}行列数不足，跳过。行内容: {row}", file=debug_out)
                        continue
                    
                    # 提取数据，处理索引可能超出范围的情况
                    title = row[title_idx].strip() if title_idx >= 0 and title_idx < len(row) else "Unknown"
                    author = row[author_idx].strip() if author_idx >= 0 and author_idx < len(row) else "Unknown"
                    publication = row[publication_idx].strip() if publication_idx >= 0 and publication_idx < len(row) else "Unknown"
                    
                    # 提取DOI，如果存在
                    doi = ""
                    if doi_idx >= 0 and doi_idx < len(row):
                        doi = row[doi_idx].strip()
                    
                    # 提取年份，如果存在
                    year = ""
                    if year_idx >= 0 and year_idx < len(row):
                        year = row[year_idx].strip()
                    
                    # 如果DOI不是以http://doi.org/或https://doi.org/开头，则添加前缀
                    if doi and not doi.startswith(("http://doi.org/", "https://doi.org/")):
                        doi = f"https://doi.org/{doi}"
                    
                    entries.append({
                        "title": title,
                        "author": author,
                        "year": year,
                        "publication": publication,
                        "doi": doi
                    })
                    
                except Exception as e:
                    print(f"处理第{row_count}行时出错: {e}", file=debug_out)
                    print(f"行内容: {row}", file=debug_out)
        
        print(f"从CSV文件中处理了 {len(entries)} 条记录", file=debug_out)
        return entries
        
    except Exception as e:
        print(f"处理CSV文件时出错: {e}", file=debug_out)
        import traceback
        traceback.print_exc(file=debug_out)
        return []

def process_txt_file(file_path):
    """处理TXT文件，从引用文本中提取标题、作者、出版物和DOI"""
    entries = []
    
    try:
        print(f"尝试打开文件: {file_path}", file=debug_out)
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在 - {file_path}", file=debug_out)
            return []
            
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            line_count = 0
            for line in file:
                line_count += 1
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                # 打印前几行用于调试
                if line_count <= 5:
                    print(f"第{line_count}行: {line[:100]}...", file=debug_out)
                
                # 跳过包含"Just Accepted"的行
                if "Just Accepted" in line:
                    print(f"跳过包含'Just Accepted'的引用 (第{line_count}行): {line[:50]}...", file=debug_out)
                    continue
                
                # 检查是否包含DOI
                doi_match = re.search(r'https?://doi\.org/([^\s]+)', line)
                if not doi_match:
                    print(f"跳过没有DOI的引用 (第{line_count}行): {line[:50]}...", file=debug_out)
                    continue
                
                doi = doi_match.group(0)  # 完整的DOI URL
                
                # 尝试提取年份 - 查找四位数字(年份)
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    year = year_match.group(0)
                    year_pos = line.find(year)
                    
                    # 1. 提取作者(从行开始到年份之前)
                    author = line[:year_pos].strip()
                    # 移除作者末尾的标点
                    author = re.sub(r'[.,]\s*$', '', author)
                    
                    # 提取年份后的内容
                    after_year = line[year_pos + len(year):].strip()
                    
                    # 2. 提取标题(年份后第一个句号后到下一个句号前)
                    # 找到年份后的第一个句号
                    first_dot = after_year.find('.')
                    if first_dot != -1:
                        # 标题从第一个句号后开始
                        title_start = first_dot + 1
                        # 找下一个句号作为标题结束
                        second_dot = after_year.find('.', title_start)
                        
                        if second_dot != -1:
                            title = after_year[title_start:second_dot].strip()
                            
                            # 3. 会议信息(第二个句号后到第三个句号前) - 不保存
                            
                            # 4. 出版商信息(第三个句号后到页码前)
                            third_dot = after_year.find('.', second_dot + 1)
                            if third_dot != -1:
                                publisher_start = third_dot + 1
                                
                                # 找到"Association for Computing Machinery"
                                acm_pos = after_year.find("Association for Computing Machinery", publisher_start)
                                if acm_pos != -1:
                                    # 找到页码(数字)
                                    # 使用正则表达式查找页码格式: 数字-数字
                                    page_match = re.search(r'\d+[-–]\d+', after_year[acm_pos:])
                                    if page_match:
                                        page_pos = after_year.find(page_match.group(0), acm_pos)
                                        publisher_end = page_pos
                                    else:
                                        # 如果找不到页码，使用DOI位置作为结束
                                        doi_pos_after_year = after_year.find(doi)
                                        publisher_end = doi_pos_after_year if doi_pos_after_year != -1 else len(after_year)
                                    
                                    # 提取出版商信息
                                    publication = after_year[publisher_start:publisher_end].strip()
                                else:
                                    # 如果找不到ACM，尝试找IEEE或其他出版商
                                    ieee_pos = after_year.find("IEEE", publisher_start)
                                    if ieee_pos != -1:
                                        # 寻找页码
                                        page_match = re.search(r'\d+[-–]\d+', after_year[ieee_pos:])
                                        if page_match:
                                            page_pos = after_year.find(page_match.group(0), ieee_pos)
                                            publisher_end = page_pos
                                        else:
                                            doi_pos_after_year = after_year.find(doi)
                                            publisher_end = doi_pos_after_year if doi_pos_after_year != -1 else len(after_year)
                                        
                                        publication = after_year[publisher_start:publisher_end].strip()
                                    else:
                                        # 如果找不到明确的出版商，尝试使用第三个句号到DOI的内容
                                        doi_pos_after_year = after_year.find(doi)
                                        if doi_pos_after_year != -1:
                                            # 向前找最近的数字，可能是页码
                                            page_match = re.search(r'\d+[-–]\d+', after_year[publisher_start:doi_pos_after_year])
                                            if page_match:
                                                publisher_end = after_year.find(page_match.group(0), publisher_start)
                                            else:
                                                publisher_end = doi_pos_after_year
                                            
                                            publication = after_year[publisher_start:publisher_end].strip()
                                        else:
                                            publication = after_year[publisher_start:].strip()
                            else:
                                # 如果找不到第三个句号，使用第二个句号后到DOI前的内容
                                remaining = after_year[second_dot + 1:].strip()
                                doi_pos_remaining = remaining.find(doi)
                                if doi_pos_remaining != -1:
                                    # 向前找最近的数字，可能是页码
                                    page_match = re.search(r'\d+[-–]\d+', remaining[:doi_pos_remaining])
                                    if page_match:
                                        publication = remaining[:remaining.find(page_match.group(0))].strip()
                                    else:
                                        publication = remaining[:doi_pos_remaining].strip()
                                else:
                                    publication = remaining
                            
                            # 清理出版物前后的标点和空格
                            publication = re.sub(r'^[.,\s]+|[.,\s]+$', '', publication)
                            
                            entries.append({
                                "title": title,
                                "author": author,
                                "year": year,
                                "publication": publication,
                                "doi": doi
                            })
                        else:
                            print(f"无法找到标题结束的句号 (第{line_count}行): {line[:50]}...", file=debug_out)
                    else:
                        print(f"无法找到年份后的第一个句号 (第{line_count}行): {line[:50]}...", file=debug_out)
                else:
                    print(f"无法解析引用中的年份 (第{line_count}行): {line[:50]}...", file=debug_out)
        
        print(f"从TXT文件中处理了 {len(entries)} 条记录", file=debug_out)
        return entries
        
    except Exception as e:
        print(f"处理TXT文件时出错: {e}", file=debug_out)
        import traceback
        traceback.print_exc(file=debug_out)
        return []

def write_csv_output(entries, output_file):
    """将处理后的条目写入CSV文件"""
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            # 创建CSV写入器
            csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            
            # 写入表头
            csv_writer.writerow(['Author', 'Title', 'Year', 'Publication', 'DOI'])
            
            # 写入数据行
            for entry in entries:
                csv_writer.writerow([
                    entry.get('author', 'Unknown'),
                    entry.get('title', 'Unknown'),
                    entry.get('year', 'Unknown'),
                    entry.get('publication', 'Unknown'),
                    entry.get('doi', '')
                ])
            
        print(f"已成功将 {len(entries)} 条记录写入到 {output_file}", file=debug_out)
        return True
    except Exception as e:
        print(f"写入CSV文件时出错: {e}", file=debug_out)
        import traceback
        traceback.print_exc(file=debug_out)
        return False

def main():
    if len(sys.argv) < 4:
        print("用法: python specificate_csv.py [csv|txt] <输入文件路径> <输出文件路径>", file=sys.stderr)
        sys.exit(1)
    
    file_type = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print(f"处理文件类型: {file_type}, 输入文件: {input_file}, 输出文件: {output_file}", file=debug_out)
    
    entries = []
    if file_type.lower() == "csv":
        entries = process_csv_file(input_file)
    elif file_type.lower() == "txt":
        entries = process_txt_file(input_file)
    else:
        print(f"不支持的文件类型: {file_type}", file=sys.stderr)
        sys.exit(1)
    
    if not entries:
        print("没有找到有效的条目，无法生成输出文件", file=sys.stderr)
        sys.exit(1)
    
    # 将处理后的条目写入CSV文件
    success = write_csv_output(entries, output_file)
    
    if success:
        print(f"CSV转换已完成，共 {len(entries)} 条记录已写入 {output_file}", file=debug_out)
    else:
        print("CSV转换失败", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
