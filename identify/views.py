import os
import json
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
import torch
from PIL import Image
from torchvision import transforms
from .models import identify_flower
from .flowers_models import AlexNet

def upload_view(request):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if request.method == 'POST'and request.FILES['image']:
        # 获取上传的图片
        image_file = request.FILES.get('image')
        # 将图片保存到本地
        filename = default_storage.save(os.path.join(settings.MEDIA_ROOT, 'flower/',image_file.name), image_file)
        # 加载模型
        model = AlexNet(num=102).to(device)
        weights_path = os.path.join(settings.MODEL_ROOT, 'alexnet_ox.pt')
        model.load_state_dict(torch.load(weights_path))
        model.eval()
        json_path = os.path.join(settings.MODEL_ROOT, 'cat_to_name.json')
        json_file = open(json_path, "r")
        class_indict = json.load(json_file)
        # model = torch.load(os.path.join(settings.MODEL_ROOT, 'alexnet_ox.pt'))
        # 打开图片并将其转换为模型可接受的格式
        data_transform = transforms.Compose(
            [  # transforms.Resize((224, 224)),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        img = Image.open(os.path.join(settings.MEDIA_ROOT, filename))
        img= data_transform(img)
        img = torch.unsqueeze(img, dim=0)
        # 使用模型进行预测
        with torch.no_grad():
            # predict class
            output = torch.squeeze(model(img.to(device))).cpu()
            predict = torch.softmax(output, dim=0)
            predict_cla = torch.argmax(predict).numpy()
        # 获取预测结果
        flower_name = class_indict[str(predict_cla)]
        flower_predict = predict[predict_cla].numpy()
        # 查询数据库
        flower = identify_flower.objects.get(flower_name=flower_name)
        # 返回结果
        data = {
            'flower_name': flower.flower_name,
            'flower_info': flower.flower_info,
        }
        return render(request, 'identify/result.html', data, image_file)
    return render(request, 'identify/upload.html')


