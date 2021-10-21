# 300hero_info
基于hoshino机器人，进行300英雄的团分，对局战绩信息查询。
## 功能介绍
在群内绑定300英雄角色ID，实现群内获取角色团分，对局信息等功能。
## 具体操作
1、在<code>hoshino/modules</code>文件夹中，打开<code>cmd</code>，输入以下代码 按回车执行：
<pre>git clone https://github.com/jiyemengmei/300hero_info.git</pre>
2、在<code>hoshino/config/__bot__.py</code>文件中，<code>MODULES_ON</code>里添加 "300hero_info"
## 功能指令
|  指令   | 说明  | 具体  |
|  ----  | ----  | ----  |
| <b>绑定用户</b>  | 绑定300英雄游戏内角色ID  | 绑定用户<b>ω千石抚子ω</b>  |
| 用户信息  | 查询自己的用户信息，可用@查询他人的信息  | 用户信息@qq号  |
| 删除用户  | 删除自己的用户信息，管理员可用@删除他人信息  | 删除用户@qq号  |
| 团分  | 查询自己的团分信息，可用@或指定ID获取他人信息  | 团分@qq号或团分ω千石抚子ω  |
| 战场对局  | 查询自己的战场对局信息，用@可以查询他人的信息  | 战场对局@qq号或战场对局ω千石抚子ω  |
| 竞技场对局  | 查询自己的竞技场对局信息，用@可以查询他人的信息  | 竞技场对局@qq号或竞技场对局ω千石抚子ω  |
## 鸣谢
<a href="https://github.com/Mrs4s/go-cqhttp" target="_BLANK">go-cqhttp</a>\
<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_BLANK">HoshinoBot</a>\
<a href="https://300report.jumpw.com/" target="_BLANK">300英雄战报分析</a>
## API
<a href="https://300report.jumpw.com/static/doc/openapi.txt" target="_BLANK">300英雄战报分析api文档</a>
## 更新日志
### 2021/10/21
首次上传
