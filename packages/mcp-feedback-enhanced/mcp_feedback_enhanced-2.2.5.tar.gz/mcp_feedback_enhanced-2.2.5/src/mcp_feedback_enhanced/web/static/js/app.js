/**
 * 主要前端應用
 * ============
 * 
 * 處理 WebSocket 通信、分頁切換、圖片上傳、命令執行等功能
 */

class PersistentSettings {
    constructor() {
        this.settingsFile = 'ui_settings.json';
        this.storageKey = 'mcp_feedback_settings';
    }

    async saveSettings(settings) {
        try {
            // 嘗試保存到伺服器端
            const response = await fetch('/api/save-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                console.log('設定已保存到檔案');
            } else {
                throw new Error('伺服器端保存失敗');
            }
        } catch (error) {
            console.warn('無法保存到檔案，使用 localStorage:', error);
            // 備用方案：保存到 localStorage
            this.saveToLocalStorage(settings);
        }
    }

    async loadSettings() {
        try {
            // 嘗試從伺服器端載入
            const response = await fetch('/api/load-settings');
            if (response.ok) {
                const settings = await response.json();
                console.log('從檔案載入設定');
                return settings;
            } else {
                throw new Error('伺服器端載入失敗');
            }
        } catch (error) {
            console.warn('無法從檔案載入，使用 localStorage:', error);
            // 備用方案：從 localStorage 載入
            return this.loadFromLocalStorage();
        }
    }

    saveToLocalStorage(settings) {
        localStorage.setItem(this.storageKey, JSON.stringify(settings));
    }

    loadFromLocalStorage() {
        const saved = localStorage.getItem(this.storageKey);
        return saved ? JSON.parse(saved) : {};
    }

    async clearSettings() {
        try {
            // 清除伺服器端設定
            await fetch('/api/clear-settings', { method: 'POST' });
        } catch (error) {
            console.warn('無法清除伺服器端設定:', error);
        }
        
        // 清除 localStorage
        localStorage.removeItem(this.storageKey);
        
        // 也清除個別設定項目（向後兼容）
        localStorage.removeItem('layoutMode');
        localStorage.removeItem('autoClose');
        localStorage.removeItem('activeTab');
        localStorage.removeItem('language');
    }
}

class FeedbackApp {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.layoutMode = 'separate'; // 預設為分離模式
        this.autoClose = true; // 預設啟用自動關閉
        this.currentTab = 'feedback'; // 預設當前分頁
        this.persistentSettings = new PersistentSettings();
        this.images = []; // 初始化圖片陣列
        this.isConnected = false; // 初始化連接狀態
        this.websocket = null; // 初始化 WebSocket
        this.isHandlingPaste = false; // 防止重複處理貼上事件的標記

        // 圖片設定
        this.imageSizeLimit = 0; // 0 表示無限制
        this.enableBase64Detail = false;

        // 超時設定
        this.timeoutEnabled = false;
        this.timeoutDuration = 600; // 預設 10 分鐘
        this.timeoutTimer = null;
        this.countdownTimer = null;
        this.remainingSeconds = 0;
        
