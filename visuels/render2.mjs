// Rendu de la vidéo à plusieurs pages : la page maître donne, pour chaque instant, le temps local de chaque scène.
// usage : node render2.mjs <première image> <dernière exclue> <images/s> <dossier> [liste de temps en secondes pour un contrôle]
import { chromium } from 'playwright';
const polices=async f=>{const KO=await f.evaluate(()=>[...document.fonts].filter(x=>x.status==='error').map(x=>x.family+' '+x.weight+' '+x.style)); if(KO.length){console.error('polices non chargées :',KO.join(', '),'→ lancer « npm install » dans visuels/'); process.exit(2);}};
import fs from 'fs';
const [,, start, end, fps='60', dir='frames2', only=''] = process.argv;
fs.mkdirSync(dir,{recursive:true});
const b = await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined, args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror', e=>console.log('pageerror:', e.message));
await p.goto('file://'+process.cwd()+'/md2.html');
const fr = n => p.frames().find(f=>f.url().includes(n));
for (const n of ['md2.html','vitv.html','fiche_anim.html','duel_anim.html']) { await fr(n).waitForFunction(()=>window.READY===true, null, {timeout:20000}); await polices(fr(n)); }
await p.waitForTimeout(200);
const F={old:fr('vitv.html'), fi:fr('fiche_anim.html'), du:fr('duel_anim.html')};
const at = async T => { const loc = await p.evaluate(x=>window.seek(x), T); for (const k of ['old','fi','du']) await F[k].evaluate(x=>window.seek(x), loc[k]); };
const t0=Date.now();
if (only){ for (const s of only.split(',')){ await at(+s); await p.screenshot({path:`${dir}/c_${s}.png`}); } }
else for (let f=+start; f<+end; f++){ await at(f/+fps); await p.screenshot({path:`${dir}/f_${String(f).padStart(5,'0')}.jpg`, type:'jpeg', quality:96}); }
console.log('done', start, end, ((Date.now()-t0)/1000).toFixed(1)+'s');
await b.close();
