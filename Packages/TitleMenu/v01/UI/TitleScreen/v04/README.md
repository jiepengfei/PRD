# 侠客行标题菜单美术交付

2026-11-09。以用户确认的 v03 简笔人物水墨封面为准。

- `Reference/title-approved.png`：原定稿效果图，含菜单文字，仅作还原参考。
- `Assets/title-background.png`：imagegen 从定稿中去除标题、印章、菜单和选中笔触后的背景，使用原比例。
- `Assets/title-logo.png`：从定稿提取的书法标题及小印，真实 Alpha，保留少量自然飞白，不能二次压缩成不透明图。
- `Assets/menu-selected-brush.png`：复用既有存档笔刷 Alpha 轮廓，转为菜单使用的灰墨色；非原图的精确笔触复制，接入时按参考尺寸校验观感。
- `Data/layout.json`：原图坐标、图层和菜单参考布局。菜单文字不在运行时图片内。
- `Source`：生成与提取来源记录。

复用目标工程中文字体、CanvasScaler、UI栈和既有存读界面；本包没有 Unity Prefab、.meta 或字体文件，不伪造已完成接入。

PNG 按 Sprite/UI、Single、Full Rect、sRGB、Alpha Is Transparency、Clamp、Bilinear、无 MipMaps 导入。背景 Max Size 至少2048，不得被平台覆盖缩小；标题与笔触不做 Tight 自动裁剪以免对齐变化。真实尺寸和源区域见布局JSON。

图片与文字分层，透明标题必须保持原宽高比；背景按屏幕等比适配，菜单保持左侧安全区，不随背景裁切丢失。常态菜单黑墨，选中时灰墨笔刷＋浅色文字，禁用状态复用项目规范。

存档 UI 美术在本交付包 `UI/SaveLoad/v01`，属于复用资源，不要求重做窗口或覆盖现有 GUID。其历史说明若与本轮入口安排冲突，以本轮标题/我的菜单需求为准。
