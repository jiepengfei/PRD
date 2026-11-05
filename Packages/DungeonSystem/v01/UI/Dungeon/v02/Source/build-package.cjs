const fs=require('fs'),path=require('path');
const modules='C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const sharp=require(path.join(modules,'sharp'));
const {chromium}=require(path.join(modules,'playwright'));
const root=path.resolve(__dirname,'..');
async function main(){
 const input=path.join(__dirname,'user-flat-icon-sheet.png');
 const names=['battle','boss','chest','story','charm','explore','shop','forge','supply','portal'];
 const records=[];
 for(let k=0;k<10;k++){
  const col=k%5,row=Math.floor(k/5);
  const {data,info}=await sharp(input).extract({left:col*290,top:row?575:230,width:col===4?288:289,height:row?285:290}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  for(let i=0;i<data.length;i+=4){const max=Math.max(data[i],data[i+1],data[i+2]);const alpha=Math.max(0,Math.min(1,(max-16)/20));data[i+3]=Math.round(alpha*255);if(alpha>0&&alpha<1)for(let c=0;c<3;c++)data[i+c]=Math.min(255,Math.round(data[i+c]/alpha));}
  const file=`Assets/Icons/ui_dungeon_${names[k]}_v001.png`;
  await sharp(data,{raw:info}).resize(256,256,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).png().toFile(path.join(root,file));
  const stats=await sharp(path.join(root,file)).stats();
  records.push({id:names[k],file,width:256,height:256,alphaMin:stats.channels[3].min,alphaMax:stats.channels[3].max});
 }
 fs.writeFileSync(path.join(root,'Data/icon-manifest.json'),JSON.stringify({source:'User-selected second icon set (flat)',alpha:'Near-black matte converted to alpha; inspect edges in Unity',unityTested:false,icons:records},null,2));
 const icons=Object.fromEntries(records.map(r=>[r.id,'data:image/png;base64,'+fs.readFileSync(path.join(root,r.file)).toString('base64')]));icons.fight=icons.battle;
 const sourcePath=process.env.DUNGEON_VARIANTS_SOURCE||'C:/Users/admin/.codex/visualizations/2026/10/29/01a18649-d1d8-7e83-a042-ad2dc7a65a20/dungeon-icon-variants.html';
 let fragment=fs.readFileSync(sourcePath,'utf8');
 fragment=fragment.replace(/<section data-variant="水墨质感"[\s\S]*?<\/section>\s*/, '');
 fragment=fragment.replace('<section data-variant="简约平涂" aria-label="第二套简约平涂图标" hidden>','<section aria-label="定稿简约平涂图标">');
 fragment=fragment.replace(/class="viz-carousel"[^>]*>/,'aria-label="地下城UI定稿">');
 fragment=fragment.replace('document.getElementById(\'dungeon-flat\')];','document.getElementById(\'dungeon-flat\')].filter(Boolean);');
 fragment=fragment.replace(/(<script type="application\/json" id="dungeon-reference-assets">)[\s\S]*?(<\/script>)/,(_,a,b)=>a+JSON.stringify([icons])+b);
 fragment=fragment.replace('filter:url(#dungeon-remove-black)','filter:none');
 fs.writeFileSync(path.join(__dirname,'dungeon-approved.html'),fragment);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const errors=[];
 try{
  const page=await browser.newPage({viewport:{width:736,height:700},deviceScaleFactor:2});
  page.on('pageerror',e=>errors.push(e.message));
  await page.setContent(fragment);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  await page.locator('#dungeon-flat').screenshot({path:path.join(root,'Reference/dungeon-approved.png')});
  fs.mkdirSync(path.join(root,'Assets/Backgrounds'),{recursive:true});
  await page.locator('#dungeon-flat').evaluate(el=>{for(const child of el.children)child.style.visibility='hidden';});
  await page.locator('#dungeon-flat').screenshot({path:path.join(root,'Assets/Backgrounds/ui_dungeon_paper_v001.png')});
  await page.locator('#dungeon-flat').evaluate(el=>{for(const child of el.children)child.style.visibility='';});
  if(await page.locator('.node').count()!==6)throw Error('Approved preview must have six sample nodes');
  await page.locator('.current').click();if(!(await page.locator('.status').innerText()).includes('已进入'))throw Error('Click feedback failed');
  await page.setViewportSize({width:320,height:700});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Narrow layout overflow');
  await page.setViewportSize({width:736,height:650});
  await page.evaluate(icons=>{
   const route=document.querySelector('.route');route.style.cssText='position:relative;display:block;height:265px;margin:18px 0 15px;';
   const nodes=[['story','入口',55,135],['battle','路线一',280,65],['battle','路线二',280,210],['supply','汇合补给',570,135]];
   const lines=[[95,135,240,65],[95,135,240,210],[320,65,530,135],[320,210,530,135]];
   route.innerHTML='<svg aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%" viewBox="0 0 680 265">'+lines.map(([a,b,c,d])=>`<path d="M${a} ${b} L${c} ${d}" stroke="#adb6a2" stroke-width="2" fill="none"/>`).join('')+'</svg>'+nodes.map(([key,label,x,y],i)=>`<div class="node ${i===1||i===2?'current':''}" style="position:absolute;left:${x-40}px;top:${y-40}px"><img class="icon" src="${icons[key]}" alt=""><span class="label">${label}</span>${i===0?'<span class="mask"></span>':''}</div>`).join('');
   document.querySelector('header small').textContent='分叉与汇合 · 布局示意';document.querySelector('.status').textContent='';
  },icons);
  await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  await page.locator('#dungeon-flat').screenshot({path:path.join(root,'Reference/branch-layout-example.png')});
  const sheets=records.map((r,i)=>`<div style="width:150px;padding:15px 5px;text-align:center"><img src="${icons[r.id]}" style="width:100px;height:100px;object-fit:contain"><div style="font:13px Microsoft YaHei">${['战斗','首领','宝箱','剧情','符牌','探索','商铺','锻造','补给','传送'][i]}</div></div>`).join('');
  await page.setContent(`<div style="display:flex;flex-wrap:wrap;width:750px;background:#f3f0e7;color:#354d40">${sheets}</div>`);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  await page.locator('body>div').screenshot({path:path.join(root,'Reference/icons-contact-sheet.png')});
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(root,'Data/preview-checks.json'),JSON.stringify({approvedIcons:10,sampleNodes:6,clickFeedback:true,narrow320NoOverflow:true,runtimeErrors:errors,unityTested:false},null,2));
 }finally{await browser.close();}
 console.log('Exported 10 PNGs, approved preview, branch layout example, contact sheet and preview checks');
}
main().catch(e=>{console.error(e);process.exit(1)});
