# 修复WorldView.py中的编码问题
with open('ui/panels/WorldView.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换全角逗号
content = content.replace('，', ',')

# 确保文件末尾没有多余的空行
content = content.rstrip() + '\n'

# 写回文件
with open('ui/panels/WorldView.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('文件修复完成') 