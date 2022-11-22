import torch
from torch.autograd import Variable

import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import cv2
import time


def parse_args():
    #
    # Setting parameters
    #
    parser = ArgumentParser(description='Inference of AGPCNet')

    #
    # Checkpoint parameters
    #
    parser.add_argument('--pkl-path', type=str, default=r'./results/Iter-29000_mIoU-0.2329_fmeasure-0.3778.pkl',
                        help='checkpoint path')

    #
    # Test image parameters
    #
    parser.add_argument('--image-path', type=str, default=r'./data/1.bmp', help='image path')
    parser.add_argument('--base-size', type=int, default=256, help='base size of images')

    args = parser.parse_args()
    return args


def preprocess_image(img):
    means=[0.485, 0.456, 0.406]
    stds=[0.229, 0.224, 0.225]

    preprocessed_img = img.copy()[: , :, ::-1]
    for i in range(3):
        preprocessed_img[:, :, i] = preprocessed_img[:, :, i] - means[i]
        preprocessed_img[:, :, i] = preprocessed_img[:, :, i] / stds[i]
    preprocessed_img = \
        np.ascontiguousarray(np.transpose(preprocessed_img, (2, 0, 1)))
    preprocessed_img = torch.from_numpy(preprocessed_img)
    preprocessed_img.unsqueeze_(0)
    input = Variable(preprocessed_img, requires_grad = True)
    return input


if __name__ == '__main__':
    args = parse_args()

    # load network
    print('...load checkpoint: %s' % args.pkl_path)
    net = torch.load(args.pkl_path, map_location=torch.device('cpu'))
    net.eval()

    total = sum([param.nelement() for param in net.parameters()])
    print("Number of parameter: %.2fM" % (total / 1e6))

    # load image
    print('...loading test image: %s' % args.image_path)
    img = cv2.imread(args.image_path, 1)
    img = np.float32(cv2.resize(img, (args.base_size, args.base_size))) / 255
    input = preprocess_image(img)

    # inference in cpu
    print('...inference in progress')

    time_start = time.time()
    with torch.no_grad():
        output = net(input)

    time_end = time.time()
    print("test time:%.2fs" % (time_end - time_start))

    output = output.cpu().detach().numpy().reshape(args.base_size, args.base_size)
    output = output > 0

    # show results
    plt.figure()
    plt.subplot(121), plt.imshow(img, cmap='gray'), plt.title('Original Image')
    plt.subplot(122), plt.imshow(output, cmap='gray'), plt.title('Inference Result')
    plt.show()