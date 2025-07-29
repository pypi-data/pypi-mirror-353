import os
import time
import threading
import argparse
import json
import base64
import asyncio
from flask import Flask, session, request, jsonify, send_file, render_template, redirect, url_for, send_from_directory
from PIL import ImageGrab, Image
import cv2
import numpy as np
from datetime import datetime
import websockets

# 获取包的安装路径
if __name__ == '__main__':
    # 直接运行时使用当前路径
    PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    # 作为包导入时使用包路径
    PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'classmate')


# 创建数据目录（统一存储在库目录下）
UPLOAD_DIR = os.path.join(PACKAGE_DIR, 'uploads')  # 共享文件
ASSIGNMENTS_DIR = os.path.join(PACKAGE_DIR, 'assignments')  # 作业文件
TRANSFER_DIR = os.path.join(PACKAGE_DIR, 'transfer')  # 中转站文件
BROADCAST_PACKAGES_DIR = os.path.join(PACKAGE_DIR, 'broadcast_packages')  # 广播数据包

# 确保所有必要的目录都存在
for directory in [UPLOAD_DIR, ASSIGNMENTS_DIR, TRANSFER_DIR, BROADCAST_PACKAGES_DIR]:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"确保目录存在: {directory}")
        # 检查目录权限
        if not os.access(directory, os.W_OK):
            print(f"警告：目录没有写入权限: {directory}")
    except Exception as e:
        print(f"创建目录失败 {directory}: {str(e)}")

# 创建Flask应用，使用包内的模板和静态文件
app = Flask(__name__, 
    static_folder=os.path.join(PACKAGE_DIR, 'static'),
    template_folder=os.path.join(PACKAGE_DIR, 'templates'))
app.secret_key = os.urandom(24)

# 全局变量
TEACHER_PASSWORD = "123456"  # 默认密码，可以通过命令行参数修改
client_images = {}         # {client_id: [(timestamp, image_bytes), ...]}
client_last_active = {}    # {client_id: last_active_time}
upload_history = {}        # {ip: [(timestamp, filename), ...]}
is_broadcasting = False    # 是否正在广播
current_broadcast_folder = None  # 当前广播保存的文件夹
use_camera = False
active_websockets = set()  # 活跃的WebSocket连接
ws_server = None  # WebSocket服务器实例
connected_clients = set()
broadcast_task = None
broadcast_history = []       # [(timestamp, image_data), ...]
MAX_HISTORY_SIZE = 1000     # 最大历史记录数量
broadcast_packages = {}      # {package_id: {'name': name, 'timestamp': timestamp, 'frames': frames}}

print('可以通过classmate.run(password="123456")以指定密码')

# 初始化摄像头
cap = cv2.VideoCapture(0)
has_camera = cap.isOpened()
if not has_camera:
    print("警告：未检测到摄像头")
    cap.release()

def capture_screen():
    """捕获屏幕画面"""
    screenshot = ImageGrab.grab()
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame

def capture_camera():
    """捕获摄像头画面"""
    if not has_camera:
        print("摄像头不可用")
        return None
    ret, frame = cap.read()
    if not ret:
        print("摄像头读取失败")
        return None
    return frame

def is_teacher():
    """检查当前用户是否为教师"""
    return session.get('is_teacher', False)

def check_upload_limit(ip):
    """检查上传频率限制"""
    now = time.time()
    if ip not in upload_history:
        upload_history[ip] = []
    
    # 清理30秒前的记录
    upload_history[ip] = [(t, f) for t, f in upload_history[ip] if now - t < 30]
    
    # 检查30秒内是否超过5次上传
    if len(upload_history[ip]) >= 5:
        return False
    return True

def add_upload_record(ip, filename):
    """添加上传记录"""
    if ip not in upload_history:
        upload_history[ip] = []
    upload_history[ip].append((time.time(), filename))

def get_folder_size(folder):
    """获取文件夹大小"""
    total = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            total += os.path.getsize(fp)
    return total

def cleanup_folder(folder, max_size=500*1024*1024):
    """清理文件夹，保持大小在限制内"""
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.jpg')]
    files = [(f, os.path.getmtime(f)) for f in files]
    files.sort(key=lambda x: x[1])  # 按修改时间升序
    while get_folder_size(folder) > max_size and files:
        os.remove(files[0][0])
        files.pop(0)

