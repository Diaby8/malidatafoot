import { chromium } from 'playwright';
const polices=async f=>{const KO=await f.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family+' '+x.weight+' '+x.style)); if(KO.length){console.error('polices non chargées :',KO.join(', '),'→ lancer « npm install » dans visuels/'); process.exit(2);}};
const [,, file, out, w='1080', h='1350', s='1'] = process.argv;
const b = await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined, args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:+w,height:+h}, deviceScaleFactor:+s});
p.on('pageerror', e=>console.log('pageerror:', e.message));
await p.goto('file://'+process.cwd()+'/'+file); await p.waitForFunction(()=>window.READY===true); await polices(p); await p.waitForTimeout(300); await p.screenshot({path:out});
await b.close();