        // 立即檢查 DOM 狀態並初始化
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.init();
            });
        } else {
            // DOM 已經載入完成，立即初始化
            this.init();
        }
    }

    async init() {
        // 等待國際化系統加載完成
        if (window.i18nManager) {
            await window.i18nManager.init();
        }

        // 處理動態摘要內容
        this.processDynamicSummaryContent();

        // 設置 WebSocket 連接
        this.setupWebSocket();
        
        // 設置事件監聽器
        this.setupEventListeners();
        
        // 初始化分頁系統
        this.setupTabs();
        
        // 設置圖片上傳
        this.setupImageUpload();
        
        // 設置鍵盤快捷鍵
        this.setupKeyboardShortcuts();
        
        // 載入設定（使用 await）
        await this.loadSettings();

        // 初始化命令終端
        this.initCommandTerminal();

        // 確保合併模式狀態正確
        this.applyCombinedModeState();

        // 初始化超時控制
        this.setupTimeoutControl();

        // 如果啟用了超時，自動開始倒數計時（在設置載入後）
        this.startTimeoutIfEnabled();

        console.log('FeedbackApp 初始化完成');
    }

    processDynamicSummaryContent() {
        // 處理所有帶有 data-dynamic-content 屬性的元素
        const dynamicElements = document.querySelectorAll('[data-dynamic-content="aiSummary"]');
        
        dynamicElements.forEach(element => {
            const currentContent = element.textContent || element.innerHTML;
            
            // 檢查是否為測試摘要
            if (this.isTestSummary(currentContent)) {
                // 如果是測試摘要，使用翻譯系統的內容
                if (window.i18nManager) {
                    const translatedSummary = window.i18nManager.t('dynamic.aiSummary');
                    if (translatedSummary && translatedSummary !== 'dynamic.aiSummary') {
                        element.textContent = translatedSummary.trim();
                        console.log('已更新測試摘要為:', window.i18nManager.currentLanguage);
                    }
                }
            } else {
                // 如果不是測試摘要，清理原有內容的前導和尾隨空白
                element.textContent = currentContent.trim();
            }
        });
    }

    isTestSummary(content) {
        // 簡化的測試摘要檢測邏輯 - 檢查是否包含任何測試相關關鍵詞
        const testKeywords = [
            // 標題關鍵詞（任何語言版本）
            '測試 Web UI 功能', 'Test Web UI Functionality', '测试 Web UI 功能',
            '圖片預覽和視窗調整測試', 'Image Preview and Window Adjustment Test', '图片预览和窗口调整测试',
            
            // 功能測試項目關鍵詞
            '功能測試項目', 'Test Items', '功能测试项目',
            
            // 特殊標記
            '🎯 **功能測試項目', '🎯 **Test Items', '🎯 **功能测试项目',
            '📋 測試步驟', '📋 Test Steps', '📋 测试步骤',
            
            // 具體測試功能
            'WebSocket 即時通訊', 'WebSocket real-time communication', 'WebSocket 即时通讯',
            '智能 Ctrl+V', 'Smart Ctrl+V', '智能 Ctrl+V',
            
            // 測試提示詞
            '請測試這些功能', 'Please test these features', '请测试这些功能'
        ];
        
        // 只要包含任何一個測試關鍵詞就認為是測試摘要
        return testKeywords.some(keyword => content.includes(keyword));
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

        try {
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                this.isConnected = true;
                console.log('WebSocket 連接已建立');
                this.updateConnectionStatus(true);
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('WebSocket 連接已關閉');
                this.updateConnectionStatus(false);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket 錯誤:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('WebSocket 連接失敗:', error);
            this.updateConnectionStatus(false);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'command_output':
                this.appendCommandOutput(data.output);
                break;
            case 'command_complete':
                this.appendCommandOutput(`\n[命令完成，退出碼: ${data.exit_code}]\n`);
                this.enableCommandInput();
                break;
            case 'command_error':
                this.appendCommandOutput(`\n[錯誤: ${data.error}]\n`);
                this.enableCommandInput();
                break;
            case 'feedback_received':
                console.log('回饋已收到');
                // 顯示成功訊息
                this.showSuccessMessage();
                break;
            case 'session_timeout':
                console.log('會話超時:', data.message);
                this.handleSessionTimeout(data.message);
                break;
            default:
                console.log('未知的 WebSocket 消息:', data);
        }
    }

    showSuccessMessage() {
        const successMessage = window.i18nManager ? 
            window.i18nManager.t('feedback.success', '✅ 回饋提交成功！') :
            '✅ 回饋提交成功！';
        this.showMessage(successMessage, 'success');
    }

    handleSessionTimeout(message) {
        console.log('處理會話超時:', message);
        
        // 顯示超時訊息
        const timeoutMessage = message || (window.i18nManager ? 
            window.i18nManager.t('session.timeout', '⏰ 會話已超時，介面將自動關閉') :
            '⏰ 會話已超時，介面將自動關閉');
        
        this.showMessage(timeoutMessage, 'warning');
        
        // 禁用所有互動元素
        this.disableAllInputs();
        
        // 3秒後自動關閉頁面
        setTimeout(() => {
            try {
                window.close();
            } catch (e) {
                // 如果無法關閉視窗（可能因為安全限制），重新載入頁面
                console.log('無法關閉視窗，重新載入頁面');
                window.location.reload();
            }
        }, 3000);
    }

    disableAllInputs() {
        // 禁用所有輸入元素
        const inputs = document.querySelectorAll('input, textarea, button');
        inputs.forEach(input => {
            input.disabled = true;
            input.style.opacity = '0.5';
        });
        
        // 特別處理提交和取消按鈕
        const submitBtn = document.getElementById('submitBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        
        if (submitBtn) {
            submitBtn.textContent = '⏰ 已超時';
            submitBtn.disabled = true;
        }
        
        if (cancelBtn) {
            cancelBtn.textContent = '關閉中...';
            cancelBtn.disabled = true;
        }
    }

    updateConnectionStatus(connected) {
        // 更新連接狀態指示器
        const elements = document.querySelectorAll('.connection-indicator');
        elements.forEach(el => {
            el.textContent = connected ? '✅ 已連接' : '❌ 未連接';
            el.className = `connection-indicator ${connected ? 'connected' : 'disconnected'}`;
        });

        // 更新命令執行按鈕狀態
        const runCommandBtn = document.getElementById('runCommandBtn');
        if (runCommandBtn) {
            runCommandBtn.disabled = !connected;
            runCommandBtn.textContent = connected ? '▶️ 執行' : '❌ 未連接';
        }
    }

    setupEventListeners() {
        // 提交回饋按鈕
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitFeedback());
        }

        // 取消按鈕
        const cancelBtn = document.getElementById('cancelBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelFeedback());
        }

        // 執行命令按鈕
        const runCommandBtn = document.getElementById('runCommandBtn');
        if (runCommandBtn) {
            runCommandBtn.addEventListener('click', () => this.runCommand());
        }

        // 命令輸入框 Enter 事件 - 修正為使用新的 input 元素
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            commandInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.runCommand();
                }
            });
        }

        // 設置貼上監聽器
        this.setupPasteListener();
        
        // 設定切換
        this.setupSettingsListeners();

        // 設定重置按鈕（如果存在）
        const resetSettingsBtn = document.getElementById('resetSettingsBtn');
        if (resetSettingsBtn) {
            resetSettingsBtn.addEventListener('click', () => this.resetSettings());
        }

        // 圖片設定監聽器
        this.setupImageSettingsListeners();
    }

    setupSettingsListeners() {
        // 設置佈局模式單選按鈕監聽器
        const layoutModeRadios = document.querySelectorAll('input[name="layoutMode"]');
        layoutModeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.setLayoutMode(e.target.value);
                }
            });
        });

        // 設置自動關閉開關監聽器
        const autoCloseToggle = document.getElementById('autoCloseToggle');
        if (autoCloseToggle) {
            autoCloseToggle.addEventListener('click', () => {
                this.toggleAutoClose();
            });
        }

        // 設置語言選擇器
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(option => {
            option.addEventListener('click', () => {
                const lang = option.getAttribute('data-lang');
                this.setLanguage(lang);
            });
        });
    }

    setupImageSettingsListeners() {
        // 圖片大小限制設定 - 原始分頁
        const imageSizeLimit = document.getElementById('imageSizeLimit');
        if (imageSizeLimit) {
            imageSizeLimit.addEventListener('change', (e) => {
                this.imageSizeLimit = parseInt(e.target.value);
                this.saveSettings();
                this.syncImageSettings();
            });
        }

        // Base64 詳細模式設定 - 原始分頁
        const enableBase64Detail = document.getElementById('enableBase64Detail');
        if (enableBase64Detail) {
            enableBase64Detail.addEventListener('change', (e) => {
                this.enableBase64Detail = e.target.checked;
                this.saveSettings();
                this.syncImageSettings();
            });
        }

        // 圖片大小限制設定 - 合併模式
        const combinedImageSizeLimit = document.getElementById('combinedImageSizeLimit');
        if (combinedImageSizeLimit) {
            combinedImageSizeLimit.addEventListener('change', (e) => {
                this.imageSizeLimit = parseInt(e.target.value);
                this.saveSettings();
                this.syncImageSettings();
            });
        }

        // Base64 詳細模式設定 - 合併模式
        const combinedEnableBase64Detail = document.getElementById('combinedEnableBase64Detail');
        if (combinedEnableBase64Detail) {
            combinedEnableBase64Detail.addEventListener('change', (e) => {
                this.enableBase64Detail = e.target.checked;
                this.saveSettings();
                this.syncImageSettings();
            });
        }

        // 相容性提示按鈕 - 原始分頁
        const enableBase64Hint = document.getElementById('enableBase64Hint');
        if (enableBase64Hint) {
            enableBase64Hint.addEventListener('click', () => {
                this.enableBase64Detail = true;
                this.saveSettings();
                this.syncImageSettings();
                this.hideCompatibilityHint();
            });
        }

        // 相容性提示按鈕 - 合併模式
        const combinedEnableBase64Hint = document.getElementById('combinedEnableBase64Hint');
        if (combinedEnableBase64Hint) {
            combinedEnableBase64Hint.addEventListener('click', () => {
                this.enableBase64Detail = true;
                this.saveSettings();
                this.syncImageSettings();
                this.hideCompatibilityHint();
            });
        }
    }

    syncImageSettings() {
        // 同步圖片大小限制設定
        const imageSizeLimit = document.getElementById('imageSizeLimit');
        const combinedImageSizeLimit = document.getElementById('combinedImageSizeLimit');

        if (imageSizeLimit) {
            imageSizeLimit.value = this.imageSizeLimit;
        }
        if (combinedImageSizeLimit) {
            combinedImageSizeLimit.value = this.imageSizeLimit;
        }

        // 同步 Base64 詳細模式設定
        const enableBase64Detail = document.getElementById('enableBase64Detail');
        const combinedEnableBase64Detail = document.getElementById('combinedEnableBase64Detail');

        if (enableBase64Detail) {
            enableBase64Detail.checked = this.enableBase64Detail;
        }
        if (combinedEnableBase64Detail) {
            combinedEnableBase64Detail.checked = this.enableBase64Detail;
        }
    }

    showCompatibilityHint() {
        const compatibilityHint = document.getElementById('compatibilityHint');
        const combinedCompatibilityHint = document.getElementById('combinedCompatibilityHint');

        if (compatibilityHint) {
            compatibilityHint.style.display = 'flex';
        }
        if (combinedCompatibilityHint) {
            combinedCompatibilityHint.style.display = 'flex';
        }
    }

    hideCompatibilityHint() {
        const compatibilityHint = document.getElementById('compatibilityHint');
        const combinedCompatibilityHint = document.getElementById('combinedCompatibilityHint');

        if (compatibilityHint) {
            compatibilityHint.style.display = 'none';
        }
        if (combinedCompatibilityHint) {
            combinedCompatibilityHint.style.display = 'none';
        }
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');

                // 移除所有活躍狀態
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));

                // 添加活躍狀態
                button.classList.add('active');
                const targetContent = document.getElementById(`tab-${targetTab}`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }

                // 保存當前分頁
                localStorage.setItem('activeTab', targetTab);
            });
        });

        // 恢復上次的活躍分頁
        const savedTab = localStorage.getItem('activeTab');
        if (savedTab) {
            const savedButton = document.querySelector(`[data-tab="${savedTab}"]`);
            if (savedButton) {
                savedButton.click();
            }
        }
    }

    setupImageUpload() {
        const imageUploadArea = document.getElementById('imageUploadArea');
        const imageInput = document.getElementById('imageInput');
        const imagePreviewContainer = document.getElementById('imagePreviewContainer');

        if (!imageUploadArea || !imageInput || !imagePreviewContainer) {
            return;
        }

        // 原始分頁的圖片上傳
        this.setupImageUploadForArea(imageUploadArea, imageInput, imagePreviewContainer);

        // 合併模式的圖片上傳
        const combinedImageUploadArea = document.getElementById('combinedImageUploadArea');
        const combinedImageInput = document.getElementById('combinedImageInput');
        const combinedImagePreviewContainer = document.getElementById('combinedImagePreviewContainer');

        if (combinedImageUploadArea && combinedImageInput && combinedImagePreviewContainer) {
            this.setupImageUploadForArea(combinedImageUploadArea, combinedImageInput, combinedImagePreviewContainer);
        }
    }

    setupImageUploadForArea(uploadArea, input, previewContainer) {
        // 點擊上傳區域
        uploadArea.addEventListener('click', () => {
            input.click();
        });

        // 文件選擇
        input.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // 拖放事件
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files);
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter 或 Cmd+Enter 提交回饋
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.submitFeedback();
            }

            // ESC 取消
            if (e.key === 'Escape') {
                this.cancelFeedback();
            }
        });

        // 設置 Ctrl+V 貼上圖片監聽器
        this.setupPasteListener();
    }

    setupPasteListener() {
        document.addEventListener('paste', (e) => {
            // 檢查是否在回饋文字框中
            const feedbackText = document.getElementById('feedbackText');
            const combinedFeedbackText = document.getElementById('combinedFeedbackText');
            
            const isInFeedbackInput = document.activeElement === feedbackText || 
                                    document.activeElement === combinedFeedbackText;
            
            if (isInFeedbackInput) {
                console.log('偵測到在回饋輸入框中貼上');
                this.handlePasteEvent(e);
            }
        });
    }

    handlePasteEvent(e) {
        if (this.isHandlingPaste) {
            console.log('Paste event already being handled, skipping subsequent call.');
            return;
        }
        this.isHandlingPaste = true;

        const clipboardData = e.clipboardData || window.clipboardData;
        if (!clipboardData) {
            this.isHandlingPaste = false; 
            return;
        }

        const items = clipboardData.items;
        let hasImages = false;

        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            
            if (item.type.indexOf('image') !== -1) {
                hasImages = true;
                e.preventDefault(); 
                
                const file = item.getAsFile();
                if (file) {
                    console.log('從剪貼簿貼上圖片:', file.name, file.type);
                    this.addImage(file);
                    break; 
                }
            }
        }

        if (hasImages) {
            console.log('已處理剪貼簿圖片');
        }

        setTimeout(() => {
            this.isHandlingPaste = false;
        }, 50);
    }

    setLayoutMode(mode) {
        if (this.layoutMode === mode) return;
        
        this.layoutMode = mode;
        
        // 保存設定到持久化存儲
        this.saveSettings();
        
        // 只更新分頁可見性，不強制切換分頁
        this.updateTabVisibility();
        
        // 數據同步
        if (mode === 'combined-vertical' || mode === 'combined-horizontal') {
            // 同步數據到合併模式
            this.syncDataToCombinedMode();
        } else {
            // 切換到分離模式時，同步數據回原始分頁
            this.syncDataFromCombinedMode();
        }
        
        // 更新合併分頁的佈局樣式
        this.updateCombinedModeLayout();
        
        console.log('佈局模式已切換至:', mode);
    }

    updateTabVisibility() {
        const feedbackTab = document.querySelector('[data-tab="feedback"]');
        const summaryTab = document.querySelector('[data-tab="summary"]');
        const combinedTab = document.querySelector('[data-tab="combined"]');

        if (this.layoutMode === 'separate') {
            // 分離模式：顯示原本的分頁，隱藏合併分頁
            if (feedbackTab) feedbackTab.classList.remove('hidden');
            if (summaryTab) summaryTab.classList.remove('hidden');
            if (combinedTab) {
                combinedTab.classList.add('hidden');
                // 只有在當前就在合併分頁時才切換到其他分頁
                if (combinedTab.classList.contains('active')) {
                    this.switchToFeedbackTab();
                }
            }
        } else {
            // 合併模式：隱藏原本的分頁，顯示合併分頁
            if (feedbackTab) feedbackTab.classList.add('hidden');
            if (summaryTab) summaryTab.classList.add('hidden');
            if (combinedTab) {
                combinedTab.classList.remove('hidden');
                // 不要強制切換到合併分頁，讓用戶手動選擇
            }
        }
    }

    switchToFeedbackTab() {
        // 切換到回饋分頁的輔助方法
        const feedbackTab = document.querySelector('[data-tab="feedback"]');
        if (feedbackTab) {
            // 移除所有分頁按鈕的活躍狀態
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            // 移除所有分頁內容的活躍狀態
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // 設定回饋分頁為活躍
            feedbackTab.classList.add('active');
            document.getElementById('tab-feedback').classList.add('active');
            
            console.log('已切換到回饋分頁');
        }
    }

    updateCombinedModeLayout() {
        const combinedTabContent = document.getElementById('tab-combined');
        if (!combinedTabContent) {
            console.warn('找不到合併分頁元素 #tab-combined');
            return;
        }

        // 移除所有佈局類
        combinedTabContent.classList.remove('combined-horizontal', 'combined-vertical');

        // 根據當前模式添加對應的佈局類
        if (this.layoutMode === 'combined-horizontal') {
            combinedTabContent.classList.add('combined-horizontal');
        } else if (this.layoutMode === 'combined-vertical') {
            combinedTabContent.classList.add('combined-vertical');
        }
    }

    setLanguage(language) {
        // 更新語言選擇器的活躍狀態
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(option => {
            option.classList.remove('active');
            if (option.getAttribute('data-lang') === language) {
                option.classList.add('active');
            }
        });

        // 調用國際化管理器
        if (window.i18nManager) {
            window.i18nManager.setLanguage(language);
            
            // 語言切換後重新處理動態摘要內容
            setTimeout(() => {
                this.processDynamicSummaryContent();
            }, 200); // 增加延遲時間確保翻譯加載完成
        }

        console.log('語言已切換至:', language);
    }

    handleFileSelection(files) {
        for (let file of files) {
            if (file.type.startsWith('image/')) {
                this.addImage(file);
            }
        }
    }

    addImage(file) {
        // 檢查圖片大小限制
        if (this.imageSizeLimit > 0 && file.size > this.imageSizeLimit) {
            const limitMB = this.imageSizeLimit / (1024 * 1024);
            const fileMB = file.size / (1024 * 1024);

            const message = window.i18nManager ?
                window.i18nManager.t('images.sizeLimitExceeded', {
                    filename: file.name,
                    size: fileMB.toFixed(1) + 'MB',
                    limit: limitMB.toFixed(0) + 'MB'
                }) :
                `圖片 ${file.name} 大小為 ${fileMB.toFixed(1)}MB，超過 ${limitMB.toFixed(0)}MB 限制！`;

            const advice = window.i18nManager ?
                window.i18nManager.t('images.sizeLimitExceededAdvice') :
                '建議使用圖片編輯軟體壓縮後再上傳，或調整圖片大小限制設定。';

            alert(message + '\n\n' + advice);

            // 顯示相容性提示（如果圖片上傳失敗）
            this.showCompatibilityHint();
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                name: file.name,
                data: e.target.result.split(',')[1], // 移除 data:image/...;base64, 前綴
                size: file.size,
                type: file.type,
                preview: e.target.result
            };

            this.images.push(imageData);
            this.updateImagePreview();
        };
        reader.readAsDataURL(file);
    }

    updateImagePreview() {
        // 更新原始分頁的圖片預覽
        this.updateImagePreviewForContainer('imagePreviewContainer', 'imageUploadArea');

        // 更新合併模式的圖片預覽
        this.updateImagePreviewForContainer('combinedImagePreviewContainer', 'combinedImageUploadArea');
    }

    updateImagePreviewForContainer(containerId, uploadAreaId) {
        const container = document.getElementById(containerId);
        const uploadArea = document.getElementById(uploadAreaId);
        if (!container || !uploadArea) return;

        container.innerHTML = '';

        // 更新上傳區域的樣式
        if (this.images.length > 0) {
            uploadArea.classList.add('has-images');
        } else {
            uploadArea.classList.remove('has-images');
        }

        this.images.forEach((image, index) => {
            const preview = document.createElement('div');
            preview.className = 'image-preview';
            preview.innerHTML = `
                <img src="${image.preview}" alt="${image.name}">
                <button class="image-remove" onclick="feedbackApp.removeImage(${index})">×</button>
            `;
            container.appendChild(preview);
        });
    }

    removeImage(index) {
        this.images.splice(index, 1);
        this.updateImagePreview();
    }

    runCommand() {
        const commandInput = document.getElementById('commandInput');
        const command = commandInput?.value.trim();

        if (!command) {
            this.appendCommandOutput('⚠️ 請輸入命令\n');
            return;
        }

        if (!this.isConnected) {
            this.appendCommandOutput('❌ WebSocket 未連接，無法執行命令\n');
            return;
        }

        // 禁用輸入和按鈕
        this.disableCommandInput();

        // 顯示執行的命令，使用 terminal 風格
        this.appendCommandOutput(`$ ${command}\n`);

        // 發送命令
        try {
            this.websocket.send(JSON.stringify({
                type: 'run_command',
                command: command
            }));

            // 清空輸入框
            commandInput.value = '';

            // 顯示正在執行的狀態
            this.appendCommandOutput('[正在執行...]\n');

        } catch (error) {
            this.appendCommandOutput(`❌ 發送命令失敗: ${error.message}\n`);
            this.enableCommandInput();
        }
    }

    disableCommandInput() {
        const commandInput = document.getElementById('commandInput');
        const runCommandBtn = document.getElementById('runCommandBtn');

        if (commandInput) {
            commandInput.disabled = true;
            commandInput.style.opacity = '0.6';
        }
        if (runCommandBtn) {
            runCommandBtn.disabled = true;
            runCommandBtn.textContent = '⏳ 執行中...';
        }
    }

    enableCommandInput() {
        const commandInput = document.getElementById('commandInput');
        const runCommandBtn = document.getElementById('runCommandBtn');

        if (commandInput) {
            commandInput.disabled = false;
            commandInput.style.opacity = '1';
            commandInput.focus(); // 自動聚焦到輸入框
        }
        if (runCommandBtn) {
            runCommandBtn.disabled = false;
            runCommandBtn.textContent = '▶️ 執行';
        }
    }

    appendCommandOutput(text) {
        const output = document.getElementById('commandOutput');
        if (output) {
            output.textContent += text;
            output.scrollTop = output.scrollHeight;

            // 添加時間戳（可選）
            if (text.includes('[命令完成') || text.includes('[錯誤:')) {
                const timestamp = new Date().toLocaleTimeString();
                output.textContent += `[${timestamp}]\n`;
            }
        }
    }

    submitFeedback() {
        let feedbackText;

        // 根據當前模式選擇正確的輸入框
        if (this.layoutMode === 'combined-vertical' || this.layoutMode === 'combined-horizontal') {
            const combinedFeedbackInput = document.getElementById('combinedFeedbackText');
            feedbackText = combinedFeedbackInput?.value.trim() || '';
        } else {
            const feedbackInput = document.getElementById('feedbackText');
            feedbackText = feedbackInput?.value.trim() || '';
        }

        const feedback = feedbackText;

        if (!feedback && this.images.length === 0) {
            alert('請提供回饋文字或上傳圖片');
            return;
        }

        if (!this.isConnected) {
            alert('WebSocket 未連接');
            return;
        }

        // 準備圖片數據
        const imageData = this.images.map(img => ({
            name: img.name,
            data: img.data,
            size: img.size,
            type: img.type
        }));

        // 發送回饋（包含圖片設定）
        this.websocket.send(JSON.stringify({
            type: 'submit_feedback',
            feedback: feedback,
            images: imageData,
            settings: {
                image_size_limit: this.imageSizeLimit,
                enable_base64_detail: this.enableBase64Detail
            }
        }));

        console.log('回饋已提交');
        
        // 根據設定決定是否自動關閉頁面
        if (this.autoClose) {
            // 稍微延遲一下讓用戶看到提交成功的反饋
            setTimeout(() => {
                window.close();
            }, 1000);
        }
    }

    cancelFeedback() {
        if (confirm('確定要取消回饋嗎？')) {
            window.close();
        }
    }

    toggleAutoClose() {
        this.autoClose = !this.autoClose;

        const toggle = document.getElementById('autoCloseToggle');
        if (toggle) {
            toggle.classList.toggle('active', this.autoClose);
        }

        // 保存設定到持久化存儲
        this.saveSettings();

        console.log('自動關閉頁面已', this.autoClose ? '啟用' : '停用');
    }

    syncDataToCombinedMode() {
        // 同步回饋文字
        const feedbackText = document.getElementById('feedbackText');
        const combinedFeedbackText = document.getElementById('combinedFeedbackText');
        if (feedbackText && combinedFeedbackText) {
            combinedFeedbackText.value = feedbackText.value;
        }

        // 同步摘要內容
        const summaryContent = document.getElementById('summaryContent');
        const combinedSummaryContent = document.getElementById('combinedSummaryContent');
        if (summaryContent && combinedSummaryContent) {
            combinedSummaryContent.textContent = summaryContent.textContent;
        }
    }

    syncDataFromCombinedMode() {
        // 同步回饋文字
        const feedbackText = document.getElementById('feedbackText');
        const combinedFeedbackText = document.getElementById('combinedFeedbackText');
        if (feedbackText && combinedFeedbackText) {
            feedbackText.value = combinedFeedbackText.value;
        }
    }

    syncLanguageSelector() {
        // 同步語言選擇器的狀態
        if (window.i18nManager) {
            const currentLang = window.i18nManager.currentLanguage;
            
            // 更新現代化語言選擇器
            const languageOptions = document.querySelectorAll('.language-option');
            languageOptions.forEach(option => {
                const lang = option.getAttribute('data-lang');
                option.classList.toggle('active', lang === currentLang);
            });
        }
    }

    async loadSettings() {
        try {
            // 使用持久化設定系統載入設定
            const settings = await this.persistentSettings.loadSettings();
            
            // 載入佈局模式設定
            if (settings.layoutMode && ['separate', 'combined-vertical', 'combined-horizontal'].includes(settings.layoutMode)) {
                this.layoutMode = settings.layoutMode;
            } else {
                // 嘗試從舊的 localStorage 載入（向後兼容）
                const savedLayoutMode = localStorage.getItem('layoutMode');
                if (savedLayoutMode && ['separate', 'combined-vertical', 'combined-horizontal'].includes(savedLayoutMode)) {
                    this.layoutMode = savedLayoutMode;
                } else {
                    this.layoutMode = 'separate'; // 預設為分離模式
                }
            }

            // 更新佈局模式單選按鈕狀態
            const layoutRadios = document.querySelectorAll('input[name="layoutMode"]');
            layoutRadios.forEach((radio, index) => {
                radio.checked = radio.value === this.layoutMode;
            });

            // 載入自動關閉設定
            if (settings.autoClose !== undefined) {
                this.autoClose = settings.autoClose;
            } else {
                // 嘗試從舊的 localStorage 載入（向後兼容）
                const savedAutoClose = localStorage.getItem('autoClose');
                if (savedAutoClose !== null) {
                    this.autoClose = savedAutoClose === 'true';
                } else {
                    this.autoClose = true; // 預設啟用
                }
            }

            // 更新自動關閉開關狀態
            const autoCloseToggle = document.getElementById('autoCloseToggle');
            if (autoCloseToggle) {
                autoCloseToggle.classList.toggle('active', this.autoClose);
            }

            // 載入圖片設定
            if (settings.imageSizeLimit !== undefined) {
                this.imageSizeLimit = settings.imageSizeLimit;
            } else {
                this.imageSizeLimit = 0; // 預設無限制
            }

            if (settings.enableBase64Detail !== undefined) {
                this.enableBase64Detail = settings.enableBase64Detail;
            } else {
                this.enableBase64Detail = false; // 預設關閉
            }

            // 載入超時設定
            if (settings.timeoutEnabled !== undefined) {
                this.timeoutEnabled = settings.timeoutEnabled;
            } else {
                this.timeoutEnabled = false; // 預設關閉
            }

            if (settings.timeoutDuration !== undefined) {
                this.timeoutDuration = settings.timeoutDuration;
            } else {
                this.timeoutDuration = 600; // 預設 10 分鐘
            }

            // 更新超時 UI
            this.updateTimeoutUI();

            // 同步圖片設定到 UI
            this.syncImageSettings();

            // 確保語言選擇器與當前語言同步
            this.syncLanguageSelector();

            // 應用佈局模式設定
            this.applyCombinedModeState();

            // 如果是合併模式，同步數據
            if (this.layoutMode === 'combined-vertical' || this.layoutMode === 'combined-horizontal') {
                this.syncDataToCombinedMode();
            }

            console.log('設定已載入:', {
                layoutMode: this.layoutMode,
                autoClose: this.autoClose,
                currentLanguage: window.i18nManager?.currentLanguage,
                source: settings.layoutMode ? 'persistent' : 'localStorage'
            });
            
        } catch (error) {
            console.warn('載入設定時發生錯誤:', error);
            // 使用預設設定
            this.layoutMode = 'separate';
            this.autoClose = true;
            
            // 仍然需要更新 UI 狀態
            const layoutRadios = document.querySelectorAll('input[name="layoutMode"]');
            layoutRadios.forEach((radio, index) => {
                radio.checked = radio.value === this.layoutMode;
            });
            
            const autoCloseToggle = document.getElementById('autoCloseToggle');
            if (autoCloseToggle) {
                autoCloseToggle.classList.toggle('active', this.autoClose);
            }
        }
    }

    applyCombinedModeState() {
        // 更新分頁可見性
        this.updateTabVisibility();
        
        // 更新合併分頁的佈局樣式
        if (this.layoutMode !== 'separate') {
            this.updateCombinedModeLayout();
        }
    }

    initCommandTerminal() {
        // 使用翻譯的歡迎信息
        if (window.i18nManager) {
            const welcomeTemplate = window.i18nManager.t('dynamic.terminalWelcome');
            if (welcomeTemplate && welcomeTemplate !== 'dynamic.terminalWelcome') {
                const welcomeMessage = welcomeTemplate.replace('{sessionId}', this.sessionId);
                this.appendCommandOutput(welcomeMessage);
                return;
            }
        }

        // 回退到預設歡迎信息（如果翻譯不可用）
        const welcomeMessage = `Welcome to Interactive Feedback Terminal
========================================
Project Directory: ${this.sessionId}
Enter commands and press Enter or click Execute button
Supported commands: ls, dir, pwd, cat, type, etc.

$ `;
        this.appendCommandOutput(welcomeMessage);
    }

    async resetSettings() {
        // 確認重置
        const confirmMessage = window.i18nManager ? 
            window.i18nManager.t('settings.resetConfirm', '確定要重置所有設定嗎？這將清除所有已保存的偏好設定。') :
            '確定要重置所有設定嗎？這將清除所有已保存的偏好設定。';
            
        if (!confirm(confirmMessage)) {
            return;
        }

        try {
            // 使用持久化設定系統清除設定
            await this.persistentSettings.clearSettings();
            
            // 重置本地變數
            this.layoutMode = 'separate';
            this.autoClose = true;
            this.imageSizeLimit = 0;
            this.enableBase64Detail = false;
            this.timeoutEnabled = false;
            this.timeoutDuration = 600;

            // 更新佈局模式單選按鈕狀態
            const layoutRadios = document.querySelectorAll('input[name="layoutMode"]');
            layoutRadios.forEach((radio, index) => {
                radio.checked = radio.value === this.layoutMode;
            });

            // 更新自動關閉開關狀態
            const autoCloseToggle = document.getElementById('autoCloseToggle');
            if (autoCloseToggle) {
                autoCloseToggle.classList.toggle('active', this.autoClose);
            }

            // 同步圖片設定到 UI
            this.syncImageSettings();

            // 更新超時 UI
            this.updateTimeoutUI();
            this.stopTimeout();

            // 確保語言選擇器與當前語言同步
            this.syncLanguageSelector();

            // 應用佈局模式設定
            this.applyCombinedModeState();

            // 切換到回饋分頁
            this.switchToFeedbackTab();

            // 顯示成功訊息
            const successMessage = window.i18nManager ? 
                window.i18nManager.t('settings.resetSuccess', '設定已重置為預設值') :
                '設定已重置為預設值';
            
            this.showMessage(successMessage, 'success');

            console.log('設定已重置');
            
        } catch (error) {
            console.error('重置設定時發生錯誤:', error);
            
            // 顯示錯誤訊息
            const errorMessage = window.i18nManager ? 
                window.i18nManager.t('settings.resetError', '重置設定時發生錯誤') :
                '重置設定時發生錯誤';
                
            this.showMessage(errorMessage, 'error');
        }
    }

    showMessage(text, type = 'info') {
        // 確保動畫樣式已添加
        if (!document.getElementById('slideInAnimation')) {
            const style = document.createElement('style');
            style.id = 'slideInAnimation';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        // 創建訊息提示
        const message = document.createElement('div');
        const colors = {
            success: 'var(--success-color)',
            error: 'var(--error-color)',
            warning: 'var(--warning-color)',
            info: 'var(--info-color)'
        };
        
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        `;
        message.textContent = text;
        
        document.body.appendChild(message);
        
        // 3秒後移除訊息
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 3000);
    }

    setupTimeoutControl() {
        // 設置超時開關監聽器
        const timeoutToggle = document.getElementById('timeoutToggle');
        if (timeoutToggle) {
            timeoutToggle.addEventListener('click', () => {
                this.toggleTimeout();
            });
        }

        // 設置超時時間輸入監聽器
        const timeoutDuration = document.getElementById('timeoutDuration');
        if (timeoutDuration) {
            timeoutDuration.addEventListener('change', (e) => {
                this.setTimeoutDuration(parseInt(e.target.value));
            });
        }

        // 更新界面狀態
        this.updateTimeoutUI();
    }

    startTimeoutIfEnabled() {
        // 如果啟用了超時，自動開始倒數計時
        if (this.timeoutEnabled) {
            this.startTimeout();
            console.log('頁面載入時自動開始倒數計時');
        }
    }

    toggleTimeout() {
        this.timeoutEnabled = !this.timeoutEnabled;
        this.updateTimeoutUI();
        this.saveSettings();

        if (this.timeoutEnabled) {
            this.startTimeout();
        } else {
            this.stopTimeout();
        }

        console.log('超時功能已', this.timeoutEnabled ? '啟用' : '停用');
    }

    setTimeoutDuration(seconds) {
        if (seconds >= 30 && seconds <= 7200) {
            this.timeoutDuration = seconds;
            this.saveSettings();

            // 如果正在倒數，重新開始
            if (this.timeoutEnabled && this.timeoutTimer) {
                this.startTimeout();
            }

            console.log('超時時間設置為', seconds, '秒');
        }
    }

    updateTimeoutUI() {
        const timeoutToggle = document.getElementById('timeoutToggle');
        const timeoutDuration = document.getElementById('timeoutDuration');
        const countdownDisplay = document.getElementById('countdownDisplay');

        if (timeoutToggle) {
            timeoutToggle.classList.toggle('active', this.timeoutEnabled);
        }

        if (timeoutDuration) {
            timeoutDuration.value = this.timeoutDuration;
        }

        if (countdownDisplay) {
            countdownDisplay.style.display = this.timeoutEnabled ? 'flex' : 'none';
        }
    }

    startTimeout() {
        this.stopTimeout(); // 先停止現有的計時器

        this.remainingSeconds = this.timeoutDuration;

        // 開始主要的超時計時器
        this.timeoutTimer = setTimeout(() => {
            this.handleTimeout();
        }, this.timeoutDuration * 1000);

        // 開始倒數顯示計時器
        this.countdownTimer = setInterval(() => {
            this.updateCountdownDisplay();
        }, 1000);

        this.updateCountdownDisplay();
        console.log('開始倒數計時：', this.timeoutDuration, '秒');
    }

    stopTimeout() {
        if (this.timeoutTimer) {
            clearTimeout(this.timeoutTimer);
            this.timeoutTimer = null;
        }

        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }

        const countdownTimer = document.getElementById('countdownTimer');
        if (countdownTimer) {
            countdownTimer.textContent = '--:--';
            countdownTimer.className = 'countdown-timer';
        }

        console.log('倒數計時已停止');
    }

    updateCountdownDisplay() {
        this.remainingSeconds--;

        const countdownTimer = document.getElementById('countdownTimer');
        if (countdownTimer) {
            if (this.remainingSeconds <= 0) {
                countdownTimer.textContent = '00:00';
                countdownTimer.className = 'countdown-timer danger';
            } else {
                const minutes = Math.floor(this.remainingSeconds / 60);
                const seconds = this.remainingSeconds % 60;
                const timeText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                countdownTimer.textContent = timeText;

                // 根據剩餘時間調整樣式
                if (this.remainingSeconds <= 60) {
                    countdownTimer.className = 'countdown-timer danger';
                } else if (this.remainingSeconds <= 300) {
                    countdownTimer.className = 'countdown-timer warning';
                } else {
                    countdownTimer.className = 'countdown-timer';
                }
            }
        }

        if (this.remainingSeconds <= 0) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }
    }

    handleTimeout() {
        console.log('用戶設置的超時時間已到，自動關閉介面');

        // 通知後端用戶超時
        this.notifyUserTimeout();

        // 顯示超時訊息
        const timeoutMessage = window.i18nManager ?
            window.i18nManager.t('timeout.expired', '⏰ 時間已到，介面將自動關閉') :
            '⏰ 時間已到，介面將自動關閉';

        this.showMessage(timeoutMessage, 'warning');

        // 禁用所有互動元素
        this.disableAllInputs();

        // 3秒後自動關閉頁面
        setTimeout(() => {
            try {
                window.close();
            } catch (e) {
                console.log('無法關閉視窗，重新載入頁面');
                window.location.reload();
            }
        }, 3000);
    }

    notifyUserTimeout() {
        // 通過 WebSocket 通知後端用戶設置的超時已到
        if (this.websocket && this.isConnected) {
            try {
                this.websocket.send(JSON.stringify({
                    type: 'user_timeout',
                    message: '用戶設置的超時時間已到'
                }));
                console.log('已通知後端用戶超時');
            } catch (error) {
                console.log('通知後端超時失敗:', error);
            }
        }
    }

    disableAllInputs() {
        // 禁用所有輸入元素
        const inputs = document.querySelectorAll('input, textarea, button, select');
        inputs.forEach(input => {
            input.disabled = true;
        });

        // 禁用超時控制
        const timeoutToggle = document.getElementById('timeoutToggle');
        if (timeoutToggle) {
            timeoutToggle.style.pointerEvents = 'none';
            timeoutToggle.style.opacity = '0.5';
        }

        console.log('所有輸入元素已禁用');
    }

    async saveSettings() {
        try {
            const settings = {
                layoutMode: this.layoutMode,
                autoClose: this.autoClose,
                imageSizeLimit: this.imageSizeLimit,
                enableBase64Detail: this.enableBase64Detail,
                timeoutEnabled: this.timeoutEnabled,
                timeoutDuration: this.timeoutDuration,
                language: window.i18nManager?.currentLanguage || 'zh-TW',
                activeTab: localStorage.getItem('activeTab'),
                lastSaved: new Date().toISOString()
            };

            await this.persistentSettings.saveSettings(settings);

            // 同時保存到 localStorage 作為備用（向後兼容）
            localStorage.setItem('layoutMode', this.layoutMode);
            localStorage.setItem('autoClose', this.autoClose.toString());
            localStorage.setItem('imageSizeLimit', this.imageSizeLimit.toString());
            localStorage.setItem('enableBase64Detail', this.enableBase64Detail.toString());

            console.log('設定已保存:', settings);
        } catch (error) {
            console.warn('保存設定時發生錯誤:', error);
        }
    }
}

// 全域函數，供 HTML 中的 onclick 使用
window.feedbackApp = null; 