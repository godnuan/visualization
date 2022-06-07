import os
import numpy as np
import seaborn as sns; sns.set()
import cv2
import matplotlib.pyplot as plt
from matplotlib import animation
from data import trajectories as tra
import argparse
import random
import tkinter as tk
import tkinter.messagebox
# 给定数据集中轨迹数据或预测轨迹数据、H矩阵的逆矩阵，输出图像帧中行人的坐标
def to_image_frame(Hinv, loc):
    '''
    :param Hinv: array of shape (3,3)
    :param loc: tensor of shape (num_peds, 2, seq_len)
    :return: array of shape (num_peds, seq_len, 2)
    '''
    loc = loc.permute((0,2,1))
    locHomogenous = np.concatenate((loc, np.ones((loc.shape[0],loc.shape[1], 1))),axis=2)
    locHomogenous_mat = locHomogenous.reshape((-1,3))
    loc_tr = np.transpose(locHomogenous_mat)
    loc_tr = np.matmul(Hinv, loc_tr)  # to camera frame
    locXYZ = np.transpose(loc_tr/loc_tr[2])  # to pixels (from millimeters)
    locXYZ = locXYZ.reshape((locHomogenous.shape[0],locHomogenous.shape[1],3))
    return locXYZ[:, :, :2].astype(int)

# 找到视频中第timeframe号视频帧，显示并保存图像
def save_img(dataset_name,save_path,video_name="seq_eth.avi",timeframe=12381):
    video_file = dataset_name + video_name
    if os.path.exists(video_file):
        print('[INF] Using video file'+video_file)
        cap = cv2.VideoCapture(video_file)
    if cap:
        cap.set(cv2.CAP_PROP_POS_FRAMES, timeframe)
        ret, im = cap.read()
    # plt.axis(False)
    # plt.grid(False)
    # plt.imshow(im)
    # plt.show()
    cv2.imwrite(save_path,im)
    # FPS = cap.get(5)
    # print(FPS)

# 用于绘制一个行人的历史轨迹的绘制器
class ToyAnimation:
    # Constructor
    def __init__(self, img, ped_traj,obs_len=8,pred_len=12,frame_interval=6):
        '''
        :param img: str
        :param ped_traj: array of shape (num_peds,seq_len, 2)
        '''

        self.obs_len = obs_len
        self.pred_len = pred_len
        self.fig = plt.figure(0)
        color = ['b','r','c','m','y','k','w','g']
        ax = plt.axes()
        img = plt.imread(img)
        plt.imshow(img)
        plt.axis(False)
        plt.grid(False)
        plt.imshow(img)
        self.ped_traj = ped_traj
        self.FPS = 25*frame_interval

        self.obs_x_total = []
        self.obs_y_total = []
        self.obs_ln_total = []
        for k in range(self.ped_traj.shape[0]):
            x = []
            y = []
            if k < len(color):
                ln, = ax.plot([], [], color[k]+'.')
            else:
                ln, = ax.plot([], [], color[random.randrange(len(color))]+'.')
            self.obs_x_total.append(x)
            self.obs_y_total.append(y)
            self.obs_ln_total.append(ln)

        self.pred_x_total = []
        self.pred_y_total = []
        self.pred_ln_total = []
        for k in range(self.ped_traj.shape[0]):
            x = []
            y = []
            ln, = ax.plot([], [], 'g.')
            self.pred_x_total.append(x)
            self.pred_y_total.append(y)
            self.pred_ln_total.append(ln)


        self.anim = animation.FuncAnimation(self.fig, self.animate,
                                            frames=self.ped_traj.shape[1]*5, interval=500, blit=True)

    # 绘制函数
    def animate(self, i):
        if i < self.obs_len:
            for j in range(self.ped_traj.shape[0]):
                self.obs_x_total[j].append(self.ped_traj[j, i, 1])
                self.obs_y_total[j].append(self.ped_traj[j, i, 0])
                self.obs_ln_total[j].set_data(self.obs_x_total[j], self.obs_y_total[j])
            return tuple(self.obs_ln_total)
        elif i < self.obs_len + self.pred_len:
                for j in range(self.ped_traj.shape[0]):
                    self.pred_x_total[j].append(self.ped_traj[j, i, 1])
                    self.pred_y_total[j].append(self.ped_traj[j, i, 0])
                    self.pred_ln_total[j].set_data(self.pred_x_total[j], self.pred_y_total[j])
                return tuple(self.obs_ln_total) + tuple(self.pred_ln_total)
        else:
            return tuple(self.obs_ln_total) + tuple(self.pred_ln_total)


    def save(self, filename):
        # 保存为gif
        # anim.save('../toy_animation.mp4', fps=FPS, extra_args=['-vcodec', 'libx264'])
        if not os.path.exists(filename):
            self.anim.save(filename, fps=self.FPS, writer='pillow')
        else:
            print("The gif has existed.")

