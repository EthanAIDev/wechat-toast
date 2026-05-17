# wechat-toast

适用于 Windows 的微信 4.x 桌面消息弹窗提醒工具，支持浮层通知/win系统通知。

本项目基于 [fenqijun/wechat-notifier](https://github.com/fenqijun/wechat-notifier) 修改而成，当前版本主要面向微信 4.x，重点优化了未读会话扫描、本地浮层通知样式和回退探测逻辑。

## 功能

- 支持微信桌面版 4.x
- 只提醒未读消息，尽量避免误读自己发出的内容
- 默认使用本地浮层通知，也支持 Windows 系统通知
- 同一会话连续来消息时，会直接刷新同一张通知卡片
- 显示未读数量和最新一条消息摘要
- 支持过滤折叠聊天、公众号、服务号、免打扰等干扰项

## 示例图

![通知效果示例](./test_pic.png)

## 运行环境

- Windows 10 / 11
- 微信桌面版 4.x
- Python 3.10+（推荐）

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 启动方式

```powershell
python .\wechat-toast.py
```

如果你使用项目内虚拟环境：

```powershell
.\.venv\Scripts\python.exe .\wechat-toast.py
```

## 常用配置

配置位于 [wechat-toast.py](./wechat-toast.py) 顶部。

- `NOTIFICATION_MODE = "overlay"`：本地浮层通知，默认推荐
- `NOTIFICATION_MODE = "system"`：Windows 系统通知
- `WECHAT_NOTIFIER_LOG_LEVEL=DEBUG`：开启调试日志

## 已知问题

当前版本已经可以满足基本使用，但仍有以下已知问题：

1. 只有当微信主界面处于前台可见状态时，程序才能稳定生效。  
   未显示在前台时参考：![未显示在前台](./未显示在前台.png)  
   已显示在前台时参考：![显示在前台](./显示在前台.png)

2. 点击通知后，目前可以拉起微信主窗口，但还不能自动精确定位到对应会话，后续会继续考虑修复。

3. 当鼠标悬浮在任务栏中闪烁的微信图标上时，可能会再次触发一次通知，后续会继续考虑修复。

## 更新记录

### 当前版本

- 合并为单文件入口 `wechat-toast.py`
- 完全转向微信 4.x 桌面版适配
- 重做本地浮层通知样式与布局
- 增强未读会话探测与多层回退逻辑
- 将微信图标内嵌到代码中，不再依赖额外图片文件

## 致谢

- 上游项目：[fenqijun/wechat-notifier](https://github.com/fenqijun/wechat-notifier)
- 本项目当前版本的设计、调试、重构与实现过程，全程主要通过 Codex 协作完成
