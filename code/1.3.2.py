"""Todo:
1.回帖中的回复，点评 √
2.开头的贴子地址，保存的文件名(安全目录)  √
3.附件处理和附件图片移除   √
4.table使用容器嵌套，使其能够水平滚动  √
5.<iframe标签js处理     √
6.代码框字体大小调整
7.添加原帖地址(出处)    √
"""
import re
import os
import sys
from bs4 import BeautifulSoup,Tag
import requests
import base64
import htmlmin


attachment_counts = 0
session52 = requests.Session()# 一定要用，否则会出现频率限制
session = requests.Session()# 一定要用，否则会出现频率限制

def safe_filename(filename):
    # 定义非法字符及其对应的全角符号
    illegal_to_fullwidth = {
        '\\': '＼',
        '/': '／',
        ':': '：',
        '*': '＊',
        '?': '？',
        '"': '＂',
        '<': '＜',
        '>': '＞',
        '|': '｜',
    }
    
    # 处理成对的引号
    # 先用临时标记替换成对的双引号
    temp_paired = "___TEMP_PAIRED___"
    filename = re.sub(r'\"(.+?)\"', lambda m: f'“{m.group(1)}”', filename)
    
    # 逐个字符处理剩余的单引号
    safe_name = []
    for char in filename:
        if char in illegal_to_fullwidth:
            if char == '"':
                safe_name.append('“')  # 替换为左双引号
            else:
                safe_name.append(illegal_to_fullwidth[char])  # 替换为全角符号
        else:
            safe_name.append(char)  # 其他字符直接保留
    
    safe_name = ''.join(safe_name)
    
    # 如果文件名为空，返回默认名称
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name

def create_folder_if_not_exists(folder_path):
    """
    如果文件夹不存在，则自动创建
    :param folder_path: 文件夹路径
    """
    if not os.path.exists(folder_path):  # 判断文件夹是否存在
        os.makedirs(folder_path)  # 创建文件夹
        # print(f"文件夹 '{folder_path}' 已创建")
    # else:
        # print(f"文件夹 '{folder_path}' 已存在")


def replace_img(soup):
    def downloadImage_and_base64(url):
        global session52
        url = url.strip()# 一定要加，血泪教训
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://www.52pojie.cn/" + url
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
            "Referer":"https://www.52pojie.cn/"
        }
        if url.startswith("https://attach.52pojie.cn/"):
           # headers["Referer"]="https://www.52pojie.cn/"
           response = session52.get(url, headers=headers)
        else:
            response = session.get(url, headers=headers,verify = False)# ,verify = False
            # print(url)
            # response = requests.get(url)
        # if 'Referer' in headers:
            # del headers["Referer"]
        
        if response.status_code >= 200 and response.status_code < 300:
            # with open("/storage/emulated/0/0python/pylearn/52html/bs4/2.png", "wb") as f:
                # f.write(response.content)
                
            return base64.b64encode(response.content).decode('utf-8')
            # return ""
        else:
            raise RuntimeError(f"download failed,status_code = {response.status_code}")
            # return None
    
    global attachment_counts
    
    for tag in soup.find_all('img'):
        # Extract alt text from the surrounding div's strong tag if available
        alt_text = ""
        image_url = tag.get("file", tag.get("src", ""))
        # if "https://static.52pojie.cn/static/image/filetype/zip.gif" == image_url:    # text.gif
        if image_url.startswith("https://static.52pojie.cn/static/image/filetype/"):# 附件处理
            attachment_counts += 1
            tag.parent.decompose()
            image_url = ""
            continue

        if image_url.startswith("https://attach.52pojie.cn/"):
            xs0 = tag.parent.find('div', class_='xs0')
            if isinstance(xs0, Tag):
                alt_text = xs0.find('strong').get_text()  
        
        if tag.parent.name == "ignore_js_op":
            tag = tag.parent# .parent
            # print(tag)
                
        print(image_url)
        
        img_base64 = downloadImage_and_base64(image_url.strip())
        tag.replace_with(BeautifulSoup("", 'html.parser').new_tag('img', src=f"data:image;base64,{img_base64}", alt=alt_text))
        # try:
            # tag.parent.replace_with(BeautifulSoup("", 'html.parser').new_tag('img', src=f"data:image;base64,{img_base64}", alt=alt_text))
        # except Exception as e:
            # pass
        image_url = ""
            



     

