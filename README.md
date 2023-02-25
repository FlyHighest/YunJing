# YunJing
云景. A simple web ui (frontend) for AI image generating. 



# TODO

1. 分享页面，有利于网站宣传。展示一张图像，扫码打开绘图页。
2. 登录用户配置：主题切换，是否署名，画廊列数，自定义模板，是否自动发布


# 图像引导功能设计

text2image data 加一个参数 是否图生图；
对应的，set param，main的popup和画廊的popup添加这个checkbox

预处理：原图、边缘图、。。。
引导方式：图生图、Hed边缘、

原图 图生图 就是img2img
其他则调用controlnet的功能


输入参数设计

左边放一个图像，文本（点击上传图像），右边 一列参数选择 分别是 预处理方式，引导方式，降噪力度

