// 全局变量
let ws = null;
let isTeacher = localStorage.getItem('isTeacher') === 'true';  // 从localStorage读取教师状态
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

// DOM元素
const teacherModeBtn = document.getElementById('teacherModeBtn');
const logoutBtn = document.getElementById('logoutBtn');
const passwordModal = document.getElementById('passwordModal');
const passwordInput = document.getElementById('passwordInput');
const loginBtn = document.getElementById('loginBtn');
const cancelBtn = document.getElementById('cancelBtn');
const startBroadcastBtn = document.getElementById('startBroadcastBtn');
const stopBroadcastBtn = document.getElementById('stopBroadcastBtn');
const screenSourceBtn = document.getElementById('screenSourceBtn');
const cameraSourceBtn = document.getElementById('cameraSourceBtn');
const broadcastImage = document.getElementById('broadcastImage');
const broadcastStatus = document.querySelector('.broadcast-status');
const broadcastControls = document.querySelector('.broadcast-controls');
const fileControls = document.querySelector('.file-controls');
const transferFileInput = document.getElementById('transferFileInput');
const transferUploadBtn = document.getElementById('transferUploadBtn');
const transferFileTable = document.getElementById('transferFileTable').querySelector('tbody');
const assignmentFileInput = document.getElementById('assignmentFileInput');
const submitAssignmentBtn = document.getElementById('submitAssignmentBtn');
const studentControls = document.getElementById('studentControls');
const viewAssignmentsBtn = document.getElementById('viewAssignmentsBtn');
const toggleDisplayModeBtn = document.getElementById('toggleDisplayMode');
const fullscreenControls = document.querySelector('.fullscreen-controls');
const prevFrameFullscreen = document.getElementById('prevFrameFullscreen');
const nextFrameFullscreen = document.getElementById('nextFrameFullscreen');
const exitFullscreen = document.getElementById('exitFullscreen');
const historySliderFullscreen = document.getElementById('historySliderFullscreen');
const historyTimeFullscreen = document.getElementById('historyTimeFullscreen');

// 广播数据包管理
let broadcastPackages = [];

// 广播历史记录
let broadcastHistory = [];

// 历史回放相关变量
let currentHistoryIndex = -1;

// 工具函数
function $(selector) {
    return document.querySelector(selector);
}

function $$(selector) {
    return document.querySelectorAll(selector);
}

function showElement(element) {
    if (element) {
        element.style.display = 'block';
    }
}

function hideElement(element) {
    if (element) {
        element.style.display = 'none';
    }
}

