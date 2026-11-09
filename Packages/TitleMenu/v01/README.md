# 侠客行封面、我的菜单存读入口与 Esc 交付包

2026-11-09 · 需求 v0.1 / 封面美术 v0.4

- [本轮需求](Requirements/TitleMenu/v01/侠客行封面与我的存读入口需求.md)
- [封面资源及导入说明](UI/TitleScreen/v04/README.md)
- [原定稿图](UI/TitleScreen/v04/Reference/title-approved.png)
- [拆分资源重组参考](UI/TitleScreen/v04/Reference/title-layered-reconstruction.png)
- [复用存读界面资源](UI/SaveLoad/v01/README.md)

范围：已确认的简笔水墨“侠客行”封面及五项菜单；游戏内保存/读取放在已有“我的”；Esc 按最高层优先消费，空闲时打开/关闭“我的”；新游戏、读档及返回标题复用已有系统。

本包同时包含无文字背景、透明标题和菜单笔刷、布局参数、来源及提取脚本，并复用原存读UI资源。按钮文字单独渲染，不以整图替代交互。笔刷复用存档轮廓，重组参考如实展示与原定稿的差异；实际中文字体与按钮需目标工程校验。

存读资源旧说明保留为来源记录。若其入口规则/历史“待确认”表述与本次需求冲突，以本轮需求为准；不要求重复制作已经接入的存档系统，也不覆盖已有GUID。

尚未在 Unity 接入或验收，不含 Prefab、.meta、字体或游戏代码。本次仅上传仓库，未通知家里实施。checksums.json记录本包内容SHA256（不含自身）。
