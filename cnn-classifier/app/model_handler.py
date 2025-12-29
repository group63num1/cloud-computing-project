import torch
import os
import json
import io
from PIL import Image

# 首先尝试导入torchvision，并明确捕获导入错误
try:
    import torchvision
    import torchvision.models as models
    import torchvision.transforms as transforms
    TORCHVISION_AVAILABLE = True
except ImportError as e:
    TORCHVISION_AVAILABLE = False
    TORCHVISION_ERROR = str(e)
    print(f"✗ Torchvision导入失败: {TORCHVISION_ERROR}")
    # 创建空占位符，防止后续代码因未定义而崩溃
    models = None
    transforms = None

class ImageClassifier:
    def __init__(self):
        print("=" * 50)
        print("正在初始化图像分类模型...")
        
        # 检查torchvision是否可用
        if not TORCHVISION_AVAILABLE:
            print("✗ 无法继续：torchvision库不可用。")
            raise ImportError(f"Torchvision导入失败: {TORCHVISION_ERROR}")
        
        print(f"PyTorch版本: {torch.__version__}")
        print(f"Torchvision版本: {torchvision.__version__}")
        
        # 使用CPU
        self.device = torch.device('cpu')
        print(f"使用设备: {self.device}")
        
        # 加载ResNet18模型（更新为推荐方式）
        try:
            print("正在下载ResNet18预训练模型...")
            # 对于torchvision 0.13+，使用新的weights API
            from torchvision.models import ResNet18_Weights
            
            # 使用最新的预训练权重
            weights = ResNet18_Weights.IMAGENET1K_V1
            self.model = models.resnet18(weights=weights)
            print("✓ 模型加载成功!")
            
            # 获取模型预期的预处理方法
            self.transform = weights.transforms()
            print("✓ 使用标准预处理管道")
            
        except Exception as e:
            print(f"✗ 新API加载失败，尝试旧方法: {e}")
            # 回退到旧方法
            self.model = models.resnet18(pretrained=True)
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        
        self.model.eval()
        self.model.to(self.device)
        
        # 加载完整的1000个ImageNet类别
        print("正在加载ImageNet类别标签...")
        try:
            # 读取下载的完整标签文件
            labels_path = os.path.join(os.path.dirname(__file__), '..', 'imagenet_classes.json')
            if not os.path.exists(labels_path):
                # 如果文件不在上层目录，尝试当前目录
                labels_path = 'imagenet_classes.json'
            
            with open(labels_path, 'r', encoding='utf-8') as f:
                self.labels = json.load(f)
            
            if len(self.labels) >= 1000:
                print(f"✓ 加载了完整的{len(self.labels)}个ImageNet类别")
                # 显示一些示例类别
                print("   示例类别:")
                print(f"   291. {self.labels[290]}")  # 老虎 tiger
                print(f"   282. {self.labels[281]}")  # 虎斑猫 tabby cat
                print(f"   207. {self.labels[206]}")  # 金毛犬 golden retriever
                print(f"   468. {self.labels[467]}")  # 公交车 bus
                print(f"   751. {self.labels[750]}")  # 赛车 racer
            else:
                print(f"⚠ 只加载了{len(self.labels)}个类别，可能不是完整列表")
                
        except Exception as e:
            print(f"✗ 无法加载完整标签文件: {e}")
            print("  使用简化的20个类别作为后备...")
            # 简化的ImageNet类别（后备方案）
            self.labels = [
                "金鱼 goldfish", "大白鲨 great white shark", "虎鲨 tiger shark", 
                "公鸡 cock", "母鸡 hen", "大象 elephant", "考拉 koala", 
                "蜗牛 snail", "甲虫 beetle", "瓢虫 ladybug",
                "汽车 car", "出租车 taxi", "公交车 bus", "救护车 ambulance", 
                "消防车 fire truck", "飞机 airplane", "直升机 helicopter",
                "猫 cat", "狗 dog", "马 horse"
            ]
        
        print("模型初始化完成!")
        print("=" * 50)
    
    def predict(self, image_bytes):
        """预测图像类别"""
        try:
            # 1. 打开图像
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # 2. 预处理
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 3. 推理
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # 4. 获取top-5预测结果（原来top-3，现在显示更多）
            top5_prob, top5_idx = torch.topk(probabilities, 5)
            
            results = []
            for i in range(top5_prob.size(0)):
                idx = top5_idx[i].item()
                # 确保索引在标签范围内
                if idx < len(self.labels):
                    label = self.labels[idx]
                else:
                    label = f"未知类别 (索引: {idx})"
                    
                prob = top5_prob[i].item() * 100  # 转换为百分比
                
                results.append({
                    'class_id': idx,
                    'class_name': label,
                    'confidence': round(prob, 2),
                    'rank': i + 1
                })
            
            # 5. 添加一些分析信息
            top_prediction = results[0]
            is_animal = any(keyword in top_prediction['class_name'].lower() 
                          for keyword in ['tiger', 'cat', 'dog', 'lion', 'bear', 'animal'])
            
            return {
                'success': True,
                'predictions': results,
                'top_prediction': top_prediction,
                'analysis': {
                    'is_animal': is_animal,
                    'top_confidence': top_prediction['confidence'],
                    'total_classes_available': len(self.labels)
                },
                'message': '识别成功!',
                'model': 'ResNet18',
                'device': str(self.device)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '识别失败，请检查图片格式'
            }

# ==== 文件末尾：创建全局实例 ====
print("正在创建图像分类器实例...")
try:
    classifier = ImageClassifier()
    print("✓ 图像分类器创建成功！")
except Exception as e:
    print(f"✗ 创建分类器失败: {e}")
    # 创建一个标记对象，让服务至少能启动
    classifier = None
    print("⚠ 创建了空的分类器对象，/predict接口将不可用")