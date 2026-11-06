"""Reproducible non-combat procedural audition assets. Python 3 standard library only.
Run: python Audio/SFX/v02/Source/build.py (from workspace root).
No recordings, external samples, acoustic model, runtime game code or dependencies.
"""
from pathlib import Path
import math, random, wave, struct, json, hashlib, html, csv, io

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[2]
RATE = 44100
PI = math.pi

# id, Chinese name, family, seconds, file peak dBFS, UI gain, cooldown ms, voices
DEFS = [
 ('ui_wood_click','木扣·点击','wood',.13,-12,.55,75,1),
 ('ui_back','木扣·返回','back',.18,-12,.55,120,1),
 ('ui_confirm','竹扣·确认','confirm',.26,-10,.60,180,1),
 ('ui_unavailable','闷木·不可用／失败','deny',.24,-13,.55,500,1),
 ('ui_select','竹点·选择','select',.10,-15,.48,90,1),
 ('map_paper_flip_a','纸页·翻面甲','paper',.29,-14,.45,100,1),
 ('map_paper_flip_b','纸页·翻面乙','paper',.32,-14,.45,100,1),
 ('map_step_a','土石·落步甲','step',.15,-16,.45,160,1),
 ('map_step_b','土石·落步乙','step',.17,-16,.45,160,1),
 ('map_step_c','土石·落步丙','step',.14,-16,.45,160,1),
 ('map_revisit','纸风·重访落地','travel',.43,-13,.50,300,1),
 ('event_unlock','竹石·入口开放','unlock',.48,-10,.58,700,1),
 ('quest_accept','卷签·任务接取','accept',.55,-10,.60,800,1),
 ('quest_update','卷签·目标更新','update',.29,-13,.52,700,1),
 ('quest_complete','卷签·任务完成','complete',.77,-9,.60,1000,1),
 ('reward_coin','铜钱·到账','coin',.62,-11,.58,400,1),
 ('item_acquire','布袋·物品获得','item',.30,-13,.52,400,1),
 ('chest_open','木匣·开启','chest',.58,-11,.58,900,1),
 ('supply_restore','清息·补给恢复','restore',.91,-11,.60,1200,1),
 ('save_success','落笔·保存成功','save',.37,-13,.52,900,1),
 ('load_success','展卷·读取成功','load',.44,-13,.52,900,1),
 ('dungeon_enter','竹石·进入节点图','enter',.36,-12,.55,600,1),
 ('dungeon_progress','竹石·非战斗节点进度','progress',.36,-13,.52,700,1),
 ('story_transition','纸风·对白／CG转场','transition',.55,-16,.48,600,1),
 ('chapter_end','归卷·Demo结束','end',1.18,-10,.60,2500,1),
]

def pulse(t, start, frequency, decay, material='wood'):
    x=t-start
    if x < 0: return 0.
    attack=1-math.exp(-x/.0025)
    ratios = [(1,1),(1.48,.27),(2.19,.10)] if material=='bell' else [(1,1),(1.71,.30),(2.83,.09)]
    return attack*sum(a*math.sin(2*PI*frequency*r*x)*math.exp(-x/(decay/(1+j*.6))) for j,(r,a) in enumerate(ratios))

