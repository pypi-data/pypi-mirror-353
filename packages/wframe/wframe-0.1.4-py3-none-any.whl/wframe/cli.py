import os
import click
from pathlib import Path

@click.group()
def main():
    """WFrame - 一个轻量级的 Python Web 框架"""
    pass

@main.command()
@click.argument('project_name')
def new(project_name):
    """创建一个新的 WFrame 项目"""
    # 创建项目目录
    os.makedirs(project_name, exist_ok=True)
    
    # 创建基本文件结构
    files = {
        'app.py': '''from wframe import WebFramework, Response

app = WebFramework()

@app.route('/')
def index(request):
    return Response('Hello, WFrame!')

if __name__ == '__main__':
    app.run()
''',
        'requirements.txt': '''wframe>=0.1.0
''',
        '.env': '''DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key-here
''',
        '.gitignore': '''__pycache__/
*.pyc
.env
*.db
'''
    }
    
    for filename, content in files.items():
        with open(os.path.join(project_name, filename), 'w') as f:
            f.write(content)
    
    click.echo(f'项目 {project_name} 创建成功！')
    click.echo(f'cd {project_name}')
    click.echo('python app.py')

@main.command()
def run():
    """运行 WFrame 应用"""
    if not os.path.exists('app.py'):
        click.echo('错误：未找到 app.py 文件')
        return
    
    os.system('python app.py')

if __name__ == '__main__':
    main() 