// Version Twitter/X (1080 x 1350) d'une scène du gabarit vertical « style vidéo » : même mise en scène,
// réduite d'un cran et recentrée, sans la bande réservée aux boutons TikTok.
// usage : node stillx.mjs vitv.html <temps en secondes> <sortie.png> [échelle de rendu]
import { chromium } from 'playwright';
const polices=async f=>{const KO=await f.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family+' '+x.weight+' '+x.style)); if(KO.length){console.error('polices non chargées :',KO.join(', '),'→ lancer « npm install » dans visuels/'); process.exit(2);}};
const [,, file, t, out, dsf='2'] = process.argv;
const S=.915, Y0=128, W=Math.round(1080/S), DX=Math.round((W-1080)/2);
const b = await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined, args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:1080,height:1350}, deviceScaleFactor:+dsf});
p.on('pageerror', e=>console.log('pageerror:', e.message));
await p.goto('file://'+process.cwd()+'/'+file); await p.waitForFunction(()=>window.READY===true, null, {timeout:15000}); await polices(p);
await p.addStyleTag({content:`html,body{width:1080px!important;height:1350px!important;background:#F6C41C!important}
#stage{width:${W}px!important;transform:scale(${S});transform-origin:0 0;position:absolute!important;left:0;top:${-Y0*S}px}
.sc{left:${DX}px!important;right:${-DX}px!important}
#foot{left:${64+DX}px!important;width:952px!important}#src{left:${64+DX}px!important}
.dots{left:-10px!important;width:${W+20}px!important}`});
await p.evaluate(x=>window.seek(x), +t); await p.waitForTimeout(200); await p.screenshot({path: out});
await b.close();
