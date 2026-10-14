// Capture d'une page animée (window.seek, window.DUREE, window.READY) en vidéo MP4 via ffmpeg.
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs'; import { spawn } from 'child_process';
const [,, page, out, fps='30'] = process.argv;
const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--allow-file-access-from-files','--force-color-profile=srgb']});
const p = await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror', e=>console.log('pageerror:', e.message));
await p.goto('file://'+process.cwd()+'/'+page); await p.waitForFunction(()=>window.READY===true,null,{timeout:60000});
const D = await p.evaluate(()=>window.DUREE); const N = Math.round(D*fps);
const ff = spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium','-movflags','+faststart',out]);
for (let i=0;i<N;i++){ await p.evaluate(t=>window.seek(t), i/fps); const buf = await p.screenshot({type:'jpeg',quality:92}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('ok', N, 'images', D, 's');
