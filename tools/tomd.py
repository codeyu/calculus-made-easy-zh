# coding: utf-8

import re
import os
import warnings

__all__ = ['Tomd', 'convert']

MARKDOWN = {
    'h1': ('\n# ', '\n'),
    'h2': ('\n## ', '\n'),
    'h3': ('\n### ', '\n'),
    'h4': ('\n#### ', '\n'),
    'h5': ('\n##### ', '\n'),
    'h6': ('\n###### ', '\n'),
    'code': ('`', '`'),
    'ul': ('', ''),
    'ol': ('', ''),
    'li': ('- ', ''),
    'blockquote': ('\n> ', '\n'),
    'em': ('*', '*'),
    'strong': ('**', '**'),
    'block_code': ('\n```', '\n```\n'),
    'span': ('', ''),
    'p': ('\n', '\n'),
    'p_with_out_class': ('\n', '\n'),
    'inline_p': ('', ''),
    'inline_p_with_out_class': ('', ''),
    'b': ('**', '**'),
    'i': ('*', '*'),
    'del': ('~~', '~~'),
    'hr': ('\n---', '\n'),
    'thead': ('\n', '|------\n'),
    'tbody': ('\n', '\n'),
    'td': ('|', ''),
    'th': ('|', ''),
    'tr': ('', '\n'),
    'table': ('', '\n'),
    'e_p': ('', '\n'),
    'mathjax_inline': ('$', '$'),
    'mathjax_block': ('\n$$\n', '\n$$\n'),
    'sup': ('<sup>', '</sup>'),
    'note': ('\n> Note: ', '\n'),
    'pre': ('\n```\n', '\n```\n'),
    'br': ('\n', ''),
    'img': ('![', ')'),
    'a': ('[', ')'),
}

BlOCK_ELEMENTS = {
    'mathjax_block': r'<script type="math/tex; mode=display".*?>([\s\S]*?)</script>',
    'h1': r'<h1.*?>(.*?)</h1>',
    'h2': r'<h2.*?>(.*?)</h2>',
    'h3': r'<h3.*?>(.*?)</h3>',
    'h4': r'<h4.*?>(.*?)</h4>',
    'h5': r'<h5.*?>(.*?)</h5>',
    'h6': r'<h6.*?>(.*?)</h6>',
    'hr': r'<hr\s*/?>',
    'blockquote': r'<blockquote.*?>([\s\S]*?)</blockquote>',
    'ul': r'<ul.*?>([\s\S]*?)</ul>',
    'ol': r'<ol.*?>([\s\S]*?)</ol>',
    'block_code': r'<pre.*?><code.*?>([\s\S]*?)</code></pre>',
    'p': r'<p\s*(?:class="[^"]*")?>([\s\S]*?)</p>',
    'p_with_out_class': r'<p>([\s\S]*?)</p>',
    'thead': r'<thead.*?>([\s\S]*?)</thead>',
    'tr': r'<tr.*?>([\s\S]*?)</tr>',
    'note': r'<note.*?>([\s\S]*?)</note>',
    'pre': r'<pre.*?>([\s\S]*?)</pre>',
}

INLINE_ELEMENTS = {
    'mathjax_inline': r'<script type="math/tex".*?>(.*?)</script>',
    'mathjax_block': r'<script type="math/tex; mode=display".*?>([\s\S]*?)</script>',
    'td': r'<td.*?>([\s\S]*?)</td>',
    'tr': r'<tr.*?>([\s\S]*?)</tr>',
    'th': r'<th.*?>([\s\S]*?)</th>',
    'b': r'<b.*?>([\s\S]*?)</b>',
    'i': r'<i.*?>([\s\S]*?)</i>',
    'del': r'<del.*?>([\s\S]*?)</del>',
    'inline_p': r'<p\s*(?:class="[^"]*")?>([\s\S]*?)</p>',
    'inline_p_with_out_class': r'<p>([\s\S]*?)</p>',
    'code': r'<code.*?>([\s\S]*?)</code>',
    'span': r'<span.*?>([\s\S]*?)</span>',
    'ul': r'<ul.*?>([\s\S]*?)</ul>',
    'ol': r'<ol.*?>([\s\S]*?)</ol>',
    'li': r'<li.*?>([\s\S]*?)</li>',
    'img': r'<img.*?src="([^"]*)".*?(?:>|/>)',
    'a': r'<a[^>]*href="([^"]*)"[^>]*>([\s\S]*?)</a>',
    'em': r'<em.*?>([\s\S]*?)</em>',
    'strong': r'<strong.*?>([\s\S]*?)</strong>',
    'tbody': r'<tbody.*?>([\s\S]*?)</tbody>',
    'sup': r'<sup.*?>([\s\S]*?)</sup>',
    'br': r'<br\s*/?>',
}

