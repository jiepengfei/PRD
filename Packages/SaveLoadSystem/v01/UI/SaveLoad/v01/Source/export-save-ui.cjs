// File Path: UI/SaveLoad/v01/Source/export-save-ui.cjs
// Responsibility: Export the approved code-native preview into transparent UI assets and reference images.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const modules = process.env.SAVE_UI_NODE_MODULES || 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const { chromium } = require(path.join(modules, 'playwright'));
const sharp = require(path.join(modules, 'sharp'));
const packageRoot = path.resolve(__dirname, '..');
const assetRoot = path.join(packageRoot, 'Assets/WuxiaVillage/Art/UI/SaveLoad');
const scale = 2;
const fragment = fs.readFileSync(path.join(__dirname, 'save-load-approved.html'), 'utf8');
const css = fragment.match(/<style>([\s\S]*?)<\/style>/)[1];
const errors = [];
const records = [];
const slotsSelector = '#jianghu-save-preview';
const safeText = text => text.replace(/[&<>]/g, value => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[value]));

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: process.env.SAVE_UI_BROWSER || 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  try {
    const context = await browser.newContext({ viewport: { width: 850, height: 1000 }, deviceScaleFactor: scale, colorScheme: 'light', reducedMotion: 'reduce' });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.setContent(`<html><head><meta charset="utf-8"><style>html,body{margin:0;background:transparent}button{cursor:pointer}</style></head><body>${fragment}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => [...document.querySelectorAll('.slot-brush')].every(canvas => canvas.width > 0));
    const layout = await page.evaluate(() => {
      const root = document.querySelector('.save-window');
      const parent = root.getBoundingClientRect();
      const rect = element => { const box = element.getBoundingClientRect(); return { x: +(box.x-parent.x).toFixed(2), y: +(box.y-parent.y).toFixed(2), width: +box.width.toFixed(2), height: +box.height.toFixed(2) }; };
      const selectors = { title:'.save-title',subtitle:'.save-caption',returnButton:'.save-close',modeTabs:'.save-mode',slotList:'.slot-list',details:'.detail',primaryButton:'[data-main]' };
      const components = Object.fromEntries(Object.entries(selectors).map(([key, selector]) => [key,rect(document.querySelector(selector))]));
      components.slots = [...document.querySelectorAll('[data-slot]')].map(element => ({ logicalSlotIndex: +element.dataset.slot, ...rect(element) }));
      const textStyles = {};
      for (const selector of ['.save-title','.slot-name','.slot-note','.detail-heading','.detail-description','.primary-action']) {
        const computed = getComputedStyle(document.querySelector(selector));
        textStyles[selector] = { fontSize:computed.fontSize,lineHeight:computed.lineHeight,fontFamily:computed.fontFamily,color:computed.color };
      }
      const title = document.querySelector('.save-title').getBoundingClientRect();
      const close = document.querySelector('.save-close').getBoundingClientRect();
      return { referenceWidth:parent.width,referenceHeight:parent.height,coordinateOrigin:'top-left',exportScale:2,appearance:'approved light theme',components,textStyles,returnTitleCenterDifference:Math.abs(title.y+title.height/2-close.y-close.height/2) };
    });
    if (layout.returnTitleCenterDifference > 2) throw new Error('Return control and title no longer align');
    await page.locator('.save-window').screenshot({ path:path.join(packageRoot,'Reference/save-load-approved.png'), omitBackground:true });
    await page.locator('[data-main]').click();
    await page.locator('.confirm-box').screenshot({ path:path.join(packageRoot,'Reference/save-load-confirm.png'), omitBackground:true });
    const confirmRect = await page.locator('.confirm-box').boundingBox();
    const primaryRect = await page.locator('[data-confirm]').boundingBox();
    const secondaryRect = await page.locator('[data-cancel]').boundingBox();
    await page.locator('[data-cancel]').click();
    await page.locator('[data-mode="save"]').click();
    await page.locator('[data-slot="2"]').click();
    if (await page.locator('[data-main]').isDisabled()) throw new Error('Empty save slot unavailable in save mode');
    await page.locator('.name-input').fill('分步验证');
    await page.locator('[data-main]').click();
    await page.locator('[data-confirm]').click();
    if (!(await page.locator('[data-slot="2"]').innerText()).includes('分步验证')) throw new Error('Save interaction did not update');
    await page.locator('[data-slot="3"]').click();
    if (!(await page.locator('[data-main]').isDisabled())) throw new Error('Auto slot should not allow manual overwrite');
    await page.locator('[data-mode="load"]').click();
    await page.locator('[data-slot="0"]').click();

    async function register(relative, width, height, usage, imageType='Simple', border=[0,0,0,0]) {
      const file=path.join(assetRoot,relative);
      const metadata=await sharp(file).metadata();
      const raw=await sharp(file).ensureAlpha().raw().toBuffer();
      let minAlpha=255,maxAlpha=0;
      for(let offset=3;offset<raw.length;offset+=4){minAlpha=Math.min(minAlpha,raw[offset]);maxAlpha=Math.max(maxAlpha,raw[offset]);}
      records.push({ id:path.basename(relative,'.png'),file:relative,width:metadata.width,height:metadata.height,displayWidth:width,displayHeight:height,usage,hasAlpha:metadata.hasAlpha,alphaMin:minAlpha,alphaMax:maxAlpha,pivot:[.5,.5],spriteMode:'Single',meshType:'FullRect',filterMode:'Bilinear',wrapMode:'Clamp',mipmaps:false,pixelsPerUnit:100,imageType,borderPixels:border,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') });
    }
    async function exportBrush(relative, selected, empty=false) {
      await page.locator(`[data-slot="${selected?0:1}"]`).click();
      await page.waitForTimeout(40);
      const data=await page.locator('[data-slot="0"] canvas').evaluate(canvas=>canvas.toDataURL('image/png'));
      const destination=path.join(assetRoot,relative);fs.mkdirSync(path.dirname(destination),{recursive:true});
      let source=sharp(Buffer.from(data.split(',')[1],'base64'));
      if(empty){const raw=await source.ensureAlpha().raw().toBuffer({resolveWithObject:true});for(let index=3;index<raw.data.length;index+=4)raw.data[index]=Math.round(raw.data[index]*.52);source=sharp(raw.data,{raw:{width:raw.info.width,height:raw.info.height,channels:4}});}
      await source.png().toFile(destination);
      const r=layout.components.slots.find(slot=>slot.logicalSlotIndex===0);
      await register(relative,r.width,r.height,empty?'空白槽浅墨底':'同一形状的'+(selected?'选中浓墨':'未选中淡墨')+'存档底；左下右上飞白4:6');
    }
    await exportBrush('Panels/ui_save_slot_normal_v001.png',false);
    await exportBrush('Panels/ui_save_slot_selected_v001.png',true);
    await exportBrush('Panels/ui_save_slot_empty_v001.png',false,true);

    const exportPage = await context.newPage();
    exportPage.on('pageerror', error => errors.push(error.message));
    async function isolated(relative, className, markup, width, height, usage, extra='', type='Simple',border=[0,0,0,0]) {
      const w=Math.ceil(width),h=Math.ceil(height);
      await exportPage.setViewportSize({width:w,height:h});
      const normalization=`html,body{margin:0;background:transparent!important}#jianghu-save-preview{padding:0!important}#jianghu-save-preview .save-window{margin:0!important;padding:0!important;width:${w}px!important;max-width:none!important;height:${h}px!important;background:transparent!important;box-shadow:none!important;border:0!important}#jianghu-save-preview .save-window::before{display:none!important}#asset-piece{position:relative!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;inset:auto!important;margin:0!important;transform:none!important;width:${w}px!important;height:${h}px!important;max-width:none!important;min-height:0!important;min-width:0!important;box-shadow:none!important}${extra}`;
      await exportPage.setContent(`<html><head><meta charset="utf-8"><style>${css}\n${normalization}</style></head><body><div id="jianghu-save-preview"><div class="save-window"><div id="asset-piece" class="${className}">${markup}</div></div></div></body></html>`);
      const destination=path.join(assetRoot,relative);fs.mkdirSync(path.dirname(destination),{recursive:true});
      await exportPage.screenshot({path:destination,omitBackground:true});
      await register(relative,w,h,usage,type,border);
    }
    await isolated('Buttons/ui_save_button_primary_v001.png','primary-action','',layout.components.primaryButton.width,layout.components.primaryButton.height,'确认/读取/保存的深绿实心笔触按钮，无文字');
    await isolated('Buttons/ui_save_button_secondary_v001.png','secondary-action','',secondaryRect.width,secondaryRect.height,'取消按钮浅墨底，无文字，与确认同类笔触形状');
    await isolated('Panels/ui_save_detail_paper_v001.png','detail','',layout.components.details.width,layout.components.details.height,'右侧详情纸面与轻描边，无正文；轻微外阴影可由工程组件补充','', 'Sliced',[4,4,4,4]);
    await isolated('Panels/ui_save_confirm_paper_v001.png','confirm-box','',confirmRect.width,confirmRect.height,'二次确认弹窗纸面，无文字','', 'Sliced',[4,4,4,4]);
    await isolated('Icons/ui_save_return_circle_v001.png','save-close','',40,40,'朱笔厚圈，中心X另图；与标题垂直中心对齐');
    await isolated('Icons/ui_save_return_cross_v001.png','save-close','<span class="close-cross"></span>',40,40,'短粗朱色X，与圆圈使用同一画布叠放','#asset-piece::before,#asset-piece::after{display:none!important}');
    await isolated('Decorations/ui_save_tab_underline_v001.png','mode-button','',74,4,'Tab选中状态的笔触下划线','#asset-piece{background:var(--jade)!important;clip-path:polygon(0 51%,9% 19%,30% 5%,47% 19%,72% 0,96% 24%,100% 64%,80% 82%,54% 73%,31% 100%,7% 85%)!important}');
    await isolated('Decorations/ui_save_title_seal_frame_v001.png','title-seal','',15,33,'存卷小印边框；中文字由TMP单独显示，运行时旋转-4度');
    await isolated('Decorations/ui_save_mountains_v001.png','ink-landscape','<div class="ink-mountain"></div><div class="ink-mountain near"></div><div class="ink-horizon"></div>',220,100,'标题旁淡墨山影；其中纸色雾带按当前背景配色保留');

    // Full background exported from its original CSS; no text, buttons, or detail content.
    const w=Math.ceil(layout.referenceWidth),h=Math.ceil(layout.referenceHeight);
    await exportPage.setViewportSize({width:w,height:h});
    await exportPage.setContent(`<html><head><style>${css}html,body{margin:0;background:transparent}#jianghu-save-preview{padding:0}#jianghu-save-preview .save-window{margin:0;width:${w}px;height:${h}px;max-width:none;padding:0;box-shadow:none}</style></head><body><div id="jianghu-save-preview"><div class="save-window"></div></div></body></html>`);
    fs.mkdirSync(path.join(assetRoot,'Backgrounds'),{recursive:true});
    await exportPage.screenshot({path:path.join(assetRoot,'Backgrounds/ui_save_background_v001.png'),omitBackground:true});
    await register('Backgrounds/ui_save_background_v001.png',w,h,'完整菜单宣纸底色、细纹与淡色晕染，无内容；按参考比例缩放');
    await sharp({create:{width:128,height:128,channels:4,background:{r:21,g:34,b:24,alpha:.4}}}).png().toFile(path.join(assetRoot,'Backgrounds/ui_save_modal_scrim_v001.png'));
    await register('Backgrounds/ui_save_modal_scrim_v001.png',64,64,'确认弹窗遮罩，可伸展铺满界面');

    await page.setViewportSize({width:360,height:1200});
    await page.waitForTimeout(50);
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    await page.locator('.save-window').screenshot({path:path.join(packageRoot,'Reference/save-load-narrow.png'),omitBackground:true});
    if(overflow){const offenders=await page.evaluate(()=>[...document.querySelectorAll('*')].filter(element=>element.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(element=>({tag:element.tagName,cls:element.className,right:element.getBoundingClientRect().right,width:element.getBoundingClientRect().width})));throw new Error('360px preview overflows: '+JSON.stringify(offenders));}
    if(errors.length)throw new Error(errors.join('\n'));
    layout.confirmation={width:confirmRect.width,height:confirmRect.height,primaryButton:{width:primaryRect.width,height:primaryRect.height},secondaryButton:{width:secondaryRect.width,height:secondaryRect.height}};
    layout.notes=['All text is separate from production sprites.','Automatic slot appears first; current slot count is a layout example, not approved save-slot requirements.','Do not use these preview interactions as Unity save/load code.'];
    fs.writeFileSync(path.join(packageRoot,'Data/save_load_layout.json'),JSON.stringify(layout,null,2));
    fs.writeFileSync(path.join(assetRoot,'manifest_save_load.json'),JSON.stringify({version:1,approvedPreview:'Source/save-load-approved.html',exportScale:scale,appearance:'light',textBakedIntoImages:false,unityTested:false,assets:records},null,2));
    fs.writeFileSync(path.join(packageRoot,'Data/export_checks.json'),JSON.stringify({assetCount:records.length,syntaxAndRendering:'passed',runtimeErrors:errors,previewInteractions:['slot selection','confirmation cancel','empty-slot preview save','auto-slot manual overwrite disabled'],narrowWidth:360,narrowOverflow:overflow,unityTested:false},null,2));
    const cellW=440,cellH=190,columns=3,rows=Math.ceil(records.length/columns);
    const tiles=[];
    for(let i=0;i<records.length;i++){
      const asset=records[i];
      const thumb=await sharp(path.join(assetRoot,asset.file)).resize({width:cellW-32,height:120,fit:'inside',withoutEnlargement:true}).png().toBuffer();
      const dimensions=await sharp(thumb).metadata();
      const x=(i%columns)*cellW,y=Math.floor(i/columns)*cellH;
      tiles.push({input:thumb,left:x+16,top:y+20});
      const label=Buffer.from(`<svg width="${cellW}" height="44"><text x="16" y="17" font-family="Arial" font-size="12" fill="#344638">${safeText(asset.id)}</text><text x="16" y="35" font-family="Arial" font-size="11" fill="#647063">${asset.width} x ${asset.height} px</text></svg>`);
      tiles.push({input:await sharp(label).png().toBuffer(),left:x,top:y+142});
    }
    await sharp({create:{width:cellW*columns,height:cellH*rows,channels:4,background:'#ebece3'}}).composite(tiles).png().toFile(path.join(packageRoot,'Reference/assets-contact-sheet.png'));
    console.log(JSON.stringify({assets:records.length,reference:[layout.referenceWidth,layout.referenceHeight],returnAlignment:layout.returnTitleCenterDifference,checks:'passed',root:packageRoot}));
  } finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
