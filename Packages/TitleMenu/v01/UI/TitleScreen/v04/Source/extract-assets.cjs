const fs=require('fs'),path=require('path');
const deps='C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const sharp=require(path.join(deps,'sharp'));
const root=path.resolve(__dirname,'..');
async function main(){
 const original=path.join(root,'Reference/title-approved.png');
 const logoRect={left:50,top:60,width:620,height:300};
 const {data,info}=await sharp(original).extract(logoRect).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++){
  const i=(y*info.width+x)*4,r=data[i],g=data[i+1],b=data[i+2];
  const lum=.2126*r+.7152*g+.0722*b,red=r-g>30&&r-b>25;
  let alpha=red?Math.max(0,Math.min(1,(r-g)/85)):Math.max(0,Math.min(1,(205-lum)/155));
  if(x+logoRect.left>610&&y+logoRect.top>300)alpha=0;
  data[i]=red?159:35;data[i+1]=red?62:36;data[i+2]=red?48:32;data[i+3]=Math.round(alpha*255);
 }
 await sharp(data,{raw:info}).png().toFile(path.join(root,'Assets/title-logo.png'));
 const brushSource=process.env.TITLE_BRUSH_SOURCE||path.resolve(root,'../../SaveLoad/v01/Assets/WuxiaVillage/Art/UI/SaveLoad/Panels/ui_save_slot_selected_v001.png');
 const brush=await sharp(brushSource).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 for(let i=0;i<brush.data.length;i+=4){brush.data[i]=76;brush.data[i+1]=77;brush.data[i+2]=72;}
 await sharp(brush.data,{raw:brush.info}).png().toFile(path.join(root,'Assets/menu-selected-brush.png'));
 const bg=await sharp(path.join(root,'Assets/title-background.png')).metadata();
 const layout={referenceWidth:1672,referenceHeight:941,coordinateOrigin:'top-left',background:{width:bg.width,height:bg.height,preserveAspect:true},logo:{x:50,y:60,width:620,height:300,preserveAspect:true},menu:{centerX:280,firstCenterY:429,rowGap:81,fontFamily:'Reuse project Chinese font, serif/calligraphy preferred',referenceFontSize:40,items:['开始游戏','继续游戏','读取存档','设置','退出游戏'],selectedBrush:{centerX:280,centerY:429,width:400,height:88},textColor:'#232420',selectedTextColor:'#F3F0E7'},unityTested:false};
 fs.writeFileSync(path.join(root,'Data/layout.json'),JSON.stringify(layout,null,2));
 const records=[];for(const name of ['title-background.png','title-logo.png','menu-selected-brush.png']){const p=path.join(root,'Assets',name),m=await sharp(p).metadata(),s=await sharp(p).stats();records.push({file:'Assets/'+name,width:m.width,height:m.height,hasAlpha:!!m.hasAlpha,alphaRange:m.hasAlpha?[s.channels.at(-1).min,s.channels.at(-1).max]:null});}
 fs.writeFileSync(path.join(root,'Data/asset-manifest.json'),JSON.stringify({assets:records,unityTested:false},null,2));
 const {chromium}=require(path.join(deps,'playwright'));
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:1672,height:941},deviceScaleFactor:1});
  const img=n=>'data:image/png;base64,'+fs.readFileSync(path.join(root,'Assets',n)).toString('base64');
  await page.setContent(`<html><body style="margin:0"><div style="position:relative;width:1672px;height:941px;overflow:hidden"><img src="${img('title-background.png')}" style="position:absolute;inset:0;width:100%;height:100%"><img src="${img('title-logo.png')}" style="position:absolute;left:50px;top:60px;width:620px;height:300px"><img src="${img('menu-selected-brush.png')}" style="position:absolute;left:80px;top:385px;width:400px;height:88px">${layout.menu.items.map((label,i)=>`<div style="position:absolute;left:80px;top:${429+i*81-32}px;width:400px;text-align:center;font:40px/64px SimSun,serif;color:${i?'#232420':'#f3f0e7'};letter-spacing:4px">${label}</div>`).join('')}</div></body></html>`);
  await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  await page.screenshot({path:path.join(root,'Reference/title-layered-reconstruction.png')});
 }finally{await browser.close();}
 console.log('Extracted transparent logo/brush, generated layout and reconstructed reference');
}
main().catch(e=>{console.error(e);process.exit(1)});