CODE_CLEAN = {
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',    # html quote mark
    '<br>': '\n',
    '\r': '',         # windows \r character
    '\xc2\xa0': ' ',  # no break space
    '&amp;': '&',     # ampersand
    '&minus;': '-',   # minus sign
    '&plusmn;': '±',  # plus-minus sign
    '&times;': '×',   # multiplication sign
    '&divide;': '÷',  # division sign
    '&sum;': '∑',     # summation
    '&int;': '∫',     # integral
    '&infin;': '∞',   # infinity
    '&radic;': '√',   # square root
    '&deg;': '°',     # degree
}

REMOVE_ATTR = 'data-mathml=".*?"' # data-mathml contains '>', which will cause incorrect
                                  # match, must being removed at the first

DELETE_ELEMENTS = [
    r'<script.*?>[\s\S]*?</script>',
    r'<style.*?>[\s\S]*?</style>',
    r'<svg.*?>[\s\S]*?</svg>',
    r'<div.*?>',
    r'</div>',
    r'<!--.*?-->',  # 删除HTML注释
]

class Element:
    def __init__(self, start_pos, end_pos, content, tag, folder, is_block=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.content = content
        self._elements = []
        self.is_block = is_block
        self.tag = tag
        self.folder = folder
        self._result = None

    def __str__(self):
        wrapper = MARKDOWN.get(self.tag)
        if wrapper is None:
            warnings.warn(f"Unknown tag type: {self.tag}, using plain text")
            return self.content
        self._result = '{}{}{}'.format(wrapper[0], self.content, wrapper[1])
        return self._result

    def parse_inline(self):
        """Parse inline elements in the content."""
        if not self.content:
            return

        # 处理特殊标签
        for tag in ['img', 'a', 'br', 'hr']:
            pattern = INLINE_ELEMENTS.get(tag)
            if not pattern:
                continue
            
            if tag == 'img':
                self.content = re.sub(pattern, r'![](\1)', self.content)
            elif tag == 'a':
                self.content = re.sub(pattern, r'[\2](\1)', self.content)
            elif tag == 'br':
                self.content = re.sub(pattern, r'\n', self.content)
            elif tag == 'hr':
                self.content = re.sub(pattern, r'\n---\n', self.content)

        # 处理其他内联标签
        for tag, pattern in INLINE_ELEMENTS.items():
            if tag in ['img', 'a', 'br', 'hr']:
                continue
                
            wrapper = MARKDOWN.get(tag)
            if not wrapper:
                continue

            try:
                if tag == 'strong':
                    self.content = re.sub(pattern, lambda m: '**' + m.group(1).strip() + '**', self.content)
                else:
                    self.content = re.sub(pattern, rf'{wrapper[0]}\1{wrapper[1]}', self.content)
            except Exception as e:
                warnings.warn(f"Error processing tag {tag}: {str(e)}")
                continue

        # 清理多余的空行
        self.content = re.sub(r'\n\s*\n\s*\n', '\n\n', self.content)


class Tomd:
    def __init__(self, html='', folder='', file='', options=None):
        self.html = html  # actual data
        self.folder = folder
        self.file = file
        self.options = options  # haven't been implemented yet
        self._markdown = self.convert(self.html, self.options)

    def clean_html(self, html):
        """Clean HTML content before conversion."""
        # 删除文件头部的 HTML 标签
        html = re.sub(r'<!DOCTYPE.*?>', '', html, flags=re.I | re.S)
        html = re.sub(r'<html.*?>.*?<body.*?>', '', html, flags=re.I | re.S)
        html = re.sub(r'</body>.*?</html>', '', html, flags=re.I | re.S)
        html = re.sub(r'<head.*?>.*?</head>', '', html, flags=re.I | re.S)
        html = re.sub(r'<meta[^>]*>', '', html, flags=re.I)
        html = re.sub(r'<title>.*?</title>', '', html, flags=re.I)
        html = re.sub(r'<link[^>]*>', '', html, flags=re.I)
        
        # 删除其他不需要的标签和注释
        for pattern in DELETE_ELEMENTS:
            html = re.sub(pattern, '', html, flags=re.I | re.S)
        
        # 预处理特定标签
        html = re.sub(r'<br\s*/?>', '\n', html)
        html = re.sub(r'<hr\s*/?>', '\n---\n', html)
        
        # 处理图片标签
        html = re.sub(r'<img.*?src="([^"]*)".*?(?:>|/>)', r'![](\1)', html)
        
        # 处理链接标签
        html = re.sub(r'<a[^>]*?name="([^"]*)"[^>]*>(.*?)</a>', r'\2', html)  # 删除命名锚点
        html = re.sub(r'<a[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html)
        
        # 处理段落标签
        html = re.sub(r'<p.*?>([\s\S]*?)</p>', lambda m: '\n' + m.group(1).strip() + '\n', html)
        
        # 处理引用块
        html = re.sub(r'<blockquote.*?>([\s\S]*?)</blockquote>', lambda m: '\n' + '\n> '.join(m.group(1).strip().split('\n')), html)
        
        # 处理代码块
        html = re.sub(r'<pre.*?>([\s\S]*?)</pre>', lambda m: '\n```\n' + m.group(1).strip() + '\n```\n', html)
        
        # 处理注释
        html = re.sub(r'<note.*?>([\s\S]*?)</note>', lambda m: '\n> Note: ' + '\n> '.join(m.group(1).strip().split('\n')), html)
        
        # 处理强调
        html = re.sub(r'<em.*?>([\s\S]*?)</em>', r'*\1*', html)
        html = re.sub(r'<strong.*?>([\s\S]*?)</strong>', lambda m: '**' + m.group(1).strip() + '**', html)
        
        # 处理上标
        html = re.sub(r'<sup.*?>([\s\S]*?)</sup>', r'<sup>\1</sup>', html)
        
        # 清理多余的空行和空格
        html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
        html = re.sub(r'^\s+', '', html)  # 删除开头的空白
        html = re.sub(r'\s+$', '', html)  # 删除结尾的空白
        html = re.sub(r'#\s+\n', '# ', html)  # 修复标题格式
        html = re.sub(r'>\s*\n\s*>', '>\n>', html)  # 修复引用块格式
        html = re.sub(r'```\n\s*\n', '```\n', html)  # 修复代码块格式
        html = re.sub(r'\n\s*\n```', '\n```', html)
        html = re.sub(r'\n{3,}', '\n\n', html)  # 清理多余的空行
        html = re.sub(r'(\S)\n(\S)', r'\1 \2', html)  # 修复段落内的换行
        
        return html.strip()

    def convert(self, html="", options=None):
        """Convert HTML to Markdown."""
        if not html:
            return ""
        
        # 基本清理
        html = html.replace('\r', '')
        html = html.replace('\xc2\xa0', ' ')
        
        # 清理和预处理 HTML
        html = self.clean_html(html)
        
        # 处理块级元素
        for tag, pattern in BlOCK_ELEMENTS.items():
            wrapper = MARKDOWN.get(tag)
            if not wrapper:
                continue
            
            try:
                matches = list(re.finditer(pattern, html, re.I | re.S))
                for m in reversed(matches):  # 从后向前处理，避免位置偏移
                    element = Element(
                        start_pos=m.start(),
                        end_pos=m.end(),
                        content=m.group(1).strip(),  # 清理内容的首尾空白
                        tag=tag,
                        folder=self.folder,
                        is_block=True
                    )
                    element.parse_inline()  # 处理内联元素
                    html = html[:m.start()] + str(element) + html[m.end():]
            except Exception as e:
                warnings.warn(f"Error processing block tag {tag}: {str(e)}")
                continue
        
        # 最后的清理
        html = re.sub(r'<[^>]+>', '', html)  # 删除任何剩余的 HTML 标签
        html = re.sub(r'\n{3,}', '\n\n', html)  # 清理多余的空行
        html = re.sub(r'#\s+\n', '# ', html)  # 修复标题格式
        html = re.sub(r'>\s*\n\s*>', '>\n>', html)  # 修复引用块格式
        html = re.sub(r'```\n\s*\n', '```\n', html)  # 修复代码块格式
        html = re.sub(r'\n\s*\n```', '\n```', html)
        html = re.sub(r'(\S)\n(\S)', r'\1 \2', html)  # 修复段落内的换行
        html = html.strip()  # 清理首尾空白
        
        return html

    @property
    def markdown(self):
        self.convert(self.html, self.options)
        return self._markdown

    def export(self, folder=False):
        if len(self.file) < 1:
            warnings.warn("file not specified, renamed to tmp.md")
            file = "tmp.md"
        else:
            file = self.file.replace('.html', '.md')  # rename to md
        if len(self.folder) < 2:
            warnings.warn("folder not specified, will save to pwd")
        elif not folder:
            file = self.folder + '/' + file
        else:  # if folder is specified
            file = folder + '/' + file
        f = open(file, 'w')
        f.write(self._markdown)
        f.close()


_inst = Tomd()
convert = _inst.convert