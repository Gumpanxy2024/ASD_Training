document.addEventListener('DOMContentLoaded', () => {
    // 获取DOM元素
    const video = document.getElementById('webcam');
    const overlay = document.getElementById('overlay');
    const startBtn = document.getElementById('startBtn');
    const resetBtn = document.getElementById('resetBtn');
    const saveBtn = document.getElementById('saveBtn');
    const statusIndicator = document.getElementById('status');
    const messagesDiv = document.getElementById('messages');
    
    // 状态元素
    const elapsedTimeEl = document.getElementById('elapsed-time');
    const distractionCountEl = document.getElementById('distraction-count');
    const distractionTimeEl = document.getElementById('distraction-time');
    const distractionPercentageEl = document.getElementById('distraction-percentage');
    const currentStatusEl = document.getElementById('current-status');
    const earValueEl = document.getElementById('ear-value');
    
    // 创建绘图上下文
    const ctx = overlay.getContext('2d');
    
    let isRunning = false;
    let startTime = null;
    let timerInterval = null;
    let processingFrame = false;
    let attentionHistory = Array(100).fill(1); // 1表示专注，0表示分心
    
    // 初始化函数
    async function init() {
        try {
            // 请求摄像头权限
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    facingMode: 'user'
                },
                audio: false
            });
            
            // 设置视频流
            video.srcObject = stream;
            
            // 调整canvas尺寸
            overlay.width = video.clientWidth;
            overlay.height = video.clientHeight;
            
            statusIndicator.textContent = '准备就绪，点击开始';
            startBtn.disabled = false;
        } catch (error) {
            console.error('无法访问摄像头:', error);
            statusIndicator.textContent = '无法访问摄像头！';
            statusIndicator.classList.add('error');
            showMessage('错误: 无法访问摄像头。请确保您的浏览器允许访问摄像头并刷新页面。', 'error');
        }
    }
    
    // 开始检测
    function startDetection() {
        if (isRunning) return;
        
        isRunning = true;
        startTime = Date.now();
        startBtn.textContent = '停止检测';
        statusIndicator.textContent = '检测中...';
        
        // 更新计时器
        timerInterval = setInterval(updateTimer, 1000);
        
        // 开始处理帧
        requestAnimationFrame(processFrame);
    }
    
    // 停止检测
    function stopDetection() {
        isRunning = false;
        startBtn.textContent = '开始检测';
        statusIndicator.textContent = '检测已停止';
        
        clearInterval(timerInterval);
    }
    
    // 更新计时器显示
    function updateTimer() {
        if (!startTime) return;
        
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const hours = Math.floor(elapsed / 3600).toString().padStart(2, '0');
        const minutes = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
        const seconds = (elapsed % 60).toString().padStart(2, '0');
        
        elapsedTimeEl.textContent = `${hours}:${minutes}:${seconds}`;
    }
    
    // 处理视频帧
    async function processFrame() {
        if (!isRunning) return;
        
        if (!processingFrame) {
            processingFrame = true;
            
            try {
                // 捕获当前帧
                const imageData = captureFrame();
                
                // 发送到服务器进行处理
                const response = await fetch('/process_frame', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ image: imageData })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    updateUI(result);
                } else {
                    console.error('服务器处理失败');
                }
            } catch (error) {
                console.error('帧处理出错:', error);
            }
            
            processingFrame = false;
        }
        
        // 继续处理下一帧
        requestAnimationFrame(processFrame);
    }
    
    // 捕获视频帧
    function captureFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.8);
    }
    
    // 更新UI
    function updateUI(result) {
        // 清除画布
        ctx.clearRect(0, 0, overlay.width, overlay.height);
        
        // 更新统计数据
        distractionCountEl.textContent = result.distraction_count;
        distractionTimeEl.textContent = `${result.distraction_time}秒`;
        distractionPercentageEl.textContent = `${result.distraction_percentage}%`;
        earValueEl.textContent = result.avg_ear ? result.avg_ear.toFixed(2) : "未检测";
        
        // 更新当前状态
        if (result.face_detected) {
            currentStatusEl.textContent = result.is_distracted ? "分心" : "专注";
            currentStatusEl.className = result.is_distracted ? "distracted" : "focused";
            
            // 更新注意力历史
            attentionHistory.push(result.is_distracted ? 0 : 1);
            if (attentionHistory.length > 100) {
                attentionHistory.shift();
            }
            
            // 绘制人脸框和关键点
            if (result.face_box) {
                const { x, y, width, height } = result.face_box;
                const scaleX = overlay.width / result.image_width;
                const scaleY = overlay.height / result.image_height;
                
                // 绘制人脸框
                ctx.lineWidth = 2;
                ctx.strokeStyle = result.is_distracted ? 'red' : 'green';
                ctx.strokeRect(
                    x * scaleX, 
                    y * scaleY, 
                    width * scaleX, 
                    height * scaleY
                );
                
                // 如果有面部关键点，绘制它们
                if (result.landmarks) {
                    ctx.fillStyle = '#FF0000';
                    result.landmarks.forEach(point => {
                        ctx.beginPath();
                        ctx.arc(
                            point.x * scaleX, 
                            point.y * scaleY, 
                            1, 0, 2 * Math.PI
                        );
                        ctx.fill();
                    });
                }
                
                // 显示状态文本
                ctx.font = '16px Arial';
                ctx.fillStyle = result.is_distracted ? 'red' : 'green';
                ctx.fillText(
                    result.is_distracted ? '注意力分散' : '注意力集中',
                    (x * scaleX), 
                    (y * scaleY) - 5
                );
            }
        } else {
            currentStatusEl.textContent = "未检测到人脸";
            currentStatusEl.className = "";
        }
        
        // 绘制注意力历史图表
        drawAttentionChart();
    }
    
    // 绘制注意力历史图表
    function drawAttentionChart() {
        const chartCanvas = document.getElementById('attention-chart');
        const chartCtx = chartCanvas.getContext('2d');
        
        // 清除图表
        chartCtx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        
        // 绘制背景
        chartCtx.fillStyle = '#f8f8f8';
        chartCtx.fillRect(0, 0, chartCanvas.width, chartCanvas.height);
        
        // 计算每个数据点的宽度
        const barWidth = chartCanvas.width / attentionHistory.length;
        
        // 绘制数据
        attentionHistory.forEach((value, index) => {
            chartCtx.fillStyle = value === 1 ? '#4CAF50' : '#F44336';
            chartCtx.fillRect(
                index * barWidth, 
                0, 
                barWidth, 
                chartCanvas.height * (value === 1 ? 0.3 : 0.8)
            );
        });
    }
    
    // 重置统计
    async function resetStats() {
        try {
            const response = await fetch('/reset_stats', {
                method: 'POST'
            });
            
            if (response.ok) {
                distractionCountEl.textContent = '0';
                distractionTimeEl.textContent = '0.0秒';
                distractionPercentageEl.textContent = '0.0%';
                attentionHistory = Array(100).fill(1);
                drawAttentionChart();
                showMessage('统计数据已重置', 'success');
            }
        } catch (error) {
            console.error('重置失败:', error);
            showMessage('重置统计失败', 'error');
        }
    }
    
    // 保存记录
    async function saveRecord() {
        try {
            const response = await fetch('/save_record', {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                showMessage(`记录已保存: ${result.filename}`, 'success');
            }
        } catch (error) {
            console.error('保存记录失败:', error);
            showMessage('保存记录失败', 'error');
        }
    }
    
    // 显示消息
    function showMessage(text, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = text;
        
        messagesDiv.appendChild(messageEl);
        
        // 5秒后自动移除消息
        setTimeout(() => {
            messageEl.classList.add('fade-out');
            setTimeout(() => messagesDiv.removeChild(messageEl), 500);
        }, 5000);
    }
    
    // 事件监听
    startBtn.addEventListener('click', () => {
        if (isRunning) {
            stopDetection();
        } else {
            startDetection();
        }
    });
    
    resetBtn.addEventListener('click', resetStats);
    saveBtn.addEventListener('click', saveRecord);
    
    // 初始化应用
    init();
});