def render(d, index):
    sid,name,family,duration,db,*_=d
    n=round(duration*RATE); rng=random.Random(760611+index*7919)
    a=[]; low=mid=air=0.
    for i in range(n):
        t=i/RATE; u=t/duration; z=rng.uniform(-1,1)
        low += .035*(z-low); mid += .24*(z-mid); air += .09*((mid-low)-air)
        rustle=mid-low
        p=lambda s,f,d,m='wood': pulse(t,s,f,d,m)
        if family=='wood': v=p(0,620,.023)+.18*mid*math.exp(-t/.016)
        elif family=='back': v=p(0,490,.035)+.22*p(.065,330,.022)
        elif family=='confirm': v=.75*p(0,540,.04)+.65*p(.075,720,.045)
        elif family=='deny': v=p(0,240,.038)+.65*p(.095,205,.035)
        elif family=='select': v=p(0,850,.015)+.12*mid*math.exp(-t/.008)
        elif family=='paper':
            env=math.sin(PI*min(1,t/(duration*.86)))**1.5 if t<duration*.86 else 0
            v=2.2*rustle*env*(.7+.3*math.sin(2*PI*(29+index)*t))+.15*p(duration*.72,420,.017)
        elif family=='step': v=2.7*low*math.exp(-t/.028)+.18*air*math.exp(-t/.012)+.12*p(0,145+index*3,.024)
        elif family=='travel': v=2.0*air*math.sin(PI*u)**2+.3*p(.23,420,.055)
        elif family=='unlock': v=p(.02,440,.07)+.65*p(.13,660,.10,'bell')
        elif family=='accept': v=1.0*rustle*math.sin(PI*min(1,t/.21))**2*(t<.21)+.55*p(.19,520,.09)+.42*p(.27,650,.10,'bell')
        elif family=='update': v=.6*p(.01,580,.045)+.35*p(.085,710,.055)
        elif family=='complete': v=.6*p(.01,440,.13,'bell')+.5*p(.13,550,.16,'bell')+.4*p(.26,660,.18,'bell')
        elif family=='coin': v=.6*p(0,1140,.065,'bell')+.5*p(.07,1420,.075,'bell')+.23*p(.15,960,.08,'bell')
        elif family=='item': v=2.1*air*math.sin(PI*u)**2+.35*p(.08,380,.04)+.22*p(.14,530,.045)
        elif family=='chest': v=.35*p(0,280,.06)+1.2*low*math.exp(-((t-.18)/.09)**2)+.7*p(.28,420,.045)+.13*rustle*math.exp(-((t-.12)/.1)**2)
        elif family=='restore': v=.8*air*math.sin(PI*u)**2+.28*p(.03,330,.19,'bell')+.25*p(.16,440,.20,'bell')+.2*p(.30,550,.21,'bell')
        elif family=='save': v=1.1*rustle*math.exp(-((t-.09)/.06)**2)+.55*p(.19,510,.045)
        elif family=='load': v=1.1*rustle*math.sin(PI*min(1,t/.27))**2*(t<.27)+.35*p(.25,630,.055)
        elif family=='enter': v=p(.01,330,.055)+.55*p(.09,440,.07)
        elif family=='progress': v=.65*p(.01,460,.055)+.45*p(.10,580,.07)
        elif family=='transition': v=2.0*air*math.sin(PI*u)**2*(.8+.2*math.sin(2*PI*8*t))
        elif family=='end': v=.6*p(.02,440,.23,'bell')+.5*p(.20,330,.25,'bell')+.4*p(.42,220,.24,'bell')+.4*air*math.sin(PI*u)**2
        else: raise ValueError(family)
        # 4ms cosine attack and 45ms cosine release; suppress clicks and tail cut.
        fin=.5-.5*math.cos(PI*min(1,t/.004))
        fout=.5-.5*math.cos(PI*min(1,(n-1-i)/(RATE*.045)))
        a.append(v*fin*fout)
    mean=sum(a)/n
    # Remove DC while preserving zero endpoints with the same envelope.
    for i in range(n):
        t=i/RATE
        e=(.5-.5*math.cos(PI*min(1,t/.004)))*(.5-.5*math.cos(PI*min(1,(n-1-i)/(RATE*.045))))
        a[i]-=mean*e
    gain=10**(db/20)/max(map(abs,a))
    return [round(x*gain*32767) for x in a]

