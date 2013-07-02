一个简单的运行在SAE上的Blog
======
简单到只有以下功能

1. 发表日志，日志支持加密功能

2. 只支持tag，虽然有分类功能，但感觉实在无用

3. 编辑器为简单的Textarea配合一些js，实现简易Markdown编辑

4. 评论支持Markdown

5. 对于上传的附件，默认存储于sae Storage。并且自动设置为365天过期

6. sae上需要开启mysql/memcached服务



**Require**

Flask / Jinja / MySQLdb 



请将 **setting_sample.py** 重命名为 **setting.py** 

Demo:

<http://yibin.im>