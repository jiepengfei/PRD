// Re-render the editable SVG controls with sharp. No artwork is altered.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require(process.env.SHARP_MODULE_PATH || 'sharp');
const root = path.resolve(__dirname, '..');
const specs = JSON.parse(fs.readFileSync(path.join(__dirname, 'controls_spec.json'), 'utf8'));
(async () => {
  const dest = path.join(root, 'Assets/WuxiaCardUpgradeUI/Sprites/Controls');
  fs.mkdirSync(dest, {recursive: true});
  for (const entry of specs) {
    await sharp(path.join(__dirname, 'SVG', entry.name + '.svg')).png().toFile(path.join(dest, entry.name + '.png'));
  }
  console.log('Rendered ' + specs.length + ' SVG controls');
})().catch(error => { console.error(error); process.exit(1); });