SOURCES = [
 'Standards/武侠新手村_资源生产与Unity交付标准_v1.0.md',
 'Requirements/DemoMainline/v01/主线闭环需求.md',
 *['Requirements/DemoMainline/v01/'+p for p in ['Step01_开场接取主线与倒计时.md','Step02_第一场山贼战斗与任务推进.md','Step03_第二场山贼战斗与首领入口开放.md','Step04_首领入口与第一场小兵战.md','Step05_小兵二补给与首领战.md','Step06_村长对话与离村出口开放.md']],
 'Requirements/SaveLoad/v01/存档系统需求方案.md',
 'Requirements/Dungeon/v01/地下城节点流程与UI需求.md',
 'Requirements/DemoFlow/v03/补给与送别CG接入需求.md',
 '地图探索与移动改造需求.md','Requirements/MapEventFlow/v02/地图系统改造需求方案.md',
 'Delivery/Inventory/v01/Documentation/需求文档.md','Delivery/QuestModule/v01/Documentation/需求文档.md',
 'Audio/SFX/v01/README.md','Audio/SFX/v01/Source/synthesize.cjs',
 'UI/Dialogue/v08/比例修订说明.md','UI/Dialogue/v07/动效修订说明.md',
 'UI/QuestJournal/v04/设计说明.md','UI/MapBanner/v04/设计说明.md',
 'UI/SaveLoad/v01/README.md','UI/Dungeon/v02/README.md',
]

