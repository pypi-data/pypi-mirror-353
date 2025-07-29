from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import json
import time
import functools
import os
import pickle
from datetime import datetime, timedelta

class Session:
    def __init__(self, data=None):
        self.data = data or {}
        self.modified = False

class WebFramework:
    def __init__(self):
        self.url_map = Map()
        self.endpoints = {}
        self.middlewares = []
        self.error_handlers = {}
        self.secret_key = os.urandom(24)
        self.session_interface = None
        
        # 初始化 OpenAPI 规范
        self.spec = APISpec(
            title="Web Framework API",
            version="1.0.0",
            openapi_version="3.0.2",
            plugins=[MarshmallowPlugin()],
            info=dict(
                description="一个简单的Python Web框架API文档",
                contact=dict(
                    name="开发者",
                    email="developer@example.com"
                )
            )
        )
        
    def use(self, middleware):
        """添加中间件"""
        self.middlewares.append(middleware)
        return self
        
    def route(self, rule, methods=None, **kwargs):
        if methods is None:
            methods = ['GET']
            
        def decorator(f):
            endpoint = f.__name__
            self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
            self.endpoints[endpoint] = f
            
            # 添加 OpenAPI 文档
            if 'schema' in kwargs:
                self.spec.components.schema(kwargs['schema'].__name__, schema=kwargs['schema'])
                
                # 构建操作信息
                operations = {}
                for method in methods:
                    operations[method.lower()] = {
                        'summary': f.__doc__ or f"{method} {rule}",
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': kwargs['schema']
                                    }
                                },
                                'description': '成功响应'
                            }
                        }
                    }
                
                # 添加路径
                self.spec.path(
                    path=rule,
                    operations=operations
                )
            
            return f
        return decorator

    def errorhandler(self, code_or_exception):
        """注册错误处理器"""
        def decorator(f):
            self.error_handlers[code_or_exception] = f
            return f
        return decorator
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return self.endpoints[endpoint](request, **values)
        except HTTPException as e:
            return self.handle_error(e)
        except Exception as e:
            return self.handle_error(e)
    
    def handle_error(self, error):
        """处理错误"""
        if isinstance(error, HTTPException):
            code = error.code
        else:
            code = 500
            
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error)
            
        return Response(
            json.dumps({
                'error': str(error),
                'code': code
            }, ensure_ascii=False),
            status=code,
            mimetype='application/json'
        )
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        
        # 处理 OpenAPI 文档请求
        if request.path == '/openapi.json':
            return Response(
                json.dumps(self.spec.to_dict(), ensure_ascii=False),
                mimetype='application/json'
            )(environ, start_response)
            
        # 处理 API 文档页面请求
        if request.path == '/docs':
            return Response(
                open('static/swagger-ui.html').read(),
                mimetype='text/html'
            )(environ, start_response)
        
        # 初始化会话
        if self.session_interface:
            session = self.session_interface.open_session(self, request)
            if session is None:
                session = self.session_interface.make_null_session(self)
            request.session = session
        
        # 执行所有中间件
        response = request
        for middleware in self.middlewares:
            response = middleware(request)
            if isinstance(response, Response):
                break
                
        if not isinstance(response, Response):
            response = self.dispatch_request(request)
            
        # 保存会话
        if self.session_interface and hasattr(request, 'session'):
            self.session_interface.save_session(self, request.session, response)
            
        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
    
    def print_routes(self):
        """打印所有路由信息"""
        print("\n=== 可用接口列表 ===")
        print("方法\t路径\t\t处理函数")
        print("-" * 50)
        
        for rule in self.url_map.iter_rules():
            methods = ','.join(rule.methods)
            endpoint = rule.endpoint
            path = str(rule)
            print(f"{methods}\t{path}\t{endpoint}")
            
        print("\n=== 中间件列表 ===")
        for middleware in self.middlewares:
            print(f"- {middleware.__name__}")
            
        print("\n=== 错误处理器 ===")
        for code, handler in self.error_handlers.items():
            print(f"- {code}: {handler.__name__}")
            
        print("\n=== 其他端点 ===")
        print("- /openapi.json: OpenAPI规范")
        print("- /docs: API文档界面")
        print("-" * 50)
    
    def run(self, host='127.0.0.1', port=5000, debug=True):
        self.print_routes()
        run_simple(host, port, self, use_debugger=debug, use_reloader=debug)

class FileSystemSessionInterface:
    """基于文件系统的会话接口"""
    def __init__(self, session_dir='sessions'):
        self.session_dir = session_dir
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
    def open_session(self, app, request):
        sid = request.cookies.get('session_id')
        if not sid:
            return None
            
        session_file = os.path.join(self.session_dir, sid)
        if not os.path.exists(session_file):
            return None
            
        try:
            with open(session_file, 'rb') as f:
                data = pickle.load(f)
                if data.get('expires', 0) < time.time():
                    os.remove(session_file)
                    return None
                return Session(data.get('data', {}))
        except:
            return None
            
    def save_session(self, app, session, response):
        if not session.modified:
            return
            
        sid = os.urandom(16).hex()
        session_file = os.path.join(self.session_dir, sid)
        
        data = {
            'data': session.data,
            'expires': time.time() + 3600  # 1小时过期
        }
        
        with open(session_file, 'wb') as f:
            pickle.dump(data, f)
            
        response.set_cookie('session_id', sid, max_age=3600)
        
    def make_null_session(self, app):
        return Session() 