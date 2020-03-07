# Cyakka
- - -
![Cyakka 首页预览](https://cdn.img.wenhairu.com/images/2020/02/15/muwnq.png)  
[首页预览](https://cdn.img.wenhairu.com/images/2020/02/15/muwnq.png)  
- - -
环境：Virtualenv(Python3.7)  
数据库：Mysql+Redis  
部署：Tornado+Nginx  
大致实现了登录注册、搜索、点赞收藏、弹幕、视频审核、评论、后台管理等
- - -
Usage
* 按config.py配置环境变量、数据库
* 执行pip install -r requirements.txt
* 运行Cyakka.py下的create_db_table
* 运行Cyakka.py的app.run()直接启动
* 或开启Nginx并运行tornado_server.py部署到nginx上
- - -