def cleanup_inactive_clients():
    """清理不活跃的客户端"""
    while True:
        now = time.time()
        for client_id in list(client_last_active):
            if now - client_last_active[client_id] > 3600:
                client_images.pop(client_id, None)
                client_last_active.pop(client_id, None)
        time.sleep(600)

def get_folder_by_type(file_type):
    """根据文件类型获取对应的文件夹路径"""
    if file_type == 'transfer':
        return TRANSFER_DIR
    elif file_type == 'assignment':
        return ASSIGNMENTS_DIR
    else:
        return UPLOAD_DIR

# Flask路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')



@app.route('/login', methods=['POST'])
def login():
    """教师登录"""
    password = request.form.get('password')
    if password == TEACHER_PASSWORD:
        session['is_teacher'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '密码错误'})

@app.route('/logout')
def logout():
    """教师登出"""
    session.pop('is_teacher', None)
    return redirect(url_for('index'))

@app.route('/api/files')
def list_files():
    """获取文件列表"""
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, filename)
        files.append({
            'name': filename,
            'size': os.path.getsize(path),
            'upload_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(path))),
            'type': 'shared'  # 添加文件类型
        })
    return jsonify(files)

@app.route('/api/transfer_files')
def list_transfer_files():
    """获取中转站文件列表"""
    files = []
    # 获取共享文件
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'shared'
            })
    
    # 获取中转站文件
    for filename in os.listdir(TRANSFER_DIR):
        filepath = os.path.join(TRANSFER_DIR, filename)
        if os.path.isfile(filepath):
            files.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'transfer'
            })
    return jsonify(files)

