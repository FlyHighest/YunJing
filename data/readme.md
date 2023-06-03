# 数据结构文档

## 一、概况

数据分为以下几类：
- 状态数据 (status&lock)
- 历史记录相关数据 (history)
- 用户信息相关数据 (user)
- 图像信息数据 (image)
- 画廊相关数据 (gallery)
- 评分相关数据 (score)

## 二、状态数据

### 2.1 服务器状态相关数据

三个状态：`generated_num`,`upscale_num`和`gallery_num`

(1) 总的状态

- `status_get_all`: 返回`generated_num`,`upscale_num`和`gallery_num`

(2) 各状态变量

- `status_get_xxxx_num`
- `status_add_xxxx_num`

### 2.2 用户生成冷却状态

给userid设置`lock:gen:userid`，expire time为冷却时间

- `set_generation_lock`
- `exists_generation_lock`
- `unset_generation_lock`

### 2.3 用户最大ID

`max_userid`，注册用户的时候赋予其max_userid，然后增1。

## 三、历史记录

每个user有一个保存history的list，`history:userid`。list最长为500，存储以元组为单位，元组包含url和genid，用json dumps保存为字符串。

方法：
- `record_history`: push一个url+genid元组字符串。
- `del_history`: 用户主动发起删除历史记录的请求，传入userid和genid。
- `get_history`: 返回limit数量的元组列表

## 四、用户信息

### 4.1 用户信息表
用户的信息用哈希表来存，key为`user:userid`。

用户信息的哈希表有如下key:
- `username`
- `password`
- `email`
- `level`
- `jointime`
- `num_generated`
- `num_published`
- `config`

### 4.2 用户email set

用一个集合`user-emails`保存用户的email，防止重复。

## 4.3 用户username -> userid映射表

key`userid:username`的value为username的userid。

## 五、图像信息

图像信息用hash表存储，key为`image:genid`, 哈希表的key有：
- `genid`
- `imgurl`
- `height`
- `width`
- `params`
- `modelname`
- `prompt`
- `published`
- `userid`
- `nsfw`: 机器判定是否nsfw
- `score`: 机器打分(image reward)
- `face`: 机器人脸检测，是否含有人脸
- `gentime`
- `upx2` : 2倍超分 img url
- `upx4`: 4倍超分 img url
  
## 六、画廊信息

一幅图会被保存到三个有序集合中，
`gallery`,`gallery:userid:userid`,`gallery:model:modelname`
