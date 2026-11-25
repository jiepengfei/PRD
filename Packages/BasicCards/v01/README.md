# 20张基础卡牌交付

执行要求见 ../../../Requirements/BasicCards/v01/20张基础卡牌替换实施需求.md。

用户授权家里电脑实施，完整替换玩家卡牌集合。20张初学卡，初始10种各1张，另外10种作为获取池。
Data/PlayerDeck.json 是初始列表。Data/RewardPool.ids.json 是获取池ID列表，需接入工程现有获取机制。
ArtAndData 包含20张插画、CardData设计审阅配置、6张可映射效果样例、原数值表和4张五卡预览。
最终须实现全部20张效果并替换Cards.json；6张样例文件是实施参考。
插画来自带纸底裁图，未提供独立透明大图。具体尺寸和缺口见ArtAndData/说明.txt。