# module, usage, ids, exact trigger, exclusivity/coalescing, priority, status
ROWS = [
 ('通用UI','普通按钮','ui_wood_click','有效点击被最高层UI消费后；无业务音的开窗/标题返回入口','仅无更具体反馈时使用；不接hover或每帧按住',10,'已生成'),
 ('通用UI','返回／取消','ui_back','窗口实际关闭或确认框取消后','Esc只由最高层消费一次；取消离村不接转场',10,'已生成'),
 ('通用UI','普通确认','ui_confirm','无异步业务结果音的确认操作被接受后','存档/使用/补给/开箱/离村确认不叠此音',20,'已生成'),
 ('通用UI','选择／Tab／筛选','ui_select','选择对象或Tab真正改变一次后','重复选中无声；背包/任务/存档槽/地图详情/地下城共用',10,'已生成'),
 ('通用UI','不可用反馈','ui_unavailable','玩家主动尝试被规则拒绝，且已有可见原因提示时','禁用控件若不接收输入则无声；不得轮询失败连播',40,'已生成'),
 ('纸页','任务背景／背包分页／详情翻页','map_paper_flip_a|map_paper_flip_b','页码真正改变、翻页动画开始时','首末页拒绝不播；只播一枚；替代点击',10,'已生成'),
 ('地图','逐格移动落地','map_step_a|map_step_b|map_step_c','角色脚底真正落到目标格时，每格最多一次','无连续步态证据，不按动画帧造连续脚步；三变体轮换避重复',10,'已生成'),
 ('地图','免费重访／瞬移','map_revisit','权威位置已更新且目标落点准备好时','替代落步；不在点击目标时提前播',20,'已生成'),
 ('地图','首次揭示／大型组多米诺翻牌','map_paper_flip_a|map_paper_flip_b','首批可见翻面中点或揭示动画开始，二选一固定','共用flip组100ms节流；每批最多3枚，跨格不每格叠响；不再造揭示完成音',10,'已生成'),
 ('地图','入口／出口／事件可用','event_unlock','首领入口或离村出口从锁定变可用，实际状态提交且标记首次可见时','同批入口只一枚；已存在状态/读档不播；不播战斗启动/胜利',50,'已生成'),
 ('地图','详情／任务定位／事件预览','ui_select','详情首次打开、定位成功或预览选择真实改变后','只选中已有可知内容；不移动角色、不播脚步/解锁',10,'已生成'),
 ('地图','行动点不足／不可达','ui_unavailable','主动移动请求被拒绝并显示原因后','合并同次请求；未明确的未知格通行规则不自行定义',40,'已生成'),
 ('地图','休息恢复与日期推进','supply_restore','休息的HP/AP/日期统一提交成功后','替代确认；日期/期限UI刷新静默；不做烧抢或到期惩罚音',50,'已生成'),
 ('任务','新主线接取','quest_accept','报信正常结束或跳过，首次接取与期限登记成功，通知显示时','同次任务立即完成优先完成音；读档/重复回调静默',60,'已生成'),
 ('任务','非战斗目标变化','quest_update','对话/探索产生真实目标变更，通知显示时','合并700ms内更新；完成优先；战斗结果导致的更新本包不挂音',50,'已生成'),
 ('任务','非战斗任务完成','quest_complete','非战斗目标完成及自动奖励一致提交后','替代同事务accept/update/coin/item；战斗导致主线完成排除，沿用原工程声音',70,'已生成'),
 ('任务','展开／收起／筛选／定位','ui_wood_click|ui_select|ui_back','分组折叠/整栏收起为click；分类为select；关闭为back','每操作只一项；刷新补位/读档恢复静默；本轮不做支线置顶专属音',10,'已生成'),
 ('奖励','铜钱到账','reward_coin','非战斗奖励或获得事务已提交且正增量>0','同operationId只一次；混合奖励选coin；不与任务完成/宝箱同播；不接战斗结算',60,'已生成'),
 ('背包','物品获得','item_acquire','非战斗获得提交后出现正向增量提示','一批多物品只一枚；混合币奖励选coin；读档/初始填充/刷新不播',50,'已生成'),
 ('背包','草药等恢复品使用','supply_restore','恢复效果与扣物都提交成功后','共用补给音；满生命不扣不响恢复，主动拒绝可播deny；数量减少本身无音',60,'已生成'),
 ('背包','装备／卸下','ui_confirm','仅当实际工程存在装备接口，且装备状态成功改变后','无已核验运行时装备证据；暂不启用；无需额外金属声',20,'条件复用，待工程核对'),
 ('宝箱','开启反馈','chest_open','已有宝箱业务成功发奖并首次切为open外观时','单次开启用chest，抑制同事务coin/item；已开重访无声；不新增宝箱任务',60,'已生成，现有内容条件接入'),
 ('补给','首领关卡补给','supply_restore','补给CG正常完成或明确跳过，治疗和领取状态一起提交成功后','重复回调/重进/首领重试静默；不因打开CG提前播；替代节点进度音',70,'已生成'),
 ('存读档','手动保存／覆盖成功','save_success','存档服务确认正式文件替换及校验成功，成功提示显示时','确认覆盖按钮不播confirm；不是写临时文件即成功；连点合并',60,'已生成'),
 ('存读档','自动保存成功','save_success','仅需要声音辅助时，在事件稳定后写入成功提示时','默认静默；若开启音量0.25；与补给/任务/剧情音冲突时省略',5,'已生成，默认不启用'),
 ('存读档','读取成功','load_success','解析/校验/恢复全成功、地图就绪且存档窗口关闭后','只播load；恢复奖励/揭示/任务/落步/入口提示全部静默',70,'已生成'),
 ('存读档','保存／读取失败','ui_unavailable','服务返回失败并显示原因/重试提示时','共享失败音；同次尝试一枚；自动保存失败最多10秒一次，成功前不播成功音',80,'已生成'),
 ('地下城','打开／重进节点图','dungeon_enter','节点数据加载完成且图真正首次显示时','替代普通开窗点击；状态恢复不播节点完成；非战斗界面声',20,'已生成'),
 ('地下城','节点选择','ui_select','可进入的非战斗节点请求被接受并锁定时','直接执行无二次按钮；若立即转场则省select；战斗节点点击本包不挂音',20,'已生成'),
 ('地下城','非战斗节点进度','dungeon_progress','对话/CG等非战斗节点提交完成并回节点图稳定时','补给/宝箱/章节有专属音则抑制；不接战斗节点√或地下城战斗胜利',40,'已生成'),
 ('地下城','不可进入／已完成节点','ui_unavailable','主动点击并出现明确拒绝提示时','若现有UI为静默忽略则保持无声；不每次刷新红边播音',30,'已生成'),
 ('对白／CG','打开／换段转场','story_transition','对白或CG实际开始可见转场时，一段一枚','补给/送别共用；非每句/每字；跳过不追播未见内容；视频自带音轨需避让',20,'已生成'),
 ('对白／CG','手动下一句／选择','ui_select','玩家主动推进至下一句或确认已有对白选项时','低音量0.30，自动推进静默；段落切换有transition则省select',10,'已生成'),
 ('对白／CG','跳过确认／异常退出','ui_back|ui_unavailable','取消跳过为back；资源失败提示为deny；正常跳过执行统一业务结果音','不将关闭窗口视为完成；正常跳过不补播整段声音',30,'已生成'),
 ('章节','离村确认与送别','story_transition','确认离村通过前置检查且送别画面已可见时','确认按钮不另播confirm；取消仅back；出口取消不每帧重触发',30,'已生成'),
 ('章节','Demo结束','chapter_end','送别完成或明确跳过后，章节完成提交且结束页首次显示时','仅章节结束，非战斗胜利声；同chapter一次，读档恢复结束页静默；返回标题用click',80,'已生成'),
]

