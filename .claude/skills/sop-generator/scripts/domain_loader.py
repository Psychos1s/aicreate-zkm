#!/usr/bin/env python3
"""
领域配置加载器（简化版）

用法:
  python domain_loader.py --domain <domain_id> --action <action>

参数:
  --domain: 领域标识
  --action: 操作类型：exists/info/questions/constraints/mapping
"""

import os
import sys
import json
import yaml
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent.parent.parent.parent


def get_domain_file(domain_id: str) -> Path:
    """获取领域配置文件路径"""
    project_root = get_project_root()
    domain_file = project_root / ".claude" / "skills" / "sop-generator" / "domains" / domain_id / "domain.yaml"
    if not domain_file.exists():
        domain_file = domain_file.with_suffix('.yml')
    return domain_file


def load_domain_config(domain_id: str) -> dict:
    """加载领域配置"""
    domain_file = get_domain_file(domain_id)
    if not domain_file.exists():
        raise FileNotFoundError(f"领域不存在: {domain_id}")
    
    with open(domain_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', required=True)
    parser.add_argument('--action', default='exists',
                        choices=['exists', 'info', 'questions', 'constraints', 'mapping',
                                 'node_example', 'field_specs', 'templates', 'all', 'schema_meta'])
    args = parser.parse_args()
    
    try:
        if args.action == 'exists':
            domain_file = get_domain_file(args.domain)
            print('true' if domain_file.exists() else 'false')
            return
        
        config = load_domain_config(args.domain)
        
        if args.action == 'info':
            info = config.get('domain', {})
            print(json.dumps(info, ensure_ascii=False))
            
        elif args.action == 'questions':
            # 直接返回 interview 数组
            interview = config.get('interview', [])
            print(json.dumps(interview, ensure_ascii=False))
            
        elif args.action == 'constraints':
            constraints = config.get('constraints', [])
            print(json.dumps(constraints, ensure_ascii=False))
            
        elif args.action == 'mapping':
            mapping = config.get('mapping', {})
            print(json.dumps(mapping, ensure_ascii=False))
            
        elif args.action == 'node_example':
            node_example = config.get('node_example', {})
            print(json.dumps(node_example, ensure_ascii=False))

        elif args.action == 'field_specs':
            field_specs = config.get('field_specs', {})
            print(json.dumps(field_specs, ensure_ascii=False))

        elif args.action == 'all':
            result = {
                'field_specs': config.get('field_specs', {}),
                'node_example': config.get('node_example', {}),
                'constraints': config.get('constraints', [])
            }
            print(json.dumps(result, ensure_ascii=False))

        elif args.action == 'templates':
            import sys
            template_file = config.get('field_template_file', '')
            if not template_file:
                print('')
                return
            domain_file = get_domain_file(args.domain)
            template_path = domain_file.parent / template_file
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
                # 使用UTF-8编码输出
                sys.stdout.buffer.write(content.encode('utf-8'))
            else:
                print('')

        elif args.action == 'schema_meta':
            # 读取 schema_meta.md 约束元文件
            domain_file = get_domain_file(args.domain)
            schema_meta_path = domain_file.parent / 'schema_meta.md'
            if schema_meta_path.exists():
                content = schema_meta_path.read_text(encoding='utf-8')
                print(content)
            else:
                print('')  # 文件不存在返回空

    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
