# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/6/3 下午3:20
# @项目:       TestProject
# @FileName:  form_data_boundary.py
# ----------------------------
import shlex


def curl_boundary(curl_command):
    """特殊类型multipart/form-data; boundary=----WebKitFormBoundaryppCPp5GdguiaaILe解析"""
    parts = shlex.split(curl_command)

    url = None
    headers = {}
    data = ''
    boundary = ''

    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith('http'):
            url = part
        elif part == '-H':
            header_line = parts[i + 1]
            key, val = header_line.split(':', 1)
            headers[key.strip()] = val.strip()
            i += 1
        elif part in ('--data-raw', '--data', '-d'):
            raw_data = parts[i + 1]
            data = raw_data.replace('\\n', '\n').replace('\\r', '\r')
            i += 1
        i += 1

    if not url:
        raise ValueError("在curl命令中找不到URL")

    # 构建输出字符串
    code = f"import requests\n\nurl = '{url}'\nheaders = {{\n"
    for k, v in headers.items():
        code += f"    '{k}': '{v}',\n"
    code += "}\n"

    # 处理 data 字段，确保保留 \r\n 格式
    data_escaped = data.replace("\\", "\\\\") \
        .replace("'", "\\'") \
        .replace("\r\n", "\\r\\n")
    code += f"data = '{data_escaped[1:]}'\n\n"
    code += "response = requests.post(url, headers=headers, data=data)\nprint(response.text)\n"

    return code
