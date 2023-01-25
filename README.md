# YunJing
云景. A simple web ui (frontend) for AI image generating. 


Gallery界面的弹出框，添加点赞按钮和点赞数

username | gentime      THUMBICON Num

put的时候，put image？这样方便绑定click。

如果没有登录： put image不绑定， + put text

如果登录了，当前用户对这个图有没有点赞，决定img url和on click

对thumbup false，onclik要处理：在数据库加入userid likes genid， 计数+1，右侧text文本更新。