class ToyLinePlot:

    def __init__(self, img, ped_traj,obs_len=8,pred_len=12):
        '''
        :param img: str
        :param ped_traj: array of shape (num_peds,seq_len, 2)
        '''

        self.obs_len = obs_len
        self.pred_len = pred_len
        self.fig = plt.figure(0)
        color = ['b','r','c','m','y','k','w','g']
        ax = plt.axes()
        img = plt.imread(img)
        plt.imshow(img)
        plt.axis(False)
        plt.grid(False)
        plt.imshow(img)
        self.ped_traj = ped_traj


        for k in range(self.ped_traj.shape[0]):
            x = []
            y = []
            if k < len(color):
                ln, = ax.plot(self.ped_traj[k,:self.obs_len+1,1], self.ped_traj[k,:self.obs_len+1,0], color[k]+'--')
            else:
                ln, = ax.plot(self.ped_traj[k,:self.obs_len+1,1], self.ped_traj[k,:self.obs_len+1,0], color[random.randrange(len(color))]+'--')

        self.pred_x_total = []
        self.pred_y_total = []
        self.pred_ln_total = []
        for k in range(self.ped_traj.shape[0]):
            x = []
            y = []
            ln, = ax.plot(self.ped_traj[k,self.obs_len:,1], self.ped_traj[k,self.obs_len:,0], 'g--')

    def save(self, filename):
        # 保存为png
        if not os.path.exists(filename):
            plt.savefig(filename,bbox_inches='tight', pad_inches = -0.1)
        else:
            print("The png has existed.")

parser = argparse.ArgumentParser()
'''可视化选项'''
parser.add_argument('--dataset', type=str, default='seq_eth')
parser.add_argument('--frame_id', type=int, default=0)
parser.add_argument('--anim', type=int, default=0)
parser.add_argument('--save_gif', type=str, default='./visual_traj/gif/')
parser.add_argument('--obs_len', type=int, default=8)
parser.add_argument('--pred_len', type=int, default=12)
parser.add_argument('--save_fig',type=str,default='./visual_traj/fig/')
parser.add_argument('--save_img',type=str,default='./img/')
args = parser.parse_args()

def draw_traj(args):
    '''数据集'''
    dset_ = args.dataset
    dset_name = './' + dset_ + '/'
    data_dir = dset_name + 'obsmat.txt'
    dset = tra.TrajectoryDataset(data_dir,obs_len=args.obs_len,pred_len=args.pred_len)
    if dset_ == 'seq_eth':
        frame_interval = 6
    else: frame_interval = 10
    '''id:需要可视化的轨迹序列编号'''
    id = args.frame_id
    if id >= len(dset):
        tk.messagebox.showinfo("警告", "编号已越界！")
    frame_id = dset[id][2]
    obs_data = dset[id][0]
    pred_data = dset[id][1]
    '''保存视频帧图像'''
    img_path = args.save_img + dset_ + "_" + str(id) + ".png"
    if not os.path.exists(img_path):
        save_img(dset_name,save_path=img_path,video_name=f'{dset_}.avi',timeframe=int(frame_id))
    '''计算单应性矩阵H'''
    homography_file = os.path.join(dset_name, 'H.txt')
    if os.path.exists(homography_file):
        Hinv = np.linalg.inv(np.loadtxt(homography_file))
    else:
        print('[INF] No homography file')
    '''将真实轨迹数据转换为图像坐标数据'''
    obsv_XY = to_image_frame(Hinv, obs_data)
    pred_XY = to_image_frame(Hinv, pred_data)
    peds_XY = np.concatenate((obsv_XY,pred_XY),axis=1)
    '''轨迹可视化'''
    gif_path = args.save_gif + dset_ + "_" + f"{id}.gif"
    fig_path = args.save_fig + dset_ + "_" + f"{id}.png"
    if args.anim:
        toy_animation = ToyAnimation(img_path,peds_XY,obs_len=args.obs_len,pred_len=args.pred_len,frame_interval=frame_interval)
        toy_animation.save(gif_path)
    toy_plot = ToyLinePlot(img_path,peds_XY,obs_len=args.obs_len,pred_len=args.pred_len)
    toy_plot.save(fig_path)



