import json
import os
import re
from pathlib import Path

def parse_file_to_dict(file_path):
    """
    将文件内容解析为字典，键为类型名称，值为类型描述
    处理不同文件的特殊格式问题
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 根据文件名选择不同的解析策略
    file_name = Path(file_path).name
    
    if "剧本.txt" in file_name:
        return parse_screenplay_file(content)
    elif "剧本杀.txt" in file_name:
        return parse_murder_mystery_file(content)  
    elif "严肃小说.txt" in file_name:
        return parse_serious_novel_file(content)
    elif "网络小说.txt" in file_name:
        return parse_web_novel_file(content)
    elif "游戏剧情.txt" in file_name:
        return parse_game_story_file(content)
    else:
        # 默认的解析方法
        return parse_default(content)

def parse_screenplay_file(content):
    """解析剧本.txt文件"""
    result = {}
    
    # 通过识别类型名(通常是单行文本，后面跟着多行描述)来分割
    # 我们假设类型名是独立的一行，没有缩进，后面的段落是类型描述
    entries = re.split(r'\n\n+(?=\S)', content.strip())
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        type_name = lines[0].strip()
        if not type_name:
            continue
            
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
    
    return result

def parse_murder_mystery_file(content):
    """解析剧本杀.txt文件"""
    result = {}
    
    # 剧本杀文件以类型名称为标题，然后是多行的定义、特点、创作建议
    entries = re.split(r'\n\n+(?=\S)', content.strip())
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        type_name = lines[0].strip()
        if not type_name:
            continue
            
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
    
    return result

def parse_serious_novel_file(content):
    """解析严肃小说.txt文件"""
    result = {}
    
    # 严肃小说文件以类型名称为标题，然后是多行定义和元素
    entries = content.split("\n\n\n")
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines or len(lines) < 2:
            continue
            
        type_name = lines[0].strip()
        if not type_name:
            continue
            
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
    
    return result

def parse_web_novel_file(content):
    """解析网络小说.txt文件"""
    result = {}
    
    print("开始解析网络小说文件")
    # 按连续两个或以上的空行分割，这将分离每个类型的描述块
    blocks = re.split(r'\n\s*\n\s*\n', content.strip())
    print(f"找到 {len(blocks)} 个内容块")
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # 第一行是类型名称
        type_name = lines[0].strip()
        
        # 剩余部分是描述
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
            print(f"添加类型: '{type_name}'，描述长度: {len(description)}字符")
    
    print(f"解析完成，共找到 {len(result)} 个类型")
    return result

def parse_game_story_file(content):
    """解析游戏剧情.txt文件"""
    result = {}
    
    # 游戏剧情通常有明确的类型名称和多段落描述
    entries = re.split(r'\n\n+(?=\S)', content.strip())
    
    for entry in entries:
        lines = entry.strip().split('\n')
        if not lines:
            continue
            
        type_name = lines[0].strip()
        if not type_name:
            continue
            
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
    
    return result

def parse_default(content):
    """默认解析方法，按空行分割段落"""
    result = {}
    
    paragraphs = content.split('\n\n')
    
    current_type = None
    current_description = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        lines = paragraph.split('\n')
        if len(lines) == 1 and not lines[0].startswith(' '):
            # 如果有之前的类型和描述，保存它们
            if current_type and current_description:
                result[current_type] = '\n'.join(current_description).strip()
            
            # 新的类型
            current_type = lines[0]
            current_description = []
        else:
            # 继续当前类型的描述
            if current_type:
                current_description.append(paragraph)
    
    # 保存最后一个类型的描述
    if current_type and current_description:
        result[current_type] = '\n'.join(current_description).strip()
    
    return result

def main():
    # 数据文件路径
    data_dir = Path("data/学习数据")
    files = [
        data_dir / "剧本.txt",
        data_dir / "剧本杀.txt",
        data_dir / "网络小说.txt",
        data_dir / "严肃小说.txt",
        data_dir / "游戏剧情.txt"
    ]
    
    # 遍历处理每个文件
    for file_path in files:
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            continue
            
        try:
            print(f"正在处理文件: {file_path}")
            # 解析文件内容为字典
            content_dict = parse_file_to_dict(file_path)
            print(f"解析结果: 找到 {len(content_dict)} 个类型")
            
            # 创建JSON输出文件路径
            output_file = file_path.with_suffix('.json')
            
            # 保存为JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, ensure_ascii=False, indent=2)
                
            print(f"已转换: {file_path} -> {output_file}")
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    # 合并所有类型到一个总文件
    try:
        all_types = {}
        for file_path in files:
            if not file_path.exists():
                continue
                
            json_path = file_path.with_suffix('.json')
            if not json_path.exists():
                continue
                
            with open(json_path, 'r', encoding='utf-8') as f:
                types = json.load(f)
                print(f"从 {json_path} 加载了 {len(types)} 个类型")
                all_types.update(types)
        
        # 保存合并后的JSON
        output_all = data_dir / "所有类型.json"
        with open(output_all, 'w', encoding='utf-8') as f:
            json.dump(all_types, f, ensure_ascii=False, indent=2)
            
        print(f"已创建合并文件: {output_all}，共 {len(all_types)} 个类型")
    except Exception as e:
        print(f"合并文件时出错: {str(e)}")

if __name__ == "__main__":
    main() 