@app.route('/api/assignments')
def list_assignments():
    if not session.get('is_teacher'):
        return jsonify({'error': '未授权'}), 403
    
    assignments = []
    for filename in os.listdir(ASSIGNMENTS_DIR):
        filepath = os.path.join(ASSIGNMENTS_DIR, filename)
        if os.path.isfile(filepath):
            assignments.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(assignments)

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            print("错误：请求中没有文件")
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("错误：文件名为空")
            return jsonify({'error': '没有选择文件'}), 400
        
        # 获取原始文件名
        original_filename = file.filename
        print(f"原始文件名: {original_filename}")
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        print(f"文件大小: {file_size} 字节")
        
        if file_size > 1000 * 1024 * 1024:  # 1000MB限制
            print(f"错误：文件过大 ({file_size} 字节)")
            return jsonify({'error': '文件大小超过限制（1000MB）'}), 400
        
        # 获取文件类型
        file_type = request.form.get('type', 'shared')
        print(f"文件类型: {file_type}")
        
        # 根据文件类型选择保存目录
        if file_type == 'assignment':
            save_dir = ASSIGNMENTS_DIR
            print(f"保存到作业目录: {save_dir}")
        elif file_type == 'transfer':
            save_dir = TRANSFER_DIR
            print(f"保存到中转站目录: {save_dir}")
        else:
            save_dir = UPLOAD_DIR
            print(f"保存到共享目录: {save_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(save_dir):
            print(f"错误：目录不存在 {save_dir}")
            os.makedirs(save_dir, exist_ok=True)
            print(f"已创建目录: {save_dir}")
        
        # 使用原始文件名保存
        filepath = os.path.join(save_dir, original_filename)
        print(f"保存路径: {filepath}")
        
        # 检查文件是否已存在
        if os.path.exists(filepath):
            print(f"警告：文件已存在，将被覆盖: {filepath}")
        
        # 保存文件
        try:
            file.save(filepath)
            print(f"文件保存成功: {filepath}")
            # 验证文件是否真的保存成功
            if os.path.exists(filepath):
                print(f"文件确实已保存: {filepath}")
                print(f"文件大小: {os.path.getsize(filepath)} 字节")
            else:
                print(f"警告：文件保存后不存在: {filepath}")
            return jsonify({'message': '文件上传成功'})
        except Exception as save_error:
            print(f"保存文件时出错: {str(save_error)}")
            return jsonify({'error': f'保存文件失败: {str(save_error)}'}), 500
            
    except Exception as e:
        print(f"上传文件时发生错误: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/delete_file/<path:filename>')
def delete_file(filename):
    """删除文件"""
    try:
        print(f"开始删除文件: {filename}")
        
        # 获取文件类型
        file_type = request.args.get('type', 'shared')
        print(f"文件类型: {file_type}")
        
        # 检查权限
        if file_type == 'shared' and not session.get('is_teacher'):
            print("错误：无权限删除共享文件")
            return jsonify({'error': '无权限删除共享文件'}), 403
        
        # 获取对应的文件夹
        folder = get_folder_by_type(file_type)
        print(f"目标文件夹: {folder}")
        
        # 检查文件夹是否存在
        if not os.path.exists(folder):
            print(f"错误：文件夹不存在 {folder}")
            return jsonify({'error': '文件夹不存在'}), 404
        
        # 构建完整的文件路径
        file_path = os.path.join(folder, filename)
        print(f"完整文件路径: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件不存在 {file_path}")
            # 尝试在其他目录中查找
            for other_dir in [UPLOAD_DIR, ASSIGNMENTS_DIR, TRANSFER_DIR]:
                if other_dir != folder:
                    other_path = os.path.join(other_dir, filename)
                    if os.path.exists(other_path):
                        print(f"文件在其他目录中找到: {other_path}")
                        file_path = other_path
                        break
            else:
                return jsonify({'error': '文件不存在'}), 404
        
        # 检查文件权限
        if not os.access(file_path, os.W_OK):
            print(f"错误：没有文件写入权限 {file_path}")
            return jsonify({'error': '没有文件写入权限'}), 403
        
        # 获取文件信息（用于日志）
        file_size = os.path.getsize(file_path)
        file_mtime = os.path.getmtime(file_path)
        print(f"文件大小: {file_size} 字节")
        print(f"最后修改时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_mtime))}")
        
        # 尝试删除文件
        try:
            os.remove(file_path)
            print(f"文件删除成功: {file_path}")
            # 验证文件是否真的被删除
            if not os.path.exists(file_path):
                print(f"文件确实已被删除: {file_path}")
            else:
                print(f"警告：文件删除后仍然存在: {file_path}")
            return jsonify({'message': '文件删除成功'})
        except PermissionError:
            print(f"错误：删除文件时权限不足 {file_path}")
            return jsonify({'error': '删除文件时权限不足'}), 403
        except OSError as e:
            print(f"错误：删除文件时系统错误 {file_path}: {str(e)}")
            return jsonify({'error': f'删除文件时系统错误: {str(e)}'}), 500
            
    except Exception as e:
        print(f"删除文件时发生未知错误: {str(e)}")
        return jsonify({'error': f'删除文件失败: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # 检查文件是否存在于任何目录中
        for directory in [UPLOAD_DIR, ASSIGNMENTS_DIR, TRANSFER_DIR]:
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                return send_from_directory(directory, filename, as_attachment=True)
        return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'文件下载失败: {str(e)}'}), 500

@app.route('/api/broadcast_packages')
def list_broadcast_packages():
    """获取广播数据包列表"""
    packages = []
    for filename in os.listdir(BROADCAST_PACKAGES_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(BROADCAST_PACKAGES_DIR, filename), 'r', encoding='utf-8') as f:
                    package_info = json.load(f)
                    packages.append({
                        'id': package_info['id'],
                        'name': package_info['name'],
                        'timestamp': package_info['timestamp'],
                        'frame_count': len(package_info['frames'])
                    })
            except Exception as e:
                print(f"读取广播数据包失败: {e}")
    
    # 按时间戳降序排序
    packages.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(packages)

@app.route('/api/broadcast_package/<package_id>')
def get_broadcast_package(package_id):
    """获取指定广播数据包的内容"""
    try:
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        if os.path.exists(package_file):
            with open(package_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({'error': '数据包不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_broadcast_package/<package_id>')
def delete_broadcast_package(package_id):
    """删除广播数据包"""
    try:
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        if os.path.exists(package_file):
            os.remove(package_file)
            if package_id in broadcast_packages:
                del broadcast_packages[package_id]
            return jsonify({'success': True})
        return jsonify({'error': '数据包不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files')
def get_files():
    try:
        files = []
        # 获取所有目录中的文件
        for directory in [UPLOAD_DIR, ASSIGNMENTS_DIR, TRANSFER_DIR]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        files.append({
                            'name': filename,
                            'size': os.path.getsize(filepath),
                            'type': 'file'
                        })
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/api/assignments_dir')
def get_assignments_dir():
    """返回作业文件目录的路径"""
    return jsonify({'assignments_dir': ASSIGNMENTS_DIR})

# WebSocket处理
class WebSocketHandler:
    def __init__(self):
        self.clients = set()
        self.broadcast_task = None
        self.current_package_id = None
        self.has_camera = has_camera
        self.teacher_clients = set()  # 存储教师客户端的WebSocket连接
        self.client_display_modes = {}  # 存储客户端的显示模式 {websocket: 'original'|'fullscreen'}
        print("WebSocket处理器已初始化")
        # 加载所有广播数据包
        self.load_all_packages()

    def load_all_packages(self):
        """加载所有广播数据包"""
        print("开始加载所有广播数据包")
        broadcast_packages.clear()  # 清空现有包
        
        for filename in os.listdir(BROADCAST_PACKAGES_DIR):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(BROADCAST_PACKAGES_DIR, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        package_info = json.load(f)
                        broadcast_packages[package_info['id']] = package_info
                        print(f"已加载广播包: {package_info['name']}")
                except Exception as e:
                    print(f"加载广播数据包失败 {filename}: {e}")
        
        print(f"广播包加载完成，共 {len(broadcast_packages)} 个包")

    async def register(self, websocket):
        self.clients.add(websocket)
        self.client_display_modes[websocket] = 'original'  # 默认使用原始大小
        print(f"新客户端连接，当前连接数: {len(self.clients)}")
        try:
            # 发送当前广播状态和摄像头状态
            await websocket.send(json.dumps({
                'type': 'broadcast_status',
                'status': 'started' if is_broadcasting else 'stopped',
                'has_camera': self.has_camera
            }))
            
            # 发送所有广播数据包列表
            await websocket.send(json.dumps({
                'type': 'packages_list',
                'packages': list(broadcast_packages.values())
            }))
            
            # 发送当前广播的历史记录
            if broadcast_history:
                await websocket.send(json.dumps({
                    'type': 'history',
                    'history': broadcast_history
                }))
        except Exception as e:
            print(f"发送状态和历史记录失败: {e}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        self.client_display_modes.pop(websocket, None)
        print(f"客户端断开连接，当前连接数: {len(self.clients)}")

    async def broadcast_images(self):
        global is_broadcasting, use_camera
        print("开始广播任务")
        while is_broadcasting:
            try:
                # 捕获图像
                if use_camera:
                    frame = capture_camera()
                else:
                    frame = capture_screen()
                
                if frame is not None:
                    # 压缩图片
                    frame = cv2.resize(frame, (1280, 720))
                    _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    img_b64 = base64.b64encode(buf).decode()
                    timestamp = int(time.time() * 1000)
                    
                    # 添加到历史记录
                    broadcast_history.append({
                        'timestamp': timestamp,
                        'image': img_b64
                    })
                    if len(broadcast_history) > MAX_HISTORY_SIZE:
                        broadcast_history.pop(0)
                    
                    # 广播给所有客户端
                    websockets_to_remove = set()
                    for client in self.clients:
                        try:
                            message = json.dumps({
                                'type': 'image',
                                'image': img_b64,
                                'timestamp': timestamp,
                                'display_mode': self.client_display_modes.get(client, 'original')
                            })
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            websockets_to_remove.add(client)
                        except Exception as e:
                            print(f"发送消息失败: {e}")
                            websockets_to_remove.add(client)
                    
                    # 移除断开的连接
                    for client in websockets_to_remove:
                        await self.unregister(client)
                else:
                    print("图像捕获失败")
                
                await asyncio.sleep(0.1)  # 10 FPS
            except Exception as e:
                print(f"广播错误: {e}")
                await asyncio.sleep(1)
        print("广播任务结束")

    async def save_broadcast_package(self):
        """保存当前广播数据包"""
        if not broadcast_history:
            print("没有广播历史记录，不保存数据包")
            return None
            
        package_id = str(int(time.time()))
        package_name = f"广播_{time.strftime('%Y%m%d_%H%M%S')}"
        
        print(f"开始保存广播数据包: {package_name}")
        print(f"历史记录长度: {len(broadcast_history)}")
        
        # 保存数据包信息
        package_info = {
            'id': package_id,
            'name': package_name,
            'timestamp': int(time.time() * 1000),
            'frames': broadcast_history.copy()
        }
        
        # 保存到文件
        package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
        try:
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(package_info, f, ensure_ascii=False)
            print(f"广播数据包已保存: {package_file}")
            
            # 更新内存中的包列表
            broadcast_packages[package_id] = package_info
            print(f"当前广播包数量: {len(broadcast_packages)}")
            
            # 重新加载所有包
            self.load_all_packages()
            print("已重新加载所有广播包")
            
            return package_id
        except Exception as e:
            print(f"保存广播数据包失败: {e}")
            return None

    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # 处理显示模式切换
                    if data['type'] == 'set_display_mode':
                        self.client_display_modes[websocket] = data['mode']
                        continue
                    
                    # 处理教师登录
                    if data['type'] == 'teacher_login':
                        if data['password'] == TEACHER_PASSWORD:
                            self.teacher_clients.add(websocket)
                            await websocket.send(json.dumps({
                                'type': 'login_result',
                                'success': True
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'type': 'login_result',
                                'success': False,
                                'message': '密码错误'
                            }))
                    
                    # 处理教师登出
                    elif data['type'] == 'teacher_logout':
                        self.teacher_clients.discard(websocket)
                        await websocket.send(json.dumps({
                            'type': 'logout_result',
                            'success': True
                        }))
                    
                    # 处理广播相关操作
                    elif data['type'] == 'start_broadcast':
                        if websocket in self.teacher_clients:
                            global is_broadcasting, broadcast_history
                            if not is_broadcasting:
                                is_broadcasting = True
                                broadcast_history = []
                                if self.broadcast_task is None:
                                    self.broadcast_task = asyncio.create_task(self.broadcast_images())
                                await self.broadcast_status_change('started')
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限开始广播'
                            }))
                    
                    elif data['type'] == 'stop_broadcast':
                        if websocket in self.teacher_clients:
                            if is_broadcasting:
                                is_broadcasting = False
                                if self.broadcast_task:
                                    self.broadcast_task.cancel()
                                    self.broadcast_task = None
                                package_id = await self.save_broadcast_package()
                                if package_id:
                                    await self.broadcast_package_saved(package_id)
                                await self.broadcast_status_change('stopped')
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限停止广播'
                            }))
                    
                    elif data['type'] == 'switch_source':
                        if websocket in self.teacher_clients:
                            global use_camera
                            if data['use_camera'] and not self.has_camera:
                                await websocket.send(json.dumps({
                                    'type': 'error',
                                    'message': '摄像头不可用'
                                }))
                                continue
                            use_camera = data['use_camera']
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限切换视频源'
                            }))
                    
                    # 处理重命名广播数据包
                    elif data['type'] == 'rename_package':
                        if websocket in self.teacher_clients:
                            package_id = data['package_id']
                            new_name = data['new_name']
                            package_file = os.path.join(BROADCAST_PACKAGES_DIR, f"{package_id}.json")
                            
                            if os.path.exists(package_file):
                                try:
                                    # 读取现有包信息
                                    with open(package_file, 'r', encoding='utf-8') as f:
                                        package_info = json.load(f)
                                    
                                    # 更新包名称
                                    package_info['name'] = new_name
                                    
                                    # 保存更新后的包信息
                                    with open(package_file, 'w', encoding='utf-8') as f:
                                        json.dump(package_info, f, ensure_ascii=False)
                                    
                                    # 更新内存中的包信息
                                    broadcast_packages[package_id] = package_info
                                    
                                    # 通知所有客户端包已重命名
                                    await self.broadcast_package_renamed(package_id, new_name)
                                except Exception as e:
                                    print(f"重命名广播数据包失败: {e}")
                                    await websocket.send(json.dumps({
                                        'type': 'error',
                                        'message': '重命名失败'
                                    }))
                            else:
                                await websocket.send(json.dumps({
                                    'type': 'error',
                                    'message': '数据包不存在'
                                }))
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': '无权限重命名广播数据包'
                            }))
                    
                except json.JSONDecodeError:
                    print("无效的JSON消息")
                except Exception as e:
                    print(f"处理消息错误: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        finally:
            self.teacher_clients.discard(websocket)
            await self.unregister(websocket)

    async def broadcast_package_saved(self, package_id):
        """通知所有客户端广播数据包已保存"""
        message = json.dumps({
            'type': 'package_saved',
            'package_id': package_id,
            'package_info': broadcast_packages[package_id]
        })
        await self.broadcast_to_all(message)

    async def broadcast_package_renamed(self, package_id, new_name):
        """通知所有客户端广播数据包已重命名"""
        message = json.dumps({
            'type': 'package_renamed',
            'package_id': package_id,
            'new_name': new_name
        })
        await self.broadcast_to_all(message)

    async def broadcast_package_deleted(self, package_id):
        """通知所有客户端广播数据包已删除"""
        message = json.dumps({
            'type': 'package_deleted',
            'package_id': package_id
        })
        await self.broadcast_to_all(message)

    async def broadcast_to_all(self, message):
        """向所有客户端广播消息"""
        websockets_to_remove = set()
        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                print(f"发送消息失败: {e}")
                websockets_to_remove.add(client)
        
        # 移除断开的连接
        for client in websockets_to_remove:
            await self.unregister(client)

    async def broadcast_status_change(self, status):
        """广播状态变化给所有客户端"""
        message = json.dumps({
            'type': 'broadcast_status',
            'status': status
        })
        websockets_to_remove = set()
        for client in self.clients:
            try:
                await client.send(message)
            except Exception as e:
                print(f"发送状态变化失败: {e}")
                websockets_to_remove.add(client)
        
        # 移除断开的连接
        for client in websockets_to_remove:
            await self.unregister(client)

# 创建WebSocket处理器实例
handler = WebSocketHandler()

async def websocket_handler(websocket, path):
    await handler.handle_client(websocket, path)

async def broadcast_thread():
    """广播线程"""
    while True:
        if is_broadcasting and active_websockets:
            # 根据模式选择捕获方式
            if use_camera:
                frame = capture_camera()
            else:
                frame = capture_screen()
            
            if frame is not None:
                # 压缩图片
                frame = cv2.resize(frame, (1280, 720))
                _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                img_b64 = base64.b64encode(buf).decode()
                
                # 广播给所有客户端
                message = {
                    'type': 'image',
                    'image': img_b64
                }
                for ws in active_websockets.copy():
                    try:
                        await ws.send_message(message)
                    except:
                        active_websockets.discard(ws)
        
        await asyncio.sleep(1)  # 控制发送频率

async def start_websocket_server(host, port):
    """启动WebSocket服务器"""
    print(f"启动WebSocket服务器: ws://{host}:{port}")
    server = await websockets.serve(handler.handle_client, host, port)
    await server.wait_closed()

def run_flask_server(host, port):
    """运行Flask服务器"""
    app.run(host=host, port=port)

def run(host='0.0.0.0', port=5000, password=None):
    """运行服务器
    
    参数:
        host (str): 服务器主机地址
        port (int): 服务器端口
        password (str): 教师模式密码
    """
    global TEACHER_PASSWORD
    if password:
        TEACHER_PASSWORD = password
    
    # 启动WebSocket服务器
    ws_port = port + 1
    print(f"WebSocket服务器端口: {ws_port}")
    print(f"数据存储目录: {PACKAGE_DIR}")
    
    try:
        # 创建事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 在新线程中运行WebSocket服务器
        ws_thread = threading.Thread(target=lambda: loop.run_until_complete(start_websocket_server(host, ws_port)))
        ws_thread.daemon = True
        ws_thread.start()
        
        print(f"Classmate 服务器已启动")
        print(f"HTTP 服务器地址: http://{host}:{port}")
        print(f"WebSocket 服务器地址: ws://{host}:{ws_port}")
        print(f"教师模式密码: {TEACHER_PASSWORD}")
        
        # 在主线程中运行Flask服务器
        app.run(host=host, port=port)
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
    except Exception as e:
        print(f"服务器运行错误: {e}")
    finally:
        # 清理资源
        if 'loop' in locals():
            loop.close()
        if 'cap' in globals() and cap is not None:
            cap.release()
        print("服务器已关闭")

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='Classmate - 教室管理系统')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    parser.add_argument('--password', type=str, help='教师模式密码')
    args = parser.parse_args()
    
    run(args.host, args.port, args.password)

if __name__ == '__main__':
    
    main() 