# 定义函数：读取HTML文件内容
def read_html_file(file_path, encoding='gb2312'):
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            return file.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None






# 定义函数：读取utf-8文件内容
def read_file(file_path, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
        return ""
    except Exception as e:
        print(f"读取CSS文件时发生错误：{e}")
        return ""

# 定义函数：生成HTML模板
def generate_html_template(url):
    
    style = f"<style>{read_file(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"core","style_min.css"))}</style>"
    
    js = f"<script>{read_file(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"core","js_min.js"))}</script>"
    
    code_tool = """
    <div id="zxsq-markdown-code-tools" style="display:none;">
        <span class="show">显示代码</span>
        <span class="hide">隐藏代码</span>
        <span class="copy">复制代码</span>
        <span class="copysucc" style="display:none">代码已复制到剪贴板</span>
    </div>
    
    """
    code_tool += js
    new_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>帖子内容</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        {style}
        {code_tool}
    </head>
    <body>
        
        <div class="container">
        <p>原帖地址:{url}</p>
    """
    
    return new_html






# 定义函数：将新的HTML内容写入文件
def write_html_file(file_path, content, encoding='utf-8'):
    try:
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(content)
        print(f"提取完成，已生成新的HTML文件：{file_path}")
    except Exception as e:
        print(f"写入文件时发生错误：{e}")

def format_pre_tags(soup):
    # soup = BeautifulSoup(html, 'html.parser')
    for viewsource in soup.find_all("em",class_ = "viewsource"):
        vp =  viewsource.parent.parent
        
        # print(f"vp type:{type(vp)}")
        vp.unwrap()
        viewsource.parent.decompose()
           
    for pre in soup.find_all('pre', class_=lambda x: x and re.search(r'brush:\s*\w+', x)):
        # 提取 class 属性（可能是一个列表或字符串）
        class_attr = pre.get('class', [])
        if isinstance(class_attr, list):
            class_attr = ' '.join(class_attr)  # 合并为字符串

        match = re.search(r'brush:\s*(\w+)', class_attr)
        if not match:
            continue  # 如果没有匹配到语言，跳过
        
        language = match.group(1)  # 提取语言部分
        
        code = soup.new_tag('code', **{'class': f'{language}'})# 不能写规范，因为论坛有些语言设置不对
        for content in pre.contents:
            code.append(content)
        
        # 清空 <pre> 的原有属性和内容
        pre.clear()
        pre.attrs = {}
        
        # 将 <code> 插入 <pre> 内部
        pre.append(code)

        
    return soup

def add_post(position,author,post_time,post_content,p_comment):
    if p_comment is not None:
        html = f"""
                <div class="postcontent">
                    <h1>{position}</h1>
                    <div class="author">{author}</div>
                    <div class="timestamp">{post_time}</div>
                    {post_content}
                    <div class="comment-container">
                    <div class="comment-header">点评</div>
                    <div class="comment-body">
                        <div class="comment-author">{p_comment["author_text"]}</div>
                        {p_comment["content_text"]}
                        <div class="comment-time">{p_comment["time_text"]}</div>
                    </div>
                </div>
                </div>
        """
    else:
        html = f"""
                <div class="postcontent">
                    <h1>{position}</h1>
                    <div class="author">{author}</div>
                    <div class="timestamp">{post_time}</div>
                    {post_content}
                </div>
                """
    return html




# 主程序
if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),"output")
    create_folder_if_not_exists(output_path)
    # 读取HTML文件
    html_file_path = r"X:\52\net\《安卓逆向这档事》第二十六课、Unidbg之补完环境我就睡(下).html"
    html_content = read_html_file(html_file_path)
    if html_content is None:
        exit()
    
    url = ""
    match = re.search(r'href="(https?://[^"]+)"', html_content)
    if match:
        url = match.group(1)
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # .find('div', class_='t_fsz').find('td', class_='t_f')
    # post_content = soup.find('div', class_='pcb').find('div', class_='t_fsz')
    format_pre_tags(soup)
    
    for div in soup.find_all('div', class_='parsedown-markdown'):
        div.unwrap()
    
    new_html = generate_html_template(url)
    
    
    for post_content in soup.find_all('div', class_='pcb'):
        if post_content.find('div', class_ = "locked") is not None:# 排除"作者被禁止或删除 内容自动屏蔽"的情况
            continue
        
        
        
        post_parent = post_content.parent.parent
        # 提取作者名称
        author_tag = post_parent.find('span', class_='res-author')
        author = author_tag.find('a').text if author_tag and author_tag.find('a') else None
        
        
        # 提取发表时间
        post_time_tag = post_parent.find('span', class_='poston')
        post_time = post_time_tag.next_sibling.strip() if post_time_tag else None
        
        
        position = post_parent.find('a', onclick="setCopy(this.href, '帖子地址复制成功');return false;")
        position = position.text.strip()
        
        # is_op = is_op_tag.text if is_op_tag else None
        
        # 输出结果
        print(f"作者: {author}")
        print(f"发表时间: {post_time}")
        print(f"位置: {position}")

        
        
        soup1 = BeautifulSoup(str(post_content.find('div', class_='t_fsz')), 'html.parser')
        soup1.find('td', class_="t_f").parent.parent.parent.unwrap()
        soup1.find('td', class_="t_f").parent.parent.unwrap()
        soup1.find('td', class_="t_f").parent.unwrap()
        soup1.find('td', class_="t_f").unwrap()
                
        # print(str(soup1))
        # post = post_content.find('td', class_="t_f")
        
        # post_content.find('td', class_="t_f").parent.parent.parent.unwrap()
        # post_content.find('td', class_="t_f").parent.parent.unwrap()
        # post_content.find('td', class_="t_f").parent.unwrap()
        # post_content.find('td', class_="t_f").unwrap()
        
        # print(post)
        element = post_content.find('div',class_ = "psta vm")
        if element is None:
            p_comment = None
        else:
            # 定位 class="xi2 xw1" 的元素
            author = element.find('a', class_='xi2 xw1')
            author_text = author.get_text()
            
            content = None
            for e in element.next_siblings:
                if isinstance(e,Tag):
                    if e.name == 'div':
                        content = e
            
            # content_text = ''.join([text for text in content.stripped_strings if '发表于' not in text]).strip()
            
            time_span = content.find('span', class_='xg1')
            time_text = time_span.text.strip() if time_span else None
            
            if time_span:
                time_span.decompose()
            content['class'] = ['comment-text']
            replace_img(content)
            
            print(author_text)
            print(content)
            print(time_text)
            print()
            p_comment = {
            "author_text" : author_text,
            "content_text" : str(content),
            "time_text" : time_text
            }
        
        replace_img(soup1)
        new_html += add_post(position,author,post_time,str(soup1),p_comment)
        author_text = ""
        content_text = ""
        time_text = ""
        # if post_content is None:
            # exit()
    
    new_html += "</div>"
    
    for script in soup.find_all('script'):
        if 'iframe' in script.text:
            new_html += str(script)
            # print(script)
    
    new_html += "</body></html>"

    new_html = re.sub(
    r'(<table[^>]*>)(.*?</table>)', 
    r'<div class="table-container">\1\2</div>', 
    new_html, 
    flags=re.DOTALL
    )
    
    new_html = htmlmin.minify(new_html, remove_comments=True, remove_empty_space=True)

    
    thread_subject=""
    span_tag = soup.find('span', id='thread_subject')
    file_ = ""
    if span_tag:
        thread_subject = span_tag.get_text()
        file_=os.path.join(output_path,safe_filename(thread_subject)+".html")
    
    write_html_file(file_,new_html )
    if attachment_counts == 0:
        print(f"文件{safe_filename(thread_subject)}.html保存完成")
    else:
        print(f"文件{safe_filename(thread_subject)}.html保存完成,有{attachment_counts}个附件！")
        attachment_counts = 0