function toggleElement(element) {
    element.style.display = element.style.display === 'none' ? '' : 'none';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 加载广播数据包列表
async function loadBroadcastPackages() {
    try {
        const response = await fetch('/api/broadcast_packages');
        broadcastPackages = await response.json();
        updatePackageList();
    } catch (error) {
        console.error('加载广播数据包列表错误:', error);
    }
}

// 更新广播数据包列表
function updatePackageList() {
    const packageList = document.getElementById('packageList');
    packageList.innerHTML = '';
    
    console.log('更新广播包列表，教师状态:', isTeacher);  // 添加调试日志
    
    broadcastPackages.forEach(package => {
        const div = document.createElement('div');
        div.className = 'package-item';
        div.innerHTML = `
            <div class="package-info">
                <span class="package-name">${package.name}</span>
                <span class="package-time">${new Date(package.timestamp).toLocaleString()}</span>
            </div>
            <div class="package-actions">
                ${isTeacher ? `
                    <button class="btn" onclick="renamePackage('${package.id}')">重命名</button>
                    <button class="btn danger" onclick="deletePackage('${package.id}')">删除</button>
                ` : `
                    <button class="btn" onclick="loadPackage('${package.id}')">查看</button>
                `}
            </div>
        `;
        packageList.appendChild(div);
    });
}

// 显示模式切换
function toggleDisplayMode() {
    const currentMode = broadcastImage.classList.contains('fullscreen') ? 'original' : 'fullscreen';
    broadcastImage.classList.toggle('fullscreen');
    
    // 显示/隐藏全屏控制界面
    if (currentMode === 'fullscreen') {
        fullscreenControls.classList.add('show');
        hideElement(studentControls);
    } else {
        fullscreenControls.classList.remove('show');
        showElement(studentControls);
    }
    
    // 发送显示模式到服务器
    if (ws) {
        ws.send(JSON.stringify({
            type: 'set_display_mode',
            mode: currentMode
        }));
    }
}

// 绑定显示模式切换按钮事件
toggleDisplayModeBtn.addEventListener('click', toggleDisplayMode);

// 更新广播图像显示
function updateBroadcastImage(imageData, displayMode) {
    if (!imageData) return;
    
    broadcastImage.src = `data:image/jpeg;base64,${imageData}`;
    broadcastImage.style.display = 'block';
    
    // 如果是教师端，默认使用原始大小
    if (isTeacher) {
        displayMode = 'original';
    }
    
    if (displayMode === 'fullscreen') {
        broadcastImage.classList.add('fullscreen');
        fullscreenControls.classList.add('show');
        hideElement(studentControls);
    } else {
        broadcastImage.classList.remove('fullscreen');
        fullscreenControls.classList.remove('show');
        showElement(studentControls);
    }
}

// 加载广播数据包
async function loadPackage(packageId) {
    try {
        const response = await fetch(`/api/broadcast_package/${packageId}`);
        const package = await response.json();
        
        // 更新历史记录
        broadcastHistory = package.frames;
        updateHistorySlider();
        
        // 显示第一帧
        if (broadcastHistory.length > 0) {
            const firstFrame = broadcastHistory[0];
            updateBroadcastImage(firstFrame.image, 'original');
            
            const date = new Date(firstFrame.timestamp);
            document.getElementById('historyTime').textContent = date.toLocaleTimeString();
            
            // 显示学生控制界面
            showElement(studentControls);
            hideElement(broadcastControls);
        }
    } catch (error) {
        console.error('加载广播数据包错误:', error);
        alert('加载失败，请重试');
    }
}

// 重命名广播数据包
async function renamePackage(packageId) {
    if (!isTeacher) {
        alert('无权限重命名广播数据包');
        return;
    }
    
    const package = broadcastPackages.find(p => p.id === packageId);
    if (!package) return;
    
    const newName = prompt('请输入新的名称:', package.name);
    if (!newName || newName === package.name) return;
    
    try {
        ws.send(JSON.stringify({
            type: 'rename_package',
            package_id: packageId,
            new_name: newName
        }));
        
        // 立即更新本地显示
        package.name = newName;
        updatePackageList();
    } catch (error) {
        console.error('重命名广播数据包错误:', error);
        alert('重命名失败，请重试');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 教师模式开关
    teacherModeBtn.addEventListener('click', showPasswordModal);
    logoutBtn.addEventListener('click', logout);
    
    // 登录
    loginBtn.addEventListener('click', login);
    cancelBtn.addEventListener('click', hidePasswordModal);
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') login();
    });
    
    // 广播控制
    startBroadcastBtn.addEventListener('click', startBroadcast);
    stopBroadcastBtn.addEventListener('click', stopBroadcast);
    screenSourceBtn.addEventListener('click', () => switchSource(false));
    cameraSourceBtn.addEventListener('click', () => switchSource(true));
    
    // 文件上传 - 使用一次性事件监听器
    transferUploadBtn.onclick = () => transferFileInput.click();
    transferFileInput.onchange = uploadTransferFile;
    
    // 作业相关
    submitAssignmentBtn.onclick = () => assignmentFileInput.click();
    assignmentFileInput.onchange = submitAssignment;
    viewAssignmentsBtn.addEventListener('click', viewAssignments);

    // 历史记录滑块
    const historySlider = document.getElementById('historySlider');
    historySlider.addEventListener('input', () => {
        const index = parseInt(historySlider.value);
        if (index >= 0 && index < broadcastHistory.length) {
            const frame = broadcastHistory[index];
            updateBroadcastImage(frame.image, 'original');
            
            const date = new Date(frame.timestamp);
            document.getElementById('historyTime').textContent = date.toLocaleTimeString();
        }
    });

    // 全屏控制
    exitFullscreen.addEventListener('click', () => {
        broadcastImage.classList.remove('fullscreen');
        fullscreenControls.classList.remove('show');
        showElement(studentControls);
    });

    prevFrameFullscreen.addEventListener('click', () => {
        const slider = document.getElementById('historySliderFullscreen');
        const newValue = Math.max(0, parseInt(slider.value) - 1);
        slider.value = newValue;
        if (broadcastHistory.length > 0) {
            const frame = broadcastHistory[newValue];
            updateBroadcastImage(frame.image, 'fullscreen');
            const date = new Date(frame.timestamp);
            historyTimeFullscreen.textContent = date.toLocaleTimeString();
        }
    });

    nextFrameFullscreen.addEventListener('click', () => {
        const slider = document.getElementById('historySliderFullscreen');
        const newValue = Math.min(broadcastHistory.length - 1, parseInt(slider.value) + 1);
        slider.value = newValue;
        if (broadcastHistory.length > 0) {
            const frame = broadcastHistory[newValue];
            updateBroadcastImage(frame.image, 'fullscreen');
            const date = new Date(frame.timestamp);
            historyTimeFullscreen.textContent = date.toLocaleTimeString();
        }
    });

    historySliderFullscreen.addEventListener('input', () => {
        const index = parseInt(historySliderFullscreen.value);
        if (index >= 0 && index < broadcastHistory.length) {
            const frame = broadcastHistory[index];
            updateBroadcastImage(frame.image, 'fullscreen');
            const date = new Date(frame.timestamp);
            historyTimeFullscreen.textContent = date.toLocaleTimeString();
        }
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    connectWebSocket();
    loadTransferFiles();
    loadBroadcastPackages();
    
    // 如果已经是教师身份，更新UI
    if (isTeacher) {
        updateTeacherUI(true);
    }
});

// WebSocket连接
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:${parseInt(window.location.port) + 1}`;
    
    console.log('正在连接WebSocket:', wsUrl);
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket连接已建立');
        reconnectAttempts = 0;
    };
    
    ws.onclose = () => {
        console.log('WebSocket连接已关闭');
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            console.log(`尝试重新连接 (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
            setTimeout(connectWebSocket, RECONNECT_DELAY);
            reconnectAttempts++;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        } catch (error) {
            console.error('处理WebSocket消息错误:', error);
        }
    };
}

