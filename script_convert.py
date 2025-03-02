import json
import os
from pathlib import Path

def parse_file_to_dict(file_path):
    """
    将文件内容解析为字典，键为类型名称，值为类型描述
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 按空行分割成段落
    paragraphs = content.split('\n\n\n')
    
    result = {}
    for paragraph in paragraphs:
        # 跳过空段落
        if not paragraph.strip():
            continue
            
        # 分割段落为行
        lines = paragraph.strip().split('\n')
        
        # 第一行是类型名称
        if not lines:
            continue
            
        type_name = lines[0].strip()
        
        # 剩余行组成描述，保留原有换行符
        description = '\n'.join(lines[1:]).strip()
        
        if type_name and description:
            result[type_name] = description
    
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
            # 解析文件内容为字典
            content_dict = parse_file_to_dict(file_path)
            
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
                all_types.update(types)
        
        # 保存合并后的JSON
        output_all = data_dir / "所有类型.json"
        with open(output_all, 'w', encoding='utf-8') as f:
            json.dump(all_types, f, ensure_ascii=False, indent=2)
            
        print(f"已创建合并文件: {output_all}")
    except Exception as e:
        print(f"合并文件时出错: {str(e)}")

if __name__ == "__main__":
    main() 