// Rasterize the approved interface's code-native component silhouettes.
// Skin content is rendered from Unity Prefabs and is not exported here.
const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

const root = path.resolve(__dirname, '..');
const sourceRoot = path.resolve(root, '../../SaveLoad/v01/Assets/WuxiaVillage/Art/UI/SaveLoad');
const listContour = '3,5 32,0 98,3 100,50 98,96 61,100 0,94 2,48';
const buttonContour = '2,4 18,0 50,3 97,0 100,48 98,94 69,98 30,95 0,100';
const components = [
  { id:'appearance_item_normal', file:'Panels/ui_appearance_item_normal_v001.png', width:430, height:182, color:'#E8E8DC', contour:listContour, use:'列表条目普通底板，参考215×91 UI单位' },
  { id:'appearance_item_selected', file:'Panels/ui_appearance_item_selected_v001.png', width:430, height:182, color:'#E1E5D9', contour:listContour, use:'当前查看条目底板，与正在使用状态分开绑定' },
  { id:'appearance_item_equipped', file:'Panels/ui_appearance_item_equipped_v001.png', width:430, height:182, color:'#D6E2D2', contour:listContour, use:'实际使用中条目底板' },
  { id:'appearance_apply', file:'Buttons/ui_appearance_apply_v001.png', width:300, height:96, color:'#38584B', contour:buttonContour, use:'应用按钮，参考150×48 UI单位' },
  { id:'appearance_equipped_badge', file:'Decorations/ui_appearance_equipped_badge_v001.png', width:168, height:52, color:'#38584B', contour:'2,3 97,0 100,50 98,97 3,100 0,45', use:'实心绿色使用中标记底板，文字和勾号由组件显示' },
  { id:'appearance_active_tab', file:'Decorations/ui_appearance_active_tab_v001.png', width:168, height:8, color:'#38584B', contour:'0,35 18,0 57,16 100,5 97,75 70,100 28,79 0,100', use:'分类Tab选中笔触' }
];

async function main() {
  for (const component of components) {
    const destination = path.join(root, 'Assets', component.file);
    fs.mkdirSync(path.dirname(destination), { recursive:true });
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${component.width}" height="${component.height}" viewBox="0 0 100 100" preserveAspectRatio="none"><polygon points="${component.contour}" fill="${component.color}"/></svg>`;
    await sharp(Buffer.from(svg)).png().toFile(destination);
  }
  const copies = [
    { id:'appearance_paper', file:'Backgrounds/ui_appearance_paper_v001.png', source:'Backgrounds/ui_save_background_v001.png', use:'复用现有宣纸背景，等比适配窗口' },
    { id:'appearance_detail_paper', file:'Panels/ui_appearance_detail_paper_v001.png', source:'Panels/ui_save_detail_paper_v001.png', use:'可选的预览信息纸面，四边各4源像素九宫格' }
  ];
  for (const component of copies) {
    const destination = path.join(root, 'Assets', component.file);
    fs.mkdirSync(path.dirname(destination), { recursive:true });
    fs.copyFileSync(path.join(sourceRoot, component.source), destination);
  }
  const records = [];
  for (const component of [...components, ...copies]) {
    const imagePath = path.join(root, 'Assets', component.file);
    const metadata = await sharp(imagePath).metadata();
    const stats = await sharp(imagePath).stats();
    records.push({ id:component.id, file:'Assets/'+component.file, width:metadata.width, height:metadata.height, hasAlpha:metadata.hasAlpha, alphaRange:metadata.hasAlpha ? [stats.channels.at(-1).min, stats.channels.at(-1).max] : null, use:component.use });
  }
  fs.mkdirSync(path.join(root, 'Data'), { recursive:true });
  fs.writeFileSync(path.join(root, 'Data/asset-manifest.json'), JSON.stringify({ version:1, unityImported:false, contentPreview:'Unity Prefab instances only', assets:records }, null, 2));
  console.log('Exported '+records.length+' interface component PNGs; no skin preview images');
}
main().catch(error => { console.error(error); process.exit(1); });