// 显示密码输入对话框
function showPasswordModal() {
    passwordModal.classList.add('show');
    passwordInput.focus();
}

// 关闭密码输入对话框
function hidePasswordModal() {
    passwordModal.classList.remove('show');
    passwordInput.value = '';
}

// 教师登录
async function login() {
    const password = passwordInput.value;
    if (!password) return;
    
    try {
        // 通过 WebSocket 发送登录请求
        ws.send(JSON.stringify({
            type: 'teacher_login',
            password: password
        }));
    } catch (error) {
        console.error('登录错误:', error);
        alert('登录失败，请重试');
    }
}

// 教师登出
async function logout() {
    try {
        // 通过 WebSocket 发送登出请求
        ws.send(JSON.stringify({
            type: 'teacher_logout'
        }));
        // 清除本地存储的教师身份
        localStorage.removeItem('isTeacher');
        isTeacher = false;
        updateTeacherUI(false);
    } catch (error) {
        console.error('登出错误:', error);
    }
}

// 更新教师界面
function updateTeacherUI(isTeacher) {
    if (isTeacher) {
        hideElement(teacherModeBtn);
        showElement(logoutBtn);
        showElement(broadcastControls);
        hideElement(studentControls);
        showElement(fileControls);
        showElement(viewAssignmentsBtn);
        // 保存教师身份到localStorage
        localStorage.setItem('isTeacher', 'true');
    } else {
        showElement(teacherModeBtn);
        hideElement(logoutBtn);
        hideElement(broadcastControls);
        showElement(studentControls);
        hideElement(fileControls);
        hideElement(viewAssignmentsBtn);
        // 清除localStorage中的教师身份
        localStorage.removeItem('isTeacher');
    }
}

