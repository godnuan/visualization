import os.path
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog as fd
import draw_trajectory as dt

'''选择存储视频帧的文件夹'''
def open_img_Floder():
    folder_path = fd.askdirectory() # 打开文件
    show_Imgae_Path.delete(0,tk.END)  # 清空
    show_Imgae_Path.insert(0,folder_path)  #写入路径

'''选择存储轨迹图像的文件夹'''
def open_fig_Floder():
    folder_path = fd.askdirectory() # 打开文件
    show_Fig_Path.delete(0,tk.END)  # 清空
    show_Fig_Path.insert(0,folder_path)  #写入路径

'''选择存储轨迹动图的文件夹'''
def open_gif_Floder():
    folder_path = fd.askdirectory() # 打开文件
    show_Gif_Path.delete(0,tk.END)  # 清空
    show_Gif_Path.insert(0,folder_path)  #写入路径

'''按钮事件，生成轨迹'''
def generate_img():
    is_anim = ani.get()
    dt.args.dataset= d.get()
    dt.args.frame_id = int(frame_id.get())
    dt.args.obs_len = int(obs_len.get())
    dt.args.pred_len = int(pred_len.get())
    if is_anim == "Yes":
        dt.args.anim = 1
    else: dt.args.anim = 0
    dt.args.save_img = show_Imgae_Path.get()
    dt.args.save_fig = show_Fig_Path.get()
    dt.args.save_gif = show_Gif_Path.get()
    dt.draw_traj(dt.args)
    photo_ = tk.PhotoImage(file=dt.args.save_fig + dt.args.dataset + "_" + f"{dt.args.frame_id}.png", format="png")
    photo_lable.configure(image=photo_)
    photo_lable.image = photo_

'''按钮事件，显示图像'''
def show_img():
    # number_var.set(f'{current_photo_no + 1} of {len(photos)}')
    file = show_Fig_Path.get() + d.get() + "_" + f"{int(frame_id.get())}.png"
    if os.path.exists(file):
        photo_ = tk.PhotoImage(file=file,format="png")
        photo_lable.configure(image=photo_)
        photo_lable.image = photo_
    else:
        tk.messagebox.showinfo("警告", f"编号为{frame_id.get()}的行人轨迹图像不存在！")

'''创建用户显示界面'''
root = tk.Tk()
root.geometry('720x600+100+100')
root.title('行人轨迹查看器')

'''图像显示'''
photos = 'visual_traj/fig/seq_eth_0.png'
photoss = tk.PhotoImage(file=photos,format='png')
photo_lable = tk.Label(root, image=photoss, width=720, height=400)
photo_lable.pack()

'''分割显示图像和用户面板'''
n_var1 = tk.StringVar()
n_var1.set('')
tk.Label(root, textvariable=n_var1, bd=1, relief=tk.SUNKEN, anchor=tk.CENTER, height=1).pack(fill=tk.X)

'''用户面板'''
button_frame = tk.Frame(root)
button_frame.pack()

'''数据集名称'''
d_e = tk.Label(button_frame,text="数据集:")
d = tk.StringVar()
d.set('seq_eth')
dataset = tk.OptionMenu(button_frame,d,"seq_eth","seq_hotel")
dataset.config(width=7)
d_e.grid(row=0,column=0)
dataset.grid(row=0,column=1,padx=(0,50))

'''需要可视化的轨迹序列编号'''
f_e = tk.Label(button_frame,text="视频帧编号:")
frame_id = tk.Entry(button_frame,bd=2,width=5)
frame_id.insert(0,"0")
f_e.grid(row=0,column=2)
frame_id.grid(row=0,column=3,padx=(0,50))

'''历史轨迹时长'''
o_e = tk.Label(button_frame,text="历史时长:")
obs_len = tk.Entry(button_frame,bd=2,width=5)
obs_len.insert(0,"8")
o_e.grid(row=0,column=4)
obs_len.grid(row=0,column=5,padx=(0,50))

'''未来轨迹时长'''
p_e = tk.Label(button_frame,text="未来时长:")
pred_len = tk.Entry(button_frame,bd=2,width=5)
pred_len.insert(0,"12")
p_e.grid(row=0,column=6)
pred_len.grid(row=0,column=7,padx=(0,50))

'''是否创建gif'''
ani_e = tk.Label(button_frame,text="是否生成动图:")
ani = tk.StringVar()
ani.set("Yes")
animation = tk.OptionMenu(button_frame,ani,"Yes","No")
animation.config(width=7)
ani_e.grid(row=1,column=0)
animation.grid(row=1,column=1,padx=(0,50))

'''存储视频帧路径'''
s_m_e = tk.Button(button_frame,text=" 存储视频帧路径  ",command=open_img_Floder)
show_Imgae_Path = tk.Entry(button_frame,width=30)
show_Imgae_Path.insert(0,"./img/")
s_m_e.grid(row=2,column=0)
show_Imgae_Path.grid(row=2,column=1,padx=(10,50),columnspan=3)

'''存储轨迹图像路径'''
s_f_e = tk.Button(button_frame,text="存储轨迹图像路径",command=open_fig_Floder)
show_Fig_Path = tk.Entry(button_frame,width=30)
show_Fig_Path.insert(0,"./visual_traj/fig/")
s_f_e.grid(row=3,column=0)
show_Fig_Path.grid(row=3,column=1,padx=(10,50),columnspan=3)

'''存储轨迹动图路径'''
s_g_e = tk.Button(button_frame,text="存储轨迹动图路径",command=open_gif_Floder)
show_Gif_Path = tk.Entry(button_frame,width=30)
show_Gif_Path.insert(0,"./visual_traj/gif/")
s_g_e.grid(row=4,column=0)
show_Gif_Path.grid(row=4,column=1,padx=(10,50),columnspan=3)

'''生成按钮'''
b = tk.Button(button_frame, text='可视化',height=5,width=12,command=generate_img)
b.config(background='pink')
b.grid(row=2,column=5,rowspan=3,padx=(0,10))

'''显示按钮'''
b = tk.Button(button_frame, text='展示',height=5,width=12,command=show_img)
b.config(background='pink')
b.grid(row=2,column=6,rowspan=3,padx=(10,0))

'''保持用户显示界面一直运行'''
root.mainloop()