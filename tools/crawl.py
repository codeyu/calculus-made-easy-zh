#!/usr/bin/env python3
# coding: utf-8

import sys
import requests
from bs4 import BeautifulSoup
import os
from tomd import Tomd
import re
from urllib.parse import urlparse

def clean_filename(url):
    """Generate a clean filename from URL"""
    parsed = urlparse(url)
    filename = parsed.path.strip('/')
    if not filename:
        filename = 'index'
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename + '.md'

def clean_html(html_content):
    """Clean and prepare HTML for markdown conversion"""
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除不需要的标签
    for tag in ['script', 'style', 'iframe', 'noscript']:
        for element in soup.find_all(tag):
            element.decompose()
    
    # 处理数学公式
    # KaTeX/MathJax inline math
    for math in soup.find_all('span', class_='math'):
        math.string = f"${math.get_text()}$"
        math.unwrap()
    
    # KaTeX/MathJax display math
    for math in soup.find_all('div', class_='math'):
        math.string = f"\n$${math.get_text()}$$\n"
        math.unwrap()
    
    # 处理代码块
    for pre in soup.find_all('pre'):
        if pre.code:
            language = pre.code.get('class', [''])[0].replace('language-', '') or 'text'
            pre.string = f"\n```{language}\n{pre.get_text()}\n```\n"
    
    return str(soup)

def crawl_url(url):
    """Crawl the given URL and return HTML content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # 检测并设置正确的编码
        if response.encoding.lower() == 'iso-8859-1':
            response.encoding = response.apparent_encoding
            
        return response.text
    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python crawl.py URL")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Crawling {url}...")
    
    # 创建tools目录（如果不存在）
    os.makedirs('tools', exist_ok=True)
    
    # 爬取内容
    html_content = crawl_url(url)
    
    # 清理和准备HTML
    clean_html_content = clean_html(html_content)
    
    # 转换为Markdown
    markdown = Tomd(clean_html_content).markdown
    
    # 生成输出文件名
    output_file = os.path.join('tools', clean_filename(url))
    
    # 保存Markdown文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Successfully converted to Markdown: {output_file}")

if __name__ == "__main__":
    main()