async function loadTransferFiles() {
    try {
        const response = await fetch('/api/transfer_files');
        const files = await response.json();
        
        transferFileTable.innerHTML = '';
        files.forEach(file => {
            // 显示共享文件和中转站文件
            if (file.type === 'shared' || file.type === 'transfer') {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${file.name}</td>
                    <td>${formatFileSize(file.size)}</td>
                    <td>${file.upload_time}</td>
                    <td>
                        <button class="btn" onclick="downloadTransferFile('${file.name}')">下载</button>
                        <button class="btn danger" onclick="deleteTransferFile('${file.name}')">删除</button>
                    </td>
                `;
                transferFileTable.appendChild(tr);
            }
        });
    } catch (error) {
        console.error('加载中转站文件列表错误:', error);
    }
}

async function uploadTransferFile() {
    const file = transferFileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'transfer');
    formData.append('original_filename', file.name);  // 添加原始文件名
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        if (data.message) {
            transferFileInput.value = '';
            loadTransferFiles();
        } else {
            alert(data.error || '上传失败');
        }
    } catch (error) {
        console.error('上传文件错误:', error);
        alert('上传失败，请重试');
    }
}

async function submitAssignment() {
    const file = assignmentFileInput.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'assignment');
    formData.append('original_filename', file.name);  // 添加原始文件名
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        if (data.message) {
            assignmentFileInput.value = '';
            alert('作业提交成功');
        } else {
            alert(data.error || '提交失败');
        }
    } catch (error) {
        console.error('提交作业错误:', error);
        alert('提交失败，请重试');
    }
}

// 下载文件
function downloadTransferFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}?type=transfer`;
}

// 删除中转站文件
async function deleteTransferFile(filename) {
    if (!confirm('确定要删除这个文件吗？')) return;
    
    try {
        const response = await fetch(`/delete_file/${encodeURIComponent(filename)}?type=transfer`);
        const data = await response.json();
        if (data.message) {
            loadTransferFiles();
        } else {
            alert(data.error || '删除失败');
        }
    } catch (error) {
        console.error('删除文件错误:', error);
        alert('删除失败，请重试');
    }
}

// 删除共享文件
async function deleteSharedFile(filename) {
    if (!isTeacher) {
        alert('无权限删除共享文件');
        return;
    }
    
    if (!confirm('确定要删除这个文件吗？')) return;
    
    try {
        const response = await fetch(`/delete_file/${encodeURIComponent(filename)}?type=shared`);
        const data = await response.json();
        if (data.message) {
            loadTransferFiles();
        } else {
            alert(data.error || '删除失败');
        }
    } catch (error) {
        console.error('删除文件错误:', error);
        alert('删除失败，请重试');
    }
}

// 切换视频源
function switchSource(useCamera) {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    
    // 如果尝试使用摄像头但按钮被禁用，直接返回
    if (useCamera && cameraSourceBtn.disabled) {
        return;
    }
    
    // 更新按钮状态
    if (useCamera) {
        screenSourceBtn.classList.remove('active');
        cameraSourceBtn.classList.add('active');
    } else {
        screenSourceBtn.classList.add('active');
        cameraSourceBtn.classList.remove('active');
    }
    
    console.log('切换视频源:', useCamera ? '摄像头' : '屏幕');
    ws.send(JSON.stringify({ type: 'switch_source', use_camera: useCamera }));
}

// 开始广播
function startBroadcast() {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    
    // 清空历史记录
    broadcastHistory = [];
    updateHistorySlider();
    
    console.log('开始广播');
    ws.send(JSON.stringify({ type: 'start_broadcast' }));
}

// 停止广播
function stopBroadcast() {
    if (!ws) {
        console.error('WebSocket未连接');
        return;
    }
    console.log('停止广播');
    ws.send(JSON.stringify({ type: 'stop_broadcast' }));
}

// 更新广播状态
function updateBroadcastStatus(status) {
    const statusElement = document.querySelector('.broadcast-status');
    if (status === 'started') {
        statusElement.textContent = '正在广播';
        statusElement.classList.add('active');
        showElement(broadcastImage);
        showElement(stopBroadcastBtn);
        hideElement(startBroadcastBtn);
    } else {
        statusElement.textContent = '未开始广播';
        statusElement.classList.remove('active');
        hideElement(stopBroadcastBtn);
        showElement(startBroadcastBtn);
    }
}

// 更新历史记录滑块
function updateHistorySlider() {
    const historySlider = document.getElementById('historySlider');
    const historySliderFullscreen = document.getElementById('historySliderFullscreen');
    
    if (broadcastHistory.length > 0) {
        historySlider.max = broadcastHistory.length - 1;
        historySliderFullscreen.max = broadcastHistory.length - 1;
        currentHistoryIndex = 0;
        updateHistoryDisplay();
    }
}

// 更新历史显示
function updateHistoryDisplay() {
    if (currentHistoryIndex >= 0 && currentHistoryIndex < broadcastHistory.length) {
        const frame = broadcastHistory[currentHistoryIndex];
        updateBroadcastImage(frame.image, broadcastImage.classList.contains('fullscreen') ? 'fullscreen' : 'original');
        
        // 更新时间显示
        const timestamp = new Date(frame.timestamp);
        const timeStr = timestamp.toLocaleTimeString();
        document.getElementById('historyTime').textContent = timeStr;
        document.getElementById('historyTimeFullscreen').textContent = timeStr;
        
        // 更新滑块位置
        document.getElementById('historySlider').value = currentHistoryIndex;
        document.getElementById('historySliderFullscreen').value = currentHistoryIndex;
    }
}

// 设置历史回放控制事件监听器
function setupHistoryControls() {
    const prevFrameBtn = document.getElementById('prevFrame');
    const nextFrameBtn = document.getElementById('nextFrame');
    const historySlider = document.getElementById('historySlider');
    const prevFrameFullscreenBtn = document.getElementById('prevFrameFullscreen');
    const nextFrameFullscreenBtn = document.getElementById('nextFrameFullscreen');
    const historySliderFullscreen = document.getElementById('historySliderFullscreen');

    // 上一帧
    prevFrameBtn.addEventListener('click', () => {
        if (currentHistoryIndex > 0) {
            currentHistoryIndex--;
            updateHistoryDisplay();
        }
    });

    // 下一帧
    nextFrameBtn.addEventListener('click', () => {
        if (currentHistoryIndex < broadcastHistory.length - 1) {
            currentHistoryIndex++;
            updateHistoryDisplay();
        }
    });

    // 全屏模式下的上一帧
    prevFrameFullscreenBtn.addEventListener('click', () => {
        if (currentHistoryIndex > 0) {
            currentHistoryIndex--;
            updateHistoryDisplay();
        }
    });

    // 全屏模式下的下一帧
    nextFrameFullscreenBtn.addEventListener('click', () => {
        if (currentHistoryIndex < broadcastHistory.length - 1) {
            currentHistoryIndex++;
            updateHistoryDisplay();
        }
    });

    // 历史时间轴滑动
    historySlider.addEventListener('input', (e) => {
        currentHistoryIndex = parseInt(e.target.value);
        updateHistoryDisplay();
    });

    // 全屏模式下的历史时间轴滑动
    historySliderFullscreen.addEventListener('input', (e) => {
        currentHistoryIndex = parseInt(e.target.value);
        updateHistoryDisplay();
    });
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'login_result':
            if (data.success) {
                hidePasswordModal();
                isTeacher = true;
                updateTeacherUI(true);
                console.log('教师登录成功');
                loadBroadcastPackages();
            } else {
                alert(data.message || '登录失败');
            }
            break;
        case 'logout_result':
            if (data.success) {
                isTeacher = false;
                updateTeacherUI(false);
                loadBroadcastPackages();
            }
            break;
        case 'broadcast_status':
            updateBroadcastStatus(data.status);
            if (data.has_camera === false) {
                cameraSourceBtn.disabled = true;
                cameraSourceBtn.title = '摄像头不可用';
            }
            break;
        case 'image':
            updateBroadcastImage(data.image, data.display_mode);
            break;
        case 'packages_list':
            broadcastPackages = data.packages;
            updatePackageList();
            break;
        case 'package_deleted':
            broadcastPackages = broadcastPackages.filter(p => p.id !== data.package_id);
            updatePackageList();
            break;
        case 'error':
            alert(data.message);
            break;
        case 'package_renamed':
            const package = broadcastPackages.find(p => p.id === data.package_id);
            if (package) {
                package.name = data.new_name;
                updatePackageList();
            }
            break;
        case 'history':
            // 接收历史记录
            broadcastHistory = data.history;
            updateHistorySlider();
            break;
        case 'package_saved':
            // 添加新保存的包到列表
            broadcastPackages.push(data.package_info);
            updatePackageList();
            break;
    }
}

// 删除广播数据包
async function deletePackage(packageId) {
    if (!confirm('确定要删除这个广播数据包吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/delete_broadcast_package/${packageId}`);
        const result = await response.json();
        
        if (result.success) {
            // 从本地列表中移除
            broadcastPackages = broadcastPackages.filter(p => p.id !== packageId);
            updatePackageList();
            
            // 通知服务器
            ws.send(JSON.stringify({
                type: 'package_deleted',
                package_id: packageId
            }));
        } else {
            alert(result.error || '删除失败');
        }
    } catch (error) {
        console.error('删除广播数据包错误:', error);
        alert('删除失败，请重试');
    }
}

// 添加跳转到作业目录的函数
async function viewAssignments() {
    try {
        const response = await fetch('/api/assignments_dir');
        const data = await response.json();
        if (data.assignments_dir) {
            alert('请在文件浏览器中打开以下路径查看已提交的作业：\n' + data.assignments_dir);
        } else {
            alert('无法获取作业目录路径。');
        }
    } catch (error) {
        console.error('获取作业目录路径错误:', error);
        alert('获取作业目录路径失败，请重试。');
    }
} 