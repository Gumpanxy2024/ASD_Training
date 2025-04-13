document.addEventListener('DOMContentLoaded', function() {
    // 欢迎页面处理
    const welcomeScreen = document.getElementById('welcome-screen');
    const trainingContent = document.getElementById('training-content');
    const welcomeStartBtn = document.getElementById('welcome-start-btn');
    
    // 验证关键元素是否被找到
    if (!welcomeScreen) console.error('找不到欢迎页面元素 welcome-screen');
    if (!trainingContent) console.error('找不到训练内容元素 training-content');
    if (!welcomeStartBtn) console.error('找不到开始按钮元素 welcome-start-btn');
    
    // 检查URL参数，如果有skip_welcome=true则直接显示训练内容
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('skip_welcome') === 'true') {
        console.log("URL参数设置跳过欢迎页面");
        welcomeScreen.classList.add('hidden');
        trainingContent.classList.remove('hidden');
        document.body.classList.remove('welcome-active');
        
        // 完全移除欢迎页面元素
        try {
            welcomeScreen.parentNode.removeChild(welcomeScreen);
            console.log("欢迎页面已从DOM中移除");
        } catch (e) {
            console.error("移除欢迎页面失败:", e);
        }
    } else {
        // 正常显示欢迎页面
        // 为body添加welcome-active类，激活欢迎页面样式
        document.body.classList.add('welcome-active');
        
        // 欢迎页面打字效果
        setTimeout(() => {
            // 第一段文字动画
            const typingText1 = document.getElementById('typing-text-1');
            if (typingText1) {
                // 获取原始文本
                const text = typingText1.textContent || typingText1.innerText;
                // 保存原始文本并完全清空
                const originalText = text.trim();
                typingText1.innerHTML = '';
                typingText1.textContent = '';
                
                // 强制重绘以确保清空生效
                setTimeout(() => {
                    typingText1.classList.add('typing-animation');
                    
                    // 逐字显示文本
                    let charIndex = 0;
                    let typingInterval = setInterval(() => {
                        if (charIndex < originalText.length) {
                            typingText1.textContent += originalText.charAt(charIndex);
                            charIndex++;
                        } else {
                            clearInterval(typingInterval);
                            // 打字完成后
                            typingText1.classList.add('typing-done');
                            typingText1.classList.remove('typing-animation');
                            
                            // 第二段文字动画
                            const typingText2 = document.getElementById('typing-text-2');
                            if (typingText2) {
                                // 获取原始文本
                                const text2 = typingText2.textContent || typingText2.innerText;
                                const originalText2 = text2.trim();
                                typingText2.innerHTML = '';
                                typingText2.textContent = '';
                                
                                // 强制重绘以确保清空生效
                                setTimeout(() => {
                                    typingText2.classList.add('typing-animation');
                                    
                                    // 逐字显示第二段文本
                                    let charIndex2 = 0;
                                    let typingInterval2 = setInterval(() => {
                                        if (charIndex2 < originalText2.length) {
                                            typingText2.textContent += originalText2.charAt(charIndex2);
                                            charIndex2++;
                                        } else {
                                            clearInterval(typingInterval2);
                                            // 第二段打字完成后
                                            typingText2.classList.add('typing-done');
                                            typingText2.classList.remove('typing-animation');
                                            
                                            // 列表项动画
                                            const welcomeList = document.querySelector('.welcome-list');
                                            if (welcomeList) {
                                                welcomeList.style.opacity = '1';
                                                
                                                // 逐个显示列表项
                                                const listItems = document.querySelectorAll('.list-item-animation');
                                                listItems.forEach((item, index) => {
                                                    setTimeout(() => {
                                                        item.classList.add('show');
                                                    }, 300 * index);
                                                });
                                                
                                                // 计算所有列表项显示完成的时间
                                                const listCompletionTime = 300 * listItems.length + 500;
                                                
                                                // 最后一段文字动画
                                                setTimeout(() => {
                                                    const typingText3 = document.getElementById('typing-text-3');
                                                    if (typingText3) {
                                                        // 获取原始文本
                                                        const text3 = typingText3.textContent || typingText3.innerText;
                                                        const originalText3 = text3.trim();
                                                        typingText3.innerHTML = '';
                                                        typingText3.textContent = '';
                                                        
                                                        // 强制重绘以确保清空生效
                                                        setTimeout(() => {
                                                            typingText3.classList.add('typing-animation');
                                                            
                                                            // 逐字显示最后一段文本
                                                            let charIndex3 = 0;
                                                            let typingInterval3 = setInterval(() => {
                                                                if (charIndex3 < originalText3.length) {
                                                                    typingText3.textContent += originalText3.charAt(charIndex3);
                                                                    charIndex3++;
                                                                } else {
                                                                    clearInterval(typingInterval3);
                                                                    // 最后一段打字完成后
                                                                    typingText3.classList.add('typing-done');
                                                                    typingText3.classList.remove('typing-animation');
                                                                }
                                                            }, 50); // 每50毫秒打一个字
                                                        }, 10);
                                                    }
                                                }, listCompletionTime);
                                            }
                                        }
                                    }, 50); // 每50毫秒打一个字
                                }, 10);
                            }
                        }
                    }, 50); // 每50毫秒打一个字
                }, 10);
            }
        }, 1000);
    }
    
    // 训练控制按钮
    const startTrainingBtn = document.getElementById('startTrainingBtn');
    const stopTrainingBtn = document.getElementById('stopTrainingBtn');
    const saveRecordsBtn = document.getElementById('saveRecordsBtn');
    const resetBtn = document.getElementById('resetBtn');
    const settingsButton = document.getElementById('settings-btn');
    const saveModal = document.getElementById('save-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const downloadSummaryBtn = document.getElementById('download-summary');
    
    // 训练完成按钮
    const trainingComplete = document.getElementById('training-complete');
    const completeTrainingBtn = document.getElementById('complete-training-btn');
    
    // 设置弹窗元素
    const settingsModal = document.getElementById('settings-modal');
    const closeSettingsButton = document.getElementById('close-settings');
    const saveSettingsButton = document.getElementById('save-settings');
    
    // 训练状态变量
    let isTraining = false;
    let trainingStartTime = null;
    let distractionCount = 0;
    let totalDistractionTime = 0;
    let correctAnswers = 0;
    let totalQuestions = 0;
    let totalQuestionsToComplete = 20; // 完成训练需要的总题目数
    
    // 性别设置变量
    let userGender = 'female'; // 默认为女生
    // 音乐设置变量
    let musicEnabled = true; // 默认开启音乐
    
    // 创建背景音乐元素
    const backgroundMusic = document.createElement('audio');
    backgroundMusic.id = 'background-music';
    backgroundMusic.loop = true;
    backgroundMusic.volume = 0.5;
    backgroundMusic.src = '/static/images/background-music.mp3'; // 更新音乐文件路径
    document.body.appendChild(backgroundMusic);
    
    // 添加全局变量来跟踪欢迎动画是否完成
    let welcomeAnimationCompleted = false;

    // 欢迎页面开始按钮点击事件
    welcomeStartBtn.addEventListener('click', function() {
        console.log("开始按钮被点击，准备显示训练内容");
        
        // 防止动画未完成时切换
        if (!welcomeAnimationCompleted && 
            !urlParams.get('skip_welcome') === 'true') { // 添加URL参数检查
            console.log("欢迎动画尚未完成，等待动画结束");
            return;
        }
        
        // 防止重复点击
        this.disabled = true;
        
        // 添加淡出动画
        welcomeScreen.classList.add('fade-out');
        
        // 等待动画完成后处理
        setTimeout(() => {
            console.log("淡出动画完成，显示训练内容");
            
            // 确保欢迎页面被隐藏
            welcomeScreen.classList.add('hidden');
            welcomeScreen.classList.remove('fade-out');
            
            // 确保训练内容显示
            trainingContent.classList.remove('hidden');
            
            // 移除body上的welcome-active类
            document.body.classList.remove('welcome-active');
            
            // 初始化训练内容状态
            initializeTrainingContent();
            
            // 可选：完全移除欢迎页面元素
            try {
                welcomeScreen.parentNode.removeChild(welcomeScreen);
                console.log("欢迎页面已从DOM中移除");
            } catch (e) {
                console.error("移除欢迎页面失败:", e);
            }
            
            // 初始化背景音乐
            if (musicEnabled) {
                backgroundMusic.play().catch(error => {
                    console.log('播放音乐失败:', error);
                });
            }
        }, 800); // 增加到800毫秒确保动画完全结束
    });
    
    // 添加初始化训练内容的函数
    function initializeTrainingContent() {
        // 重置训练状态
        const emotionOptions = document.querySelectorAll('.emotion-option');
        const feedbackCorrect = document.getElementById('feedback-correct');
        const feedbackIncorrect = document.getElementById('feedback-incorrect');
        
        if (emotionOptions) emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
        if (feedbackCorrect) feedbackCorrect.classList.remove('show');
        if (feedbackIncorrect) feedbackIncorrect.classList.remove('show');
        
        // 确保虚拟形象显示
        const avatarImage = document.getElementById('avatar-image');
        const videoElement = document.getElementById('video');
        if (avatarImage && videoElement) {
            avatarImage.style.display = 'block';
            avatarImage.src = '/static/images/virtual.png';
            videoElement.classList.add('video-hidden');
            videoElement.classList.remove('w-full', 'h-full', 'object-cover');
        }
        
        // 重置进度显示，但不要重复加载第一题
        const progressText = document.getElementById('progress-text');
        if (progressText) progressText.textContent = '0/20';
        
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) progressBar.style.width = '0%';
        
        // 重要：隐藏摄像头切换按钮，直到训练开始
        const toggleCameraBtn = document.getElementById('toggle-camera');
        if (toggleCameraBtn) toggleCameraBtn.style.display = 'none';
        
        console.log("训练内容已初始化完成");
    }
    
    // 初始播放音乐
    if (musicEnabled) {
        backgroundMusic.play().catch(error => {
            console.log('自动播放受限，需要用户交互后播放:', error);
        });
    }
    
    // 打开设置弹窗
    settingsButton.addEventListener('click', function() {
        // 根据当前性别设置选中状态
        const genderRadios = document.querySelectorAll('input[name="gender"]');
        genderRadios.forEach(radio => {
            if (radio.value === userGender) {
                radio.checked = true;
            }
        });
        
        // 根据当前音乐设置选中状态
        const musicCheckbox = document.getElementById('music-toggle');
        if (musicCheckbox) {
            musicCheckbox.checked = musicEnabled;
        }
        
        settingsModal.classList.remove('hidden');
        settingsModal.classList.add('flex');
    });
    
    // 关闭设置弹窗
    closeSettingsButton.addEventListener('click', function() {
        settingsModal.classList.add('hidden');
        settingsModal.classList.remove('flex');
    });
    
    // 保存设置
    saveSettingsButton.addEventListener('click', function() {
        // 获取选中的性别
        const selectedGender = document.querySelector('input[name="gender"]:checked').value;
        userGender = selectedGender;
        
        // 获取音乐设置
        const musicCheckbox = document.getElementById('music-toggle');
        if (musicCheckbox) {
            musicEnabled = musicCheckbox.checked;
            
            // 根据设置控制音乐播放
            if (musicEnabled) {
                backgroundMusic.play().catch(error => {
                    console.log('播放音乐失败:', error);
                });
            } else {
                backgroundMusic.pause();
            }
        }
        
        // 根据性别更新表情图片
        updateEmotionImages(userGender);
        
        // 关闭弹窗
        settingsModal.classList.add('hidden');
        settingsModal.classList.remove('flex');
    });
   
    // 更新表情图片函数
    function updateEmotionImages(gender) {
        const emotionOptions = document.querySelectorAll('.emotion-option');
        
        emotionOptions.forEach(option => {
            const img = option.querySelector('img');
            const emotion = option.getAttribute('data-emotion');
            
            if (gender === 'male') {
                // 男生表情图片
                if (emotion === 'neutral') {
                    img.src = '/static/images/boy_neutral.png';
                } else {
                    img.src = `/static/images/boy_${emotion}.png`;
                }
            } else {
                // 女生表情图片（默认）
                if (emotion === 'sad') {
                    img.src = '/static/images/sadness.png';
                } else if (emotion === 'neutral') {
                    img.src = '/static/images/neutral.png';
                } else {
                    img.src = `/static/images/${emotion}.png`;
                }
            }
        });
    }
    
    // 获取摄像头权限并显示视频流
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                // 创建视频元素替换虚拟形象图片
                const avatarContainer = document.querySelector('.avatar-container');
                const avatarImage = document.getElementById('avatar-image');
                const videoElement = document.getElementById('video');
                
                // 设置视频流
                if (videoElement) {
                    videoElement.srcObject = stream;
                    
                    // 获取摄像头切换按钮
                    const toggleCameraBtn = document.getElementById('toggle-camera');
                    let cameraVisible = false;
                    
                    // 开始训练时显示摄像头切换按钮，但不直接显示视频
                    startTrainingBtn.addEventListener('click', function() {
                        if (isTraining) return;
                        
                        // 开始训练前先清除可能的旧状态
                        emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
                        feedbackCorrect.classList.remove('show');
                        feedbackIncorrect.classList.remove('show');
                        
                        // 确保虚拟形象正确显示
                        const avatarImage = document.getElementById('avatar-image');
                        if (avatarImage) avatarImage.src = '/static/images/virtual.png';
                        
                        // 确保当前问题状态是清晰的
                        currentQuestionIndex = 0;
                        
                        // 开始训练
                        isTraining = true;
                        trainingStartTime = new Date();
                        
                        // 更新按钮状态
                        startTrainingBtn.disabled = true;
                        stopTrainingBtn.disabled = false;
                        
                        // 启用下一题按钮，禁用上一题按钮
                        nextBtn.disabled = false;
                        prevBtn.disabled = true;
                        
                        // 显示摄像头切换按钮
                        if (toggleCameraBtn) toggleCameraBtn.style.display = 'flex';
                        
                        // 重要：在这里只加载一次第一题
                        console.log("开始训练，加载第一题");
                        loadNewQuestion(1);
                        
                        // 更新进度显示
                        document.getElementById('progress-text').textContent = '1/20';
                        document.getElementById('progress-bar').style.width = '5%';
                        
                        // 更新状态显示
                        updateAvatarStatus("训练中，请保持专注");
                        document.getElementById('current-emotion').innerHTML = `
                            <span class="text-4xl">🔍</span>
                            <p class="text-sm text-gray-700 mt-2">情绪分析中</p>
                            <p class="text-xs text-gray-500">检测中...</p>
                        `;
                        
                        document.getElementById('attention-status').textContent = "训练已开始，系统正在监测专注度";
                    });
                    
                    // 摄像头切换按钮点击事件
                    toggleCameraBtn.addEventListener('click', function() {
                        cameraVisible = !cameraVisible;
                        
                        if (cameraVisible) {
                            // 显示摄像头
                            avatarImage.style.display = 'none';
                            videoElement.classList.remove('video-hidden');
                            videoElement.classList.add('w-full', 'h-full', 'object-cover');
                        } else {
                            // 显示虚拟形象
                            avatarImage.style.display = 'block';
                            videoElement.classList.add('video-hidden');
                            videoElement.classList.remove('w-full', 'h-full', 'object-cover');
                        }
                    });
                }
                
                // 这里可以添加视频分析代码，如表情识别、注意力监测等
                videoElement.addEventListener('play', function() {
                    // 例如每秒分析一次视频帧
                    setInterval(function() {
                        if (isTraining) {
                            analyzeVideoFrame(videoElement);
                        }
                    }, 1000);
                });
            })
            .catch(function(error) {
                console.error("无法访问摄像头: ", error);
                // 如果无法获取摄像头，仍然显示虚拟形象
                updateAvatarStatus("无法连接摄像头，使用默认模式");
            });
    }
    
    // 分析视频帧的函数 - 改为与后端通信进行实际检测
    async function analyzeVideoFrame(videoElement) {
        try {
            // 创建canvas并捕获当前视频帧
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoElement, 0, 0);
            
            // 转换为base64格式的图像数据
            const imageData = canvas.toDataURL('image/jpeg', 0.8);
            
            // 发送到后端集成API进行检测
            const response = await fetch('/api/integrated_detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData }),
            });
            
            // 处理响应数据
            const data = await response.json();
            if (data.status === 'success') {
                // 处理情绪检测结果
                if (data.emotion_results && data.emotion_results.length > 0) {
                    const dominantEmotion = data.emotion_results[0];
                    
                    // 情绪图标映射
                    const emotionIcons = {
                        'happy': '😊',
                        'sad': '😢',
                        'angry': '😠',
                        'neutral': '😐',
                        'fear': '😨',
                        'surprised': '😲',
                        'disgust': '🤢'
                    };
                    
                    // 情绪中文名称映射
                    const emotionNames = {
                        'happy': '开心',
                        'sad': '伤心',
                        'angry': '生气',
                        'neutral': '平静',
                        'fear': '害怕',
                        'surprised': '惊讶',
                        'disgust': '厌恶'
                    };
                    
                    // 更新情绪显示
                    const currentEmotion = document.getElementById('current-emotion');
                    if (currentEmotion) {
                        const emotionName = dominantEmotion.emotion;
                        const emotionIcon = emotionIcons[emotionName] || '😐';
                        const emotionText = emotionNames[emotionName] || emotionName;
                        
                        currentEmotion.innerHTML = `
                            <span class="text-4xl">${emotionIcon}</span>
                            <p class="text-sm text-gray-700 mt-2">${emotionText}</p>
                            <p class="text-xs text-gray-500">置信度: ${(dominantEmotion.confidence * 100).toFixed(1)}%</p>
                        `;
                        
                        // 更新虚拟形象的表情状态
                        updateAvatarEmotion(emotionName);
                    }
                }
                
                // 处理注意力检测结果
                if (data.attention_result) {
                    // 计算专注度百分比
                    const focusPercentage = 100 - data.attention_result.distraction_percentage;
                    
                    // 更新专注度条
                    const attentionBar = document.getElementById('attention-bar');
                    attentionBar.style.width = `${focusPercentage}%`;
                    
                    // 根据专注度改变颜色
                    if (focusPercentage > 70) {
                        attentionBar.className = 'bg-green-600 h-2.5 rounded-full';
                    } else if (focusPercentage > 30) {
                        attentionBar.className = 'bg-yellow-500 h-2.5 rounded-full';
                    } else {
                        attentionBar.className = 'bg-red-500 h-2.5 rounded-full';
                    }
                    
                    // 更新分心统计
                    document.getElementById('distraction-count').textContent = data.attention_result.distraction_count;
                    document.getElementById('distraction-time').textContent = `${data.attention_result.distraction_time}秒`;
                    
                    // 更新注意力状态文本
                    const attentionStatus = document.getElementById('attention-status');
                    if (data.attention_result.is_distracted) {
                        attentionStatus.textContent = `注意力分散 (已分心 ${data.attention_result.distraction_count} 次，共 ${data.attention_result.distraction_time} 秒)`;
                        if (data.attention_result.show_reminder) {
                            showAttentionAlert();
                        }
                    } else {
                        attentionStatus.textContent = `专注中 (专注度: ${focusPercentage.toFixed(1)}%)`;
                    }
                    
                    // 更新虚拟形象状态
                    if (data.attention_result.is_distracted) {
                        updateAvatarStatus("请集中注意力，已检测到分心");
                    } else {
                        updateAvatarStatus("注意力集中，继续保持");
                    }
                }
            } else {
                console.error('检测失败:', data.message || '未知错误');
            }
            
        } catch (error) {
            console.error('视频帧分析错误:', error);
        }
    }
    
    // 更新虚拟形象状态的函数
    function updateAvatarStatus(message) {
        const avatarStatus = document.querySelector('.avatar-status');
        if (avatarStatus) {
            avatarStatus.innerHTML = `<i class="fas fa-smile-beam mr-2"></i> ${message}`;
        }
    }
    
    // 更新虚拟形象表情的函数
    function updateAvatarEmotion(emotion) {
        const avatarImage = document.getElementById('avatar-image');
        if (avatarImage && avatarImage.style.display !== 'none') {
            // 根据检测到的用户情绪，显示响应的虚拟形象表情
            // 这里可以根据不同情绪显示不同的图片
            const genderPrefix = userGender === 'male' ? 'boy_' : '';
            
            if (emotion === 'happy') {
                avatarImage.src = `/static/images/${genderPrefix}virtual_happy.png`;
            } else if (emotion === 'sad') {
                avatarImage.src = `/static/images/${genderPrefix}virtual_sad.png`;
            } else if (emotion === 'angry') {
                avatarImage.src = `/static/images/${genderPrefix}virtual_angry.png`;
            } else {
                avatarImage.src = `/static/images/${genderPrefix}virtual.png`;
            }
        }
    }
    
    // 显示注意力提醒
    function showAttentionAlert() {
        console.log("执行显示分心提醒函数");
        
        // 获取提醒元素
        const attentionAlert = document.getElementById('attention-alert');
        if (!attentionAlert) {
            console.error("找不到attention-alert元素");
            return;
        }
        
        // 如果已经显示，不再重复显示
        if (!attentionAlert.classList.contains('hidden')) {
            console.log("分心提醒已经在显示中");
            return;
        }
        
        console.log("显示分心提醒");
        
        // 显示提醒
        attentionAlert.classList.remove('hidden');
        attentionAlert.classList.add('show-alert');
        
        // 3秒后自动隐藏
        setTimeout(function() {
            attentionAlert.classList.remove('show-alert');
            setTimeout(function() {
                attentionAlert.classList.add('hidden');
            }, 500);
        }, 3000);
    }

    // 场景选择交互
    const sceneOptions = document.querySelectorAll('.scene-option');
    const currentSceneLabel = document.getElementById('current-scene-label');
    
    // 场景选择事件
    document.querySelectorAll('.scene-option').forEach(option => {
        option.addEventListener('click', function() {
            if (isTraining) return; // 训练中不允许切换场景
            
            // 移除其他选项的选中状态
            document.querySelectorAll('.scene-option').forEach(opt => opt.classList.remove('scene-selected'));
            // 添加当前选项的选中状态
            this.classList.add('scene-selected');
            
            // 更新场景标签
            const sceneName = this.getAttribute('data-scene');
            const sceneLabels = {
                'school': '学校场景',
                'social': '社交场景',
                'transport': '交通场景',
                'food': '吃饭场景',
                'family': '家庭关系场景'
            };
            document.getElementById('current-scene-label').textContent = sceneLabels[sceneName] || '学校场景';
            
            // 重新加载第一题
            loadNewQuestion(1);
            
            // 重置进度
            document.getElementById('progress-text').textContent = '1/10';
            document.getElementById('progress-bar').style.width = '10%';
        });
    });

    // 表情选择交互
    const emotionOptions = document.querySelectorAll('.emotion-option');
    const feedbackCorrect = document.getElementById('feedback-correct');
    const feedbackIncorrect = document.getElementById('feedback-incorrect');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn'); // 添加上一题按钮引用
    
    // 当前题目索引
    let currentQuestionIndex = 0;

    emotionOptions.forEach(option => {
        option.addEventListener('click', function() {
            if (!isTraining) return; // 只有在训练中才能选择表情
            
            // 重置选项状态
            emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
            // 添加当前选项的选中状态
            this.classList.add('emotion-selected');
    
            // 无论答案是否正确，都启用下一步按钮
            nextBtn.disabled = false;
    
            // 获取当前选中表情
            const selectedEmotion = this.getAttribute('data-emotion');
            
            // 检查答案是否正确，支持多个正确答案
            let isCorrect = false;
            if (Array.isArray(currentCorrectAnswer)) {
                // 如果正确答案是数组，检查选择的答案是否在数组中
                isCorrect = currentCorrectAnswer.includes(selectedEmotion);
            } else {
                // 单个正确答案的情况
                isCorrect = selectedEmotion === currentCorrectAnswer;
            }
            
            // 显示答案反馈
            if (isCorrect) {
                feedbackCorrect.classList.add('show');
                feedbackIncorrect.classList.remove('show');
                correctAnswers++;
            } else {
                feedbackCorrect.classList.remove('show');
                feedbackIncorrect.classList.add('show');
            }
            
            totalQuestions++;
            
            // 检查是否完成了所有问题
            checkTrainingCompletion();
        });
    });
    
    // 检查训练是否完成的函数
    function checkTrainingCompletion() {
        const progressText = document.getElementById('progress-text');
        const currentProgress = progressText.textContent.split('/');
        let current = parseInt(currentProgress[0]);
        const total = parseInt(currentProgress[1]);
        
        if (current === total) {
            // 当前场景的所有题目已完成
            const sceneOptions = document.querySelectorAll('.scene-option');
            const currentSceneElement = document.querySelector('.scene-selected');
            
            if (currentSceneElement && sceneOptions.length > 1) {
                // 获取当前场景索引
                let currentIndex = -1;
                sceneOptions.forEach((option, index) => {
                    if (option.classList.contains('scene-selected')) {
                        currentIndex = index;
                    }
                });
                
                // 如果不是最后一个场景，自动切换到下一个场景
                if (currentIndex >= 0 && currentIndex < sceneOptions.length - 1) {
                    // 显示完成当前场景的反馈
                    trainingComplete.classList.remove('hidden');
                    
                    // 添加切换到下一个场景的按钮
                    const completeTrainingBtn = document.getElementById('complete-training-btn');
                    completeTrainingBtn.textContent = '继续下一个场景';
                    completeTrainingBtn.addEventListener('click', function() {
                        // 切换到下一个场景
                        trainingComplete.classList.add('hidden');
                        
                        // 选择下一个场景
                        const nextScene = sceneOptions[currentIndex + 1];
                        if (nextScene) {
                            // 移除当前选中状态
                            currentSceneElement.classList.remove('scene-selected');
                            // 选中下一个场景
                            nextScene.classList.add('scene-selected');
                            
                            // 更新场景标签
                            const sceneName = nextScene.getAttribute('data-scene');
                            const sceneLabels = {
                                'school': '学校场景',
                                'social': '社交场景',
                                'transport': '交通场景',
                                'food': '吃饭场景',
                                'family': '家庭关系场景'
                            };
                            document.getElementById('current-scene-label').textContent = sceneLabels[sceneName] || '学校场景';
                            
                            // 重置进度和加载第一题
                            document.getElementById('progress-text').textContent = '1/10';
                            document.getElementById('progress-bar').style.width = '10%';
                            loadNewQuestion(1);
                            
                            // 重置按钮状态
                            nextBtn.disabled = false;
                            prevBtn.disabled = true;
                        }
                    }, { once: true }); // 确保事件只触发一次
                } else {
                    // 如果是最后一个场景，显示训练全部完成
                    trainingComplete.classList.remove('hidden');
                    document.getElementById('complete-training-btn').textContent = '结束训练';
                    // 禁用导航按钮
                    nextBtn.disabled = true;
                    prevBtn.disabled = true;
                }
            } else {
                // 只有一个场景或未找到当前场景元素
                trainingComplete.classList.remove('hidden');
                // 禁用导航按钮
                nextBtn.disabled = true;
                prevBtn.disabled = true;
            }
        }
    }

    // 虚拟形象控制功能
    const avatarMirrorBtn = document.getElementById('avatar-mirror'); // 镜像按钮引用
    const avatarStyleBtn = document.getElementById('avatar-style'); // 样式按钮引用
    const avatarExpressionBtn = document.getElementById('avatar-expression'); // 表情按钮引用
    
    // 镜像按钮功能
    if (avatarMirrorBtn) {
        avatarMirrorBtn.addEventListener('click', function() {
            const videoElement = document.getElementById('video');
            const avatarImage = document.getElementById('avatar-image');
            
            if (videoElement && videoElement.style.display !== 'none') {
                // 获取当前transform值
                const currentTransform = getComputedStyle(videoElement).transform;
                // 切换镜像效果
                if (currentTransform.includes('matrix(-1')) {
                    videoElement.style.transform = 'scaleX(1)';
                } else {
                    videoElement.style.transform = 'scaleX(-1)';
                }
            } else if (avatarImage) {
                // 如果没有视频元素，则镜像虚拟形象图片
                const currentTransform = getComputedStyle(avatarImage).transform;
                if (currentTransform.includes('matrix(-1')) {
                    avatarImage.style.transform = 'scaleX(1)';
                } else {
                    avatarImage.style.transform = 'scaleX(-1)';
                }
            }
        });
    }
    
    // 虚拟形象样式切换功能
    if (avatarStyleBtn) {
        avatarStyleBtn.addEventListener('click', function() {
            if (isTraining) return; // 训练中不允许切换形象
            
            const avatarImage = document.getElementById('avatar-image');
            if (avatarImage) {
                // 切换不同样式的虚拟形象
                const styles = ['default', 'casual', 'formal', 'sporty'];
                const currentStyle = avatarImage.getAttribute('data-style') || 'default';
                
                // 找到当前样式的索引，并切换到下一个样式
                let index = styles.indexOf(currentStyle);
                index = (index + 1) % styles.length;
                const newStyle = styles[index];
                
                // 更新虚拟形象图片
                const genderPrefix = userGender === 'male' ? 'boy_' : '';
                avatarImage.src = `/static/images/${genderPrefix}virtual_${newStyle}.png`;
                avatarImage.setAttribute('data-style', newStyle);
                
                // 显示切换提示
                updateAvatarStatus(`已切换形象样式：${getStyleName(newStyle)}`);
            }
        });
    }
    
    // 虚拟形象表情切换功能
    if (avatarExpressionBtn) {
        avatarExpressionBtn.addEventListener('click', function() {
            if (isTraining) return; // 训练中不允许手动切换表情
            
            const avatarImage = document.getElementById('avatar-image');
            if (avatarImage) {
                // 切换不同的表情
                const expressions = ['neutral', 'happy', 'sad', 'surprised', 'wink', 'thinking'];
                const currentExpression = avatarImage.getAttribute('data-expression') || 'neutral';
                
                // 找到当前表情的索引，并切换到下一个表情
                let index = expressions.indexOf(currentExpression);
                index = (index + 1) % expressions.length;
                const newExpression = expressions[index];
                
                // 更新虚拟形象表情
                const genderPrefix = userGender === 'male' ? 'boy_' : '';
                const style = avatarImage.getAttribute('data-style') || 'default';
                
                // 对于某些特殊表情，可能需要单独的图片
                if (['wink', 'thinking', 'surprised'].includes(newExpression)) {
                    avatarImage.src = `/static/images/${genderPrefix}virtual_${newExpression}.png`;
                } else {
                    // 使用基本情绪图片
                    avatarImage.src = `/static/images/${genderPrefix}virtual_${newExpression}.png`;
                }
                
                avatarImage.setAttribute('data-expression', newExpression);
                
                // 显示切换提示
                updateAvatarStatus(`已切换表情：${getExpressionName(newExpression)}`);
            }
        });
    }

    // 重新开始按钮功能
    resetBtn.addEventListener('click', function() {
        // 重置所有选择和状态
        emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
        feedbackCorrect.classList.remove('show');
        feedbackIncorrect.classList.remove('show');
        nextBtn.disabled = true;
        
        // 隐藏训练完成按钮
        trainingComplete.classList.add('hidden');
        
        // 重置进度条
        const progressBar = document.getElementById('progress-bar');
        progressBar.style.width = '10%';
        document.getElementById('progress-text').textContent = '1/10';
        
        // 重置分心统计
        distractionCount = 0;
        totalDistractionTime = 0;
        document.getElementById('distraction-count').textContent = '0';
        document.getElementById('distraction-time').textContent = '0秒';
        
        // 重置答题统计
        correctAnswers = 0;
        totalQuestions = 0;
        
        // 重新加载第一题
        loadNewQuestion(1);
        
        // 如果正在训练，停止训练
        if (isTraining) {
            stopTraining();
        }
    });

    // 下一题按钮功能
    nextBtn.addEventListener('click', function() {
        if (!isTraining) return; // 只有训练中才能切换题目
        
        // 清除当前选择
        emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
        feedbackCorrect.classList.remove('show');
        feedbackIncorrect.classList.remove('show');
        nextBtn.disabled = true;
        
        // 更新进度
        const progressText = document.getElementById('progress-text');
        const currentProgress = progressText.textContent.split('/');
        let current = parseInt(currentProgress[0]);
        const total = parseInt(currentProgress[1]);
        
        if (current < total) {
            current++;
            currentQuestionIndex = current - 1; // 更新当前题目索引
            progressText.textContent = `${current}/${total}`;
            
            // 更新进度条
            const progressBar = document.getElementById('progress-bar');
            progressBar.style.width = `${(current / total) * 100}%`;
            
            // 启用上一题按钮
            prevBtn.disabled = false;
            
            // 加载新题目
            loadNewQuestion(current);
            
            // 检查是否完成训练
            checkTrainingCompletion();
        }
    });

    // 上一题按钮功能
    prevBtn.addEventListener('click', function() {
        if (!isTraining) return; // 只有训练中才能切换题目
        
        // 清除当前选择
        emotionOptions.forEach(opt => opt.classList.remove('emotion-selected'));
        feedbackCorrect.classList.remove('show');
        feedbackIncorrect.classList.remove('show');
        
        // 更新进度
        const progressText = document.getElementById('progress-text');
        const currentProgress = progressText.textContent.split('/');
        let current = parseInt(currentProgress[0]);
        const total = parseInt(currentProgress[1]);
        
        if (current > 1) {
            current--;
            currentQuestionIndex = current - 1; // 更新当前题目索引
            progressText.textContent = `${current}/${total}`;
            
            // 更新进度条
            const progressBar = document.getElementById('progress-bar');
            progressBar.style.width = `${(current / total) * 100}%`;
            
            // 如果是第一题，禁用上一题按钮
            if (current === 1) {
                prevBtn.disabled = true;
            }
            
            // 启用下一题按钮
            nextBtn.disabled = false;
            
            // 加载上一题
            loadNewQuestion(current);
            
            // 隐藏训练完成按钮（因为返回了前一题）
            trainingComplete.classList.add('hidden');
        }
    });

    // 加载新题目的函数
    function loadNewQuestion(questionNumber) {
        console.log("加载新题目:", questionNumber);
        
        // 获取当前选中的场景
        let currentScene = 'school'; // 默认场景
        const selectedSceneElement = document.querySelector('.scene-selected');
        
        if (selectedSceneElement) {
            currentScene = selectedSceneElement.getAttribute('data-scene') || 'school';
        }
        
        // 获取当前选择的性别
        const isMale = document.querySelector('input[name="gender"][value="male"]').checked;
        
        // 定义问题库
        const questions = {
            'school': {
                'male': [
                    "明明主动帮同学捡起掉落的课本",
                    "同学把明明的文具扔在了地上",
                    "明明的画没有被选上展览",
                    "教室里大家都在安静写作业"
                ],
                'female': [
                    "小红帮同学绑好了松掉的蝴蝶结发绳",
                    "同学故意扯掉了小红头上的发卡",
                    "小红精心准备的舞蹈动作没有跳好",
                    "午休时和小伙伴一起听轻音乐画画"
                ]
            },
            'social': {
                // 社交场景题目
                'male': [
                    "朋友邀请明明去生日派对",
                    "玩游戏时，有人故意推倒明明的积木",
                    "明明想加入跳绳，但其他孩子说'人满了'",
                    "和邻居姐姐一起拼拼图"
                ],
                'female': [
                    "朋友送了小红一个自己做的串珠发卡",
                    "有人故意踩脏了小红的新蕾丝裙摆",
                    "小红想加入跳皮筋，但被说'跳得不好'",
                    "和邻居家的小猫玩游戏"
                ]
            },
            'transport': {
                // 交通场景题目
                'male': [
                    "公交车上有人给明明让座，明明说了声谢谢",
                    "地铁坐过站，周围都是陌生人",
                    "有人主动给老爷爷让座",
                    "雨天骑车的人溅了明明一身水"
                ],
                'female': [
                    "地铁上有人给小红让座，小红说了声谢谢",
                    "地铁坐过站，周围都是陌生人",
                    "小红给流浪猫带的鱼干被不小心扫走了",
                    "和爸爸散步，闻路边的桂花香"
                ]
            },
            'food': {
                // 吃饭场景题目
                'male': [
                    "妈妈夸明明吃完饭后自己收拾了碗筷",
                    "吃饭时有人一直说话，吵得明明吃不下",
                    "餐厅里没有明明爱吃的菜",
                    "全家人慢慢品尝新做的菜"
                ],
                'female': [
                    "妈妈教小红用草莓摆出花朵形状的蛋糕",
                    "表哥把小红摆盘的胡萝卜花推散了",
                    "冰淇淋店卖完了小红最爱的味道",
                    "和外婆慢慢剥着刚煮好的玉米"
                ]
            },
            'family': {
                // 家庭关系场景题目
                'male': [
                    "爸爸帮明明修好了坏掉的玩具",
                    "明明最爱的故事书不小心被弟弟撕坏了",
                    "妈妈答应周末带明明去公园，但她不小心受伤了不能出去了",
                    "下雨天明明和爸爸在家听故事，屋里暖暖的"
                ],
                'female': [
                    "妈妈教小红编了一条彩色丝带手链",
                    "妹妹把小红收藏的亮片贴纸全贴乱了",
                    "爸爸答应陪小红去花市，却因工作取消",
                    "和奶奶一起整理旧照片，听她讲故事"
                ]
            }
        };
        
        // 不同场景和性别的正确答案
        const correctAnswers = {
            'school': {
                'male': ["happy", "angry", "sad", "neutral"],
                'female': ["happy", "angry", "sad", "neutral"]
            },
            'social': {
                'male': ["happy", "angry", "sad", "neutral"],
                'female': ["happy", "angry", "sad", "neutral"]
            },
           'transport': {
               'male': [["neutral", "happy"], "sad", "happy", "angry"],
                'female': ["happy", "sad", "sad", "neutral"]
            },
           'food': {
               'male': ["happy", "angry", "sad", "neutral"],
                'female': ["happy", "angry", "sad", "neutral"]
            },
           'family': {
               'male': ["happy", "angry", "sad", ["neutral", "happy"]], // 第四个问题接受两个答案
                'female': ["happy", "angry", "sad", "neutral"]
            },
        };
        
        // 获取当前场景和性别的问题
        const gender = isMale ? 'male' : 'female';
        const sceneQuestions = questions[currentScene]?.[gender] || questions['school'][gender];
        const questionIndex = (questionNumber - 1) % sceneQuestions.length;
        const question = sceneQuestions[questionIndex];
        
        // 更新当前正确答案
        currentCorrectAnswer = correctAnswers[currentScene]?.[gender]?.[questionIndex] || "happy";
        
        console.log("选择的问题:", question, "正确答案:", currentCorrectAnswer);
        
        // 更新问题文本
        const questionElement = document.getElementById('question-text');
        if (questionElement) {
            // 先移除之前的动画类
            questionElement.classList.remove('question-highlight');
            
            // 添加短暂的延迟后设置新内容，产生内容替换的效果
            setTimeout(() => {
                questionElement.textContent = question;
                
                // 添加动画类来突出显示新问题
                questionElement.classList.add('question-highlight');
            }, 50);
        }
    }

    // 添加全局变量来存储当前正确答案
    let currentCorrectAnswer = "happy";

    // 性别选择变化时重新加载当前题目
    document.querySelectorAll('input[name="gender"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // 获取当前进度
            const progressText = document.getElementById('progress-text');
            if (progressText) {
                const current = parseInt(progressText.textContent.split('/')[0]);
                loadNewQuestion(current);
            }
        });
    });

    // 终止训练按钮点击事件
    stopTrainingBtn.addEventListener('click', function() {
        if (isTraining) {
            // 调用原有的停止训练函数
            stopTraining();
            
            // 隐藏摄像头切换按钮
            const toggleCameraBtn = document.getElementById('toggle-camera');
            if (toggleCameraBtn) {
                toggleCameraBtn.style.display = 'none';
            }
            
            // 如果摄像头正在显示，切回虚拟形象
            const videoElement = document.getElementById('video');
            const avatarImage = document.getElementById('avatar-image');
            if (videoElement && !videoElement.classList.contains('video-hidden')) {
                avatarImage.style.display = 'block';
                videoElement.classList.add('video-hidden');
                videoElement.classList.remove('w-full', 'h-full', 'object-cover');
            }
        }
    });
    
    // 训练完成按钮功能
    completeTrainingBtn.addEventListener('click', async function() {
        if (!isTraining) return;
        
        // 停止训练
        stopTraining();
        
        // 收集训练数据
        const trainingData = {
            correctAnswers: correctAnswers,
            totalQuestions: totalQuestions,
            accuracy: totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0,
            trainingDuration: trainingStartTime ? Math.floor((new Date() - trainingStartTime) / 1000) : 0,
            scene: document.querySelector('.scene-selected').getAttribute('data-scene'),
            distractionCount: distractionCount,
            distractionTime: totalDistractionTime,
            completed: true  // 标记为已完成
        };
        
        try {
            // 发送数据到后端保存
            const response = await fetch('/api/save_records', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trainingData)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // 生成训练摘要
                const trainingSummary = document.getElementById('training-summary');
                const currentScene = document.querySelector('.scene-selected').getAttribute('data-scene');
                const sceneLabels = {
                    'school': '学校场景',
                    'social': '社交场景',
                    'transport': '交通场景',
                    'food': '吃饭场景',
                    'family': '家庭关系场景'
                };
                
                // 填充训练摘要，增加完成标记
                trainingSummary.innerHTML = `
                    <div class="mb-4 py-2 px-3 bg-green-100 text-green-800 rounded-lg">
                        <i class="fas fa-check-circle mr-2"></i>训练已完成！
                    </div>
                    <div class="mb-2"><strong>训练场景:</strong> ${sceneLabels[currentScene]}</div>
                    <div class="mb-2"><strong>训练时长:</strong> ${Math.floor(trainingData.trainingDuration / 60)}分${trainingData.trainingDuration % 60}秒</div>
                    <div class="mb-2"><strong>答题数量:</strong> ${totalQuestions}</div>
                    <div class="mb-2"><strong>正确答题:</strong> ${correctAnswers}</div>
                    <div class="mb-2"><strong>正确率:</strong> ${trainingData.accuracy}%</div>
                    <div class="mb-2"><strong>分心次数:</strong> ${distractionCount}</div>
                    <div><strong>分心总时间:</strong> ${totalDistractionTime}秒</div>
                `;
                
                if (result.attention_record) {
                    trainingSummary.innerHTML += `
                        <div class="mt-3 mb-2">
                            <a href="${result.attention_record}" target="_blank" class="text-blue-600 hover:underline">查看注意力详细数据</a>
                        </div>
                    `;
                }
                
                if (result.emotion_record) {
                    trainingSummary.innerHTML += `
                        <div class="mb-2">
                            <a href="${result.emotion_record}" target="_blank" class="text-blue-600 hover:underline">查看情绪详细数据</a>
                        </div>
                    `;
                }
                
                // 显示保存记录模态框
                saveModal.classList.remove('hidden');
                saveModal.classList.add('flex');
            } else {
                alert('保存训练记录失败: ' + (result.message || '未知错误'));
            }
        } catch (error) {
            console.error('保存记录请求失败:', error);
            alert('保存训练记录失败，请检查网络连接');
        }
    });
    
    // 关闭保存记录模态框
    closeModalBtn.addEventListener('click', function() {
        saveModal.classList.add('hidden');
        saveModal.classList.remove('flex');
    });
    
    // 下载训练摘要
    downloadSummaryBtn.addEventListener('click', function() {
        const trainingSummary = document.getElementById('training-summary').innerText;
        const blob = new Blob([trainingSummary], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `训练摘要_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // 在页面加载完成后初始化第一题
    loadNewQuestion(1);
    
    // 默认禁用导航按钮，直到训练开始
    nextBtn.disabled = true;
    prevBtn.disabled = true;

    // 停止训练函数
    function stopTraining() {
        isTraining = false;
        
        // 计算训练时长
        const trainingEndTime = new Date();
        const trainingDuration = Math.floor((trainingEndTime - trainingStartTime) / 1000); // 秒
        
        // 更新按钮状态
        startTrainingBtn.disabled = false;
        stopTrainingBtn.disabled = true;
        nextBtn.disabled = true;
        prevBtn.disabled = true;
        
        // 更新状态显示
        updateAvatarStatus("训练已结束");
        document.getElementById('current-emotion').innerHTML = `
            <span class="text-4xl">😊</span>
            <p class="text-sm text-gray-700 mt-2">已停止检测</p>
            <p class="text-xs text-gray-500">训练结束</p>
        `;
        
        document.getElementById('attention-status').textContent = "训练已结束，可以查看训练报告";
        
        // 提示用户保存训练记录
        alert("训练已结束，您可以点击'保存记录'按钮保存本次训练结果。");
    }
    
    // 实现保存记录功能
    saveRecordsBtn.addEventListener('click', async function() {
        // 如果正在训练中，先停止训练
        if (isTraining) {
            stopTraining();
        }
        
        // 收集训练数据
        const trainingData = {
            correctAnswers: correctAnswers,
            totalQuestions: totalQuestions,
            accuracy: totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0,
            trainingDuration: trainingStartTime ? Math.floor((new Date() - trainingStartTime) / 1000) : 0,
            scene: document.querySelector('.scene-selected').getAttribute('data-scene'),
            distractionCount: distractionCount,
            distractionTime: totalDistractionTime
        };
        
        try {
            // 发送数据到后端保存
            const response = await fetch('/api/save_records', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trainingData)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // 生成训练摘要
                const trainingSummary = document.getElementById('training-summary');
                const currentScene = document.querySelector('.scene-selected').getAttribute('data-scene');
                const sceneLabels = {
                    'school': '学校场景',
                    'social': '社交场景',
                    'transport': '交通场景',
                    'food': '吃饭场景',
                    'family': '家庭关系场景'
                };
                
                // 计算训练时长
                let trainingDuration = trainingData.trainingDuration;
                
                // 准确率
                const accuracy = trainingData.accuracy;
                
                // 填充训练摘要
                trainingSummary.innerHTML = `
                    <div class="mb-2"><strong>训练场景:</strong> ${sceneLabels[currentScene]}</div>
                    <div class="mb-2"><strong>训练时长:</strong> ${Math.floor(trainingDuration / 60)}分${trainingDuration % 60}秒</div>
                    <div class="mb-2"><strong>答题数量:</strong> ${totalQuestions}</div>
                    <div class="mb-2"><strong>正确答题:</strong> ${correctAnswers}</div>
                    <div class="mb-2"><strong>正确率:</strong> ${accuracy}%</div>
                    <div class="mb-2"><strong>分心次数:</strong> ${distractionCount}</div>
                    <div><strong>分心总时间:</strong> ${totalDistractionTime}秒</div>
                `;
                
                if (result.attention_record) {
                    trainingSummary.innerHTML += `
                        <div class="mt-3 mb-2">
                            <a href="${result.attention_record}" target="_blank" class="text-blue-600 hover:underline">查看注意力详细数据</a>
                        </div>
                    `;
                }
                
                if (result.emotion_record) {
                    trainingSummary.innerHTML += `
                        <div class="mb-2">
                            <a href="${result.emotion_record}" target="_blank" class="text-blue-600 hover:underline">查看情绪详细数据</a>
                        </div>
                    `;
                }
                
                // 显示保存记录模态框
                saveModal.classList.remove('hidden');
                saveModal.classList.add('flex');
            } else {
                alert('保存训练记录失败: ' + (result.message || '未知错误'));
            }
        } catch (error) {
            console.error('保存记录请求失败:', error);
            alert('保存训练记录失败，请检查网络连接');
        }
    });

    // 在每次场景切换或训练停止时恢复虚拟形象
    function restoreVirtualAvatar() {
        const avatarImage = document.getElementById('avatar-image');
        const videoElement = document.getElementById('video');
        
        if (avatarImage && videoElement) {
            // 显示虚拟形象
            avatarImage.style.display = 'block';
            videoElement.classList.add('video-hidden');
            
            // 确保使用默认图片
            avatarImage.src = '/static/images/virtual.png';
        }
    }
});
