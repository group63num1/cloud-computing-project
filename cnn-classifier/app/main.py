from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.model_handler import classifier
    MODEL_LOADED = True
except Exception as e:
    print(f"模型加载失败: {e}")
    MODEL_LOADED = False

app = FastAPI(
    title="CNN图像分类API服务",
    description="基于ResNet18的深度学习图像分类服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    """提供Web界面"""
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CNN图像分类服务</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 800px;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .upload-area {
                border: 3px dashed #4facfe;
                border-radius: 15px;
                padding: 60px 30px;
                text-align: center;
                background: #f8f9fa;
                margin-bottom: 30px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .upload-area:hover {
                background: #e9ecef;
                border-color: #667eea;
            }
            
            .upload-icon {
                font-size: 60px;
                color: #4facfe;
                margin-bottom: 20px;
            }
            
            .upload-text {
                font-size: 1.2rem;
                color: #495057;
                margin-bottom: 10px;
            }
            
            .upload-hint {
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            #fileInput {
                display: none;
            }
            
            .preview-container {
                display: none;
                margin-bottom: 30px;
                text-align: center;
            }
            
            #imagePreview {
                max-width: 100%;
                max-height: 300px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-bottom: 30px;
            }
            
            .btn {
                padding: 15px 30px;
                border: none;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3);
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #5a6268;
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .result-container {
                display: none;
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                margin-top: 20px;
            }
            
            .result-title {
                color: #495057;
                margin-bottom: 20px;
                text-align: center;
                font-size: 1.5rem;
            }
            
            .result-item {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 3px 10px rgba(0,0,0,0.05);
                transition: transform 0.3s ease;
            }
            
            .result-item:hover {
                transform: translateX(5px);
            }
            
            .result-item:first-child {
                border-left: 5px solid #4facfe;
            }
            
            .class-name {
                font-size: 1.2rem;
                font-weight: bold;
                color: #212529;
            }
            
            .confidence {
                font-size: 1.3rem;
                font-weight: bold;
                color: #00c9ff;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4facfe;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .status {
                text-align: center;
                padding: 20px;
                margin-top: 20px;
                border-radius: 10px;
                font-size: 0.9rem;
            }
            
            .status-success {
                background: #d4edda;
                color: #155724;
            }
            
            .status-error {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 AI图像识别系统</h1>
                <p>基于ResNet18深度学习模型 | 支持1000种物体识别</p>
            </div>
            
            <div class="content">
                <!-- 上传区域 -->
                <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">点击选择或拖拽图片到此处</div>
                    <div class="upload-hint">支持 JPG, PNG, BMP 格式 | 最大5MB</div>
                </div>
                
                <input type="file" id="fileInput" accept="image/*">
                
                <!-- 图片预览 -->
                <div class="preview-container" id="previewContainer">
                    <img id="imagePreview" alt="预览图片">
                </div>
                
                <!-- 按钮区域 -->
                <div class="buttons">
                    <button class="btn btn-primary" id="predictBtn" onclick="predictImage()" disabled>
                        <span>🔍 开始识别</span>
                    </button>
                    <button class="btn btn-secondary" onclick="clearAll()">
                        <span>🗑️ 清空</span>
                    </button>
                </div>
                
                <!-- 加载动画 -->
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div>AI正在分析图片...</div>
                </div>
                
                <!-- 结果显示 -->
                <div class="result-container" id="resultContainer">
                    <div class="result-title">识别结果</div>
                    <div id="results"></div>
                </div>
                
                <!-- 状态显示 -->
                <div class="status" id="status"></div>
            </div>
        </div>

        <script>
            let currentFile = null;
            
            // 页面元素
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const previewContainer = document.getElementById('previewContainer');
            const imagePreview = document.getElementById('imagePreview');
            const predictBtn = document.getElementById('predictBtn');
            const loading = document.getElementById('loading');
            const resultContainer = document.getElementById('resultContainer');
            const resultsDiv = document.getElementById('results');
            const statusDiv = document.getElementById('status');
            
            // 文件选择处理
            fileInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });
            
            // 拖拽功能
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.style.background = '#e9ecef';
                    uploadArea.style.borderColor = '#667eea';
                });
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.style.background = '#f8f9fa';
                    uploadArea.style.borderColor = '#4facfe';
                });
            });
            
            uploadArea.addEventListener('drop', (e) => {
                const file = e.dataTransfer.files[0];
                handleFile(file);
            });
            
            function handleFile(file) {
                if (!file.type.startsWith('image/')) {
                    showStatus('请选择图片文件！', 'error');
                    return;
                }
                
                if (file.size > 5 * 1024 * 1024) {
                    showStatus('图片大小不能超过5MB！', 'error');
                    return;
                }
                
                currentFile = file;
                predictBtn.disabled = false;
                
                // 显示预览
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    previewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
                
                // 隐藏之前的结果
                resultContainer.style.display = 'none';
                showStatus('图片已选择，点击"开始识别"按钮进行分析', 'success');
            }
            
            // 预测函数
            async function predictImage() {
                if (!currentFile) return;
                
                // 显示加载动画
                loading.style.display = 'block';
                predictBtn.disabled = true;
                resultContainer.style.display = 'none';
                
                const formData = new FormData();
                formData.append('file', currentFile);
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data.predictions);
                        showStatus(`识别成功！模型: ${data.model} | 设备: ${data.device}`, 'success');
                    } else {
                        showStatus('识别失败：' + data.message, 'error');
                    }
                } catch (error) {
                    showStatus('请求失败：' + error.message, 'error');
                } finally {
                    loading.style.display = 'none';
                    predictBtn.disabled = false;
                }
            }
            
            // 显示结果
            function displayResults(predictions) {
                resultsDiv.innerHTML = '';
                
                predictions.forEach(pred => {
                    const item = document.createElement('div');
                    item.className = 'result-item';
                    
                    // 创建星级显示
                    let stars = '';
                    const confidence = pred.confidence;
                    if (confidence > 80) stars = '⭐⭐⭐';
                    else if (confidence > 60) stars = '⭐⭐';
                    else stars = '⭐';
                    
                    item.innerHTML = `
                        <div>
                            <div class="class-name">${pred.rank}. ${pred.class_name}</div>
                            <div style="color: #6c757d; font-size: 0.9rem;">置信度</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="confidence">${pred.confidence}%</div>
                            <div style="color: #ffc107; font-size: 1.2rem;">${stars}</div>
                        </div>
                    `;
                    
                    resultsDiv.appendChild(item);
                });
                
                resultContainer.style.display = 'block';
            }
            
            // 清空所有
            function clearAll() {
                currentFile = null;
                fileInput.value = '';
                previewContainer.style.display = 'none';
                resultContainer.style.display = 'none';
                predictBtn.disabled = true;
                loading.style.display = 'none';
                showStatus('已清空，请选择新的图片', 'success');
            }
            
            // 显示状态信息
            function showStatus(message, type) {
                statusDiv.textContent = message;
                statusDiv.className = `status status-${type}`;
            }
            
            // 页面加载时显示欢迎信息
            window.onload = function() {
                showStatus('欢迎使用AI图像识别系统！请选择一张图片开始识别', 'success');
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """API端点：接收图像并返回分类结果"""
    if not MODEL_LOADED:
        raise HTTPException(status_code=500, detail="模型加载失败，服务不可用")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图像文件")
    
    # 检查文件大小（限制5MB）
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
    
    try:
        result = classifier.predict(contents)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    import platform
    status = {
        "status": "healthy" if MODEL_LOADED else "unhealthy",
        "service": "CNN Image Classification API",
        "model_loaded": MODEL_LOADED,
        "system": platform.system(),
        "python_version": platform.python_version(),
        "torch_version": "unknown",
        "torchvision_version": "unknown"
    }
    
    if MODEL_LOADED:
        import torch
        import torchvision
        status.update({
            "torch_version": torch.__version__,
            "torchvision_version": torchvision.__version__,
            "device": str(classifier.device),
            "model": "ResNet18"
        })
    
    return status

@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "服务运行正常",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "model_loaded": MODEL_LOADED
    }

if __name__ == "__main__":
    print("=" * 60)
    print("         CNN图像分类服务启动中")
    print("=" * 60)
    print(f"模型加载状态: {'成功' if MODEL_LOADED else '失败'}")
    print("访问地址:")
    print("  Web界面: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/health")
    print("  测试端点: http://localhost:8000/test")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )