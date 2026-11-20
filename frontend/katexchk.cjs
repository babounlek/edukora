const katex=require('katex');const fs=require('fs');
const files=fs.readFileSync('C:/Users/ADMINI~1/AppData/Local/Temp/f.txt','utf8').split(/\r?\n/).filter(Boolean);
for(const f of files){const j=JSON.parse(fs.readFileSync('D:/edukora/backend/ingest/'+f,'utf8'));
 for(const q of j)for(const k of ['enonce_markdown','corrige_markdown','choix']){const arr=k==='choix'?(q.choix||[]).map(c=>c.texte):[q[k]||''];
  for(const t of arr){const s=t.replace(/\$\$/g,'$');
   for(const m of s.matchAll(/(?<!\\)\$((?:[^$\\]|\\.)*)(?<!\\)\$/g)){try{katex.renderToString(m[1],{throwOnError:true})}catch(e){console.log(f.split('/').pop(),q.external_id,k,JSON.stringify(s.slice(Math.max(0,m.index-30),m.index+m[0].length+30)))}}}}}
