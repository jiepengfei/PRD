# 新手村 Demo · 非战斗音频与完整需求

日期：2026-11-06。解压整个文件夹后使用，目录结构请保持不变。

- [完整接入需求](Requirements/Audio/v01/非战斗音效完整接入需求.md)：范围、25枚资源、36条适配、触发规则、去重并发、实施与验收。
- [逐项试听](Audio/SFX/v02/试听.html)：原生播放器，使用相对音频路径。
- [适配表](Audio/SFX/v02/适配表.md) · [CSV](Audio/SFX/v02/适配表.csv) · [manifest](Audio/SFX/v02/manifest.json)。
- [资源说明与复现](Audio/SFX/v02/README.md) · [数值检查](Audio/SFX/v02/QA/validation.json)。

WAV在Audio/SFX/v02/WAV；生成、验证和资源包脚本在Audio/SFX/v02/Source。附带旧版资源专用ZIP，方便沿用原需求中的下载链接；它与展开目录中的音频相同，不必重复导入。

全部素材为程序合成试听／占位资源；已完成文件与数值检查，未实际试听、接入Unity或验收游戏混音。排除战斗音、BGM和配音。

为便于独立交付，本包完整需求中的外围业务文档引用以项目原始路径说明，未附带无关美术与其他模块交付包。需求原文件SHA-256及该处理范围见delivery-manifest.json。音频资源原文件未修改。

checksums.sha256覆盖包内全部文件（自身除外）；ZIP旁SHA文件用于核对整个压缩包。
