import torch
from torch import nn


# device = torch.device("cuda:0"if torch.cuda.is_available()else"cpu")  # 调用GPU

class AlexNet(torch.nn.Module):
    def __init__(self, num=1000):  # num类别数,论文中为1000
        super(AlexNet, self).__init__()
        self.conv = torch.nn.Sequential(  # 将卷积层封装,将两个GPU合并
            nn.Conv2d(in_channels=3, out_channels=96, kernel_size=11, stride=4, padding=1),
            nn.ReLU(),  # 激活
            nn.MaxPool2d(kernel_size=3, stride=2),  # 池化

            nn.Conv2d(in_channels=96, out_channels=256, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2),

            nn.Conv2d(in_channels=256, out_channels=384, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            nn.Conv2d(in_channels=384, out_channels=384, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            nn.Conv2d(in_channels=384, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2)
        )
        '''
        卷积层C1
        C1的基本结构为：卷积–>ReLU–>池化
        卷积：输入224 × 224 × 3，96个11×11×3的卷积核，不扩充边缘padding = 0，步长stride = 4，因此其FeatureMap大小为(224-11+0×2+4)/4 = 54，即54×54×96;
        激活函数：ReLU；
        池化：池化核大小3 × 3，不扩充边缘padding = 0，步长stride = 2，因此其FeatureMap输出大小为(54-3+0×2+2)/2=26, 即C1输出为26×26×96（此处未将输出分到两个GPU中，
        若按照论文将分成两组，每组为26×26×48）；
        卷积层C2
        C2的基本结构为：卷积–>ReLU–>池化
        卷积：输入26×26×96，256个5×5×96的卷积核，扩充边缘padding = 2， 步长stride = 1，因此其FeatureMap大小为(26-5+2×2+1)/1 = 26，即26×26×256;
        激活函数：ReLU；
        池化：池化核大小3 × 3，不扩充边缘padding = 0，步长stride = 2，因此其FeatureMap输出大小为(26-3+0+2)/2=12, 即C2输出为12×12×256（此处未将输出分到两个GPU中，
        若按照论文将分成两组，每组为12×12×128）；
        卷积层C3
        C3的基本结构为：卷积–>ReLU。注意一点：此层没有进行MaxPooling操作。
        卷积：输入12×12×256，384个3×3×256的卷积核， 扩充边缘padding = 1，步长stride = 1，因此其FeatureMap大小为(12-3+1×2+1)/1 = 12，即12×12×384;
        激活函数：ReLU，即C3输出为12×12×384（此处未将输出分到两个GPU中，若按照论文将分成两组，每组为12×12×192）；
        卷积层C4
        C4的基本结构为：卷积–>ReLU。注意一点：此层也没有进行MaxPooling操作。
        卷积：输入12×12×384，384个3×3×384的卷积核， 扩充边缘padding = 1，步长stride = 1，因此其FeatureMap大小为(12-3+1×2+1)/1 = 12，即12×12×384;
        激活函数：ReLU，即C4输出为12×12×384（此处未将输出分到两个GPU中，若按照论文将分成两组，每组为12×12×192）；
        卷积层C5
        C5的基本结构为：卷积–>ReLU–>池化
        卷积：输入12×12×384，256个3×3×384的卷积核，扩充边缘padding = 1，步长stride = 1，因此其FeatureMap大小为(12-3+1×2+1)/1 = 12，即12×12×256;
        激活函数：ReLU；
        池化：池化核大小3 × 3， 扩充边缘padding = 0，步长stride = 2，因此其FeatureMap输出大小为(12-3+0×2+2)/2=5, 输出为5×5×256（此处未将输出分到两个GPU中，
        若按照论文将分成两组，每组为5×5×128）；1
        '''
        self.fc = nn.Sequential(
            nn.Linear(256*5*5, 4096),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(4096, 4096),
            nn.ReLU(),
            nn.Dropout(0.5),

            nn.Linear(4096, num)
        )
        '''
        全连接层FC6
        FC6的基本结构为：全连接–>>ReLU–>Dropout
        全连接：此层的全连接实际上是通过卷积进行的，输入6×6×256，4096个6×6×256的卷积核，扩充边缘padding = 0, 步长stride = 1, 因此其FeatureMap大小为(6-6+0×2+1)/1 = 1，即1×1×4096;
        激活函数：ReLU；
        Dropout：全连接层中去掉了一些神经节点，达到防止过拟合，FC6输出为1×1×4096；
        全连接层FC7
        FC7的基本结构为：全连接–>>ReLU–>Dropout
        全连接：此层的全连接，输入1×1×4096;
        激活函数：ReLU；
        Dropout：全连接层中去掉了一些神经节点，达到防止过拟合，FC7输出为1×1×4096；
        全连接层FC8
        FC8的基本结构为：全连接–>>softmax
        全连接：此层的全连接，输入1×1×4096;
        '''
    def forward(self, img):
        feature = self.conv(img)
        output = self.fc(feature.view(img.shape[0], -1))
        return output


class VGG16(nn.Module):
    def __init__(self, num=10):
        super(VGG16, self).__init__()
        self.conv = nn.Sequential(
            # 1
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            # 2
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            # 4
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # 5
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            # 6
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            # 7
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # 8
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # 9
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # 10
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # 11
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # 12
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # 13
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AvgPool2d(kernel_size=1, stride=1),
        )
        self.fc = nn.Sequential(
            # 14
            nn.Linear(25088, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            # 15
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            # 16
            nn.Linear(4096, num),
        )
        # self.classifier = nn.Linear(512, 10)

    def forward(self, img):
        feature = self.conv(img)
        output = self.fc(feature.view(img.shape[0], -1))
        return output