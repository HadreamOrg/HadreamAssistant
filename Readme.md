# HadreamAssistant--A high custom voice assistant
- HadreamAssistant是为了创造您自己的语音应用（助手）而生的。
  - 你可以通过语音、键盘、微信进行自然语言交互，帮助您完成各种工作，甚至于帮助您的团队完成各项工作
  - 也可以自己自定义修改代码或者编写新的技能，在现有的交互系统上，使HA达到你想要的功能

### SimpleUsage
- git clone或者下载zip到Raspbian/Ubuntu等Linux系统上
  - 如果你使用的是Raspbian，那接下来很简单
    - 只需安装好python3环境以及pyaudio opencv-python keyboard 等库即可（缺什么就会报错，直接pip3 install就好了）
    - 然后sudo apt-get install swig
    - 然后cd HadreamAssistant
    - python3 run.py
    - 正常情况下就启动了，会有日志记录，在./backend/data/logs里面
  - 如果你使用的是别的系统（不支持windows）
    - 请再去snowboy的项目下面，找到编译教程，选择合适自己的系统按着教程走
      - 得到_snowboydetect.so与snowboydetect.py替换./backend/bot/snowboy下面相应的文件
    - 然后安装好相应环境（参考raspbian）即可运行
- 默认唤醒词是snowboy，你也可以在./backend/data/json/setting.json中还掉（写入相应的模型路径即可）

### Features
- 使用Snowboy语音唤醒引擎，支持自定义唤醒词，原生支持Alexa/Computer/Snowboy/Jarvis
- VAD支持
- 可配合红外传感器及摄像头实现人脸检测、人脸识别
- 高自定义性的技能
- 原生支持Notion
  - 通过NotionBase可以实现对notion的自定义操作
  
### Components
#### FolderStructure
-  Backend
  - 后端部分，为的是后期可能有前端而设计的
  - api
  - bot
  - data 
  
#### ProgramStructure
  
#### Used
- ai
  - AI能力全部来自百度
  - 人脸识别（人脸认证）
  - 语音识别（语音识别极速版）
  - 语音合成
  - 语法依存分析
  - 文本纠错
- snowboy
  - 一款离线语音唤醒引擎，目前已经停止维护，没有新的umdl，但是还可以有pmdl使用
- vad
  - 使用来自CSDN-的运用webrtcvad实现的vad解决方案
- 还有很多别的都是从小蓝移植过来的，所以HA可以算是小蓝的再重启了