def write_json(file,data):
    (ROOT/file).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    (ROOT/'WAV').mkdir(parents=True,exist_ok=True)
    sounds=[]
    for idx,d in enumerate(DEFS):
        sid,name,family,duration,db,volume,cooldown,voices=d
        values=render(d,idx); rel=f'WAV/sfx_{sid}_v002.wav'
        with wave.open(str(ROOT/rel),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
            w.writeframes(struct.pack('<'+'h'*len(values),*values))
        sounds.append(dict(id=sid,name=name,file=rel,family=family,variantGroup='map_step' if family=='step' else 'paper_flip' if family=='paper' else sid,
                           sampleRate=RATE,channels=1,bits=16,frames=len(values),durationSeconds=len(values)/RATE,targetPeakDbFS=db,
                           suggestedVolume=volume,cooldownMs=cooldown,maxVoices=voices,loop=False,status='procedural_audition_placeholder',
                           sha256=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()))
    by_id={s['id']:s for s in sounds}
    mappings=[]
    for module,use,ids,trigger,rule,priority,status in ROWS:
        refs=ids.split('|')
        mappings.append(dict(module=module,use=use,ids=refs,trigger=trigger,sharingAndSuppression=rule,priority=priority,status=status,
                             files=[by_id[x]['file'] for x in refs],suggestedVolume=[by_id[x]['suggestedVolume'] for x in refs],
                             cooldownMs=max(by_id[x]['cooldownMs'] for x in refs),maxVoices=1))
    write_json('manifest.json',dict(version=2,date='2026-11-06',source='deterministic Python procedural synthesis; no external samples',
        status='试听/占位；数值检查不等于听感验收',engineIntegrated=False,listenedByAgent=False,
        spec=dict(sampleRate=RATE,channels=1,bits=16,format='PCM little endian WAV',attackMs=4,releaseMs=45),
        globalPolicy=dict(maxVoices=4,criticalReserve=1,priority='larger wins; error/chapter > outcome > presentation > steps/paper',
                          dedupKey='session + operationId + semanticOutcome; retain successful operations for session',
                          cooldownClock='monotonic unscaled time; group-wide, not per-variant',
                          eventSuppression='one semantic outcome per operation; exclude combat-origin events; never replay restored state'),sounds=sounds,mappings=mappings))
    with (ROOT/'适配表.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['模块','用途','稳定SFX ID（选一，不全播）','具体触发时机','共享／抑制','建议线性音量','组冷却ms','最大并发','优先级','状态','包内相对路径'])
        for m in mappings: w.writerow([m['module'],m['use'],' | '.join(m['ids']),m['trigger'],m['sharingAndSuppression'],' | '.join(map(str,m['suggestedVolume'])),m['cooldownMs'],1,m['priority'],m['status'],' | '.join(m['files'])])
    md=['# 非战斗音效适配表 v02','','路径相对于本包根目录；多个 ID 是按操作选一或变体池，不表示同时播放。线性音量是现有SFX总线下的起调建议。完整机器可读字段见 manifest.json 和 CSV。','','|模块／用途|稳定ID、文件与起调音量|触发时机|去重／抑制|冷却／并发／优先级|状态|','|---|---|---|---|---|---|']
    for m in mappings:
        links='<br>'.join(f"[{sid}]({by_id[sid]['file']}) · {by_id[sid]['suggestedVolume']}" for sid in m['ids'])
        md.append(f"|{m['module']}／{m['use']}|{links}|{m['trigger']}|{m['sharingAndSuppression']}|{m['cooldownMs']}ms / 1 / {m['priority']}|{m['status']}|")
    (ROOT/'适配表.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    source_records=[]
    for rel in SOURCES:
        p=PROJECT/rel
        source_records.append(dict(file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    write_json('sources.json',dict(scope='仅当前本机需求与资源盘点；未遍历家里实时Unity工程；不以旧源码证明现状',references=source_records))
    cards=[]
    for s in sounds:
        uses='；'.join(m['module']+'／'+m['use'] for m in mappings if s['id'] in m['ids'])
        cards.append(f'<article><h2>{html.escape(s["name"])}</h2><code>{s["id"]}</code><p>{s["durationSeconds"]:.2f}s · 峰值目标 {s["targetPeakDbFS"]}dBFS · 建议音量{s["suggestedVolume"]}</p><audio controls preload="none" src="{s["file"]}"></audio><p>{html.escape(uses)}</p><a href="{s["file"]}" download>下载 WAV</a></article>')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>武侠 Demo · 非战斗音效 v02</title><style>body{margin:0;background:#f0eee6;color:#293d36;font:16px/1.65 system-ui,sans-serif}main{max-width:1100px;margin:40px auto;padding:0 24px}h1{font-size:30px}header{border-bottom:2px solid #637364;padding-bottom:22px}a{color:#8b463b}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:24px}article{padding:20px;background:#faf9f3;border:1px solid #d6d4c7}h2{font-size:19px;margin:0 0 8px}code{font-size:13px}p{font-size:14px}audio{width:100%}button{padding:8px 18px;background:#314b40;color:white;border:0;cursor:pointer}small{display:block}</style><main><header><h1>武侠 Demo · 非战斗音效 v02</h1><p>25枚 WAV · 纸、木、竹石与低亮度铜铃意象。纯程序合成试听／占位；未接入 Unity，未完成主观听感或游戏内混音验收。</p><p>请先调低系统音量，再逐项播放。页面原生播放器播放文件原始电平；下方“建议音量”是游戏内起调值。无自动播放或外部依赖。</p><button id="stop">停止播放</button> <a href="适配表.md">适配表</a> · <a href="适配表.csv">CSV</a> · <a href="QA/validation.json">数值检查</a><small>一次只播放一枚；所有音频采用包内相对路径，解压后打开本页即可试听。</small></header><section>'''+''.join(cards)+'''</section></main><script>const players=[...document.querySelectorAll('audio')];players.forEach(a=>a.addEventListener('play',()=>players.forEach(b=>{if(b!==a){b.pause();b.currentTime=0}})));document.querySelector('#stop').onclick=()=>players.forEach(a=>{a.pause();a.currentTime=0});</script></html>'''
    (ROOT/'试听.html').write_text(page,encoding='utf-8')
    print(f'Generated {len(sounds)} WAV files, {len(mappings)} mappings.')

if __name__=='__main__': main()
