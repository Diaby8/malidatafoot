// Capture plusieurs pages 1080 x 1350 en une seule session. usage : node shotmany.mjs <échelle> a.html:a.png b.html:b.png ...
import { chromium } from 'playwright';
const polices=async f=>{const KO=await f.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family+' '+x.weight+' '+x.style)); if(KO.length){console.error('polices non chargées :',KO.join(', '),'→ lancer « npm install » dans visuels/'); process.exit(2);}};
const [,, s, ...jobs] = process.argv;
const b = await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined, args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:1080,height:1350}, deviceScaleFactor:+s});
p.on('pageerror', e=>console.log('pageerror:', e.message));
for (const j of jobs){ const k=j.indexOf(':'), f=j.slice(0,k), o=j.slice(k+1);  // le chemin de sortie peut contenir « C: » sous Windows
  await p.goto('file://'+process.cwd()+'/'+f); await p.waitForFunction(()=>window.READY===true, null, {timeout:15000}); await polices(p); await p.waitForTimeout(120); await p.screenshot({path:o}); }
await b.close();
