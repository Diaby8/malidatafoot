import { chromium } from 'playwright';
const polices=async f=>{const KO=await f.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family+' '+x.weight+' '+x.style)); if(KO.length){console.error('polices non chargées :',KO.join(', '),'→ lancer « npm install » dans visuels/'); process.exit(2);}};
const [,, file, out, ts] = process.argv;
const b = await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined, args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror', e=>console.log('pageerror:', e.message));
await p.goto('file://'+process.cwd()+'/'+file); await p.waitForFunction(()=>window.READY===true, null, {timeout:15000}); await polices(p); await p.waitForTimeout(150);
for (const t of ts.split(',')){ await p.evaluate(x=>window.seek(x), +t); await p.screenshot({path: out.replace('%', t)}); }
await b.close();
