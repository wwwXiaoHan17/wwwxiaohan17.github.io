(function(){
'use strict';

const STORAGE_KEY='pyera-docs-lang';
const THEME_KEY='pyera-docs-theme';

/* ===== Language ===== */
function getLang(){return localStorage.getItem(STORAGE_KEY)||'zh';}
function setLang(l){
  localStorage.setItem(STORAGE_KEY,l);
  document.documentElement.lang=l;
  document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active',b.dataset.lang===l));
  document.querySelectorAll('.lang-content').forEach(el=>el.classList.toggle('active',el.dataset.lang===l));
}
document.addEventListener('click',e=>{const b=e.target.closest('.lang-btn');if(b)setLang(b.dataset.lang);});

/* ===== Theme ===== */
function getTheme(){return localStorage.getItem(THEME_KEY)||'dark';}
function setTheme(t){
  localStorage.setItem(THEME_KEY,t);
  document.documentElement.setAttribute('data-theme',t);
  const btn=document.querySelector('.theme-toggle');
  if(btn)btn.textContent=t==='dark'?'☀':'☽';
}
function toggleTheme(){setTheme(getTheme()==='dark'?'light':'dark');}
document.addEventListener('click',e=>{if(e.target.closest('.theme-toggle'))toggleTheme();});

/* ===== Mobile Sidebar ===== */
document.addEventListener('click',e=>{
  const btn=e.target.closest('.mobile-toggle');
  if(btn)document.querySelector('.sidebar').classList.toggle('open');
});
document.addEventListener('click',e=>{
  if(window.innerWidth<=860&&!e.target.closest('.sidebar')&&!e.target.closest('.mobile-toggle')){
    document.querySelector('.sidebar')?.classList.remove('open');
  }
});

/* ===== Copy Code ===== */
document.addEventListener('click',e=>{
  const btn=e.target.closest('.copy-btn');if(!btn)return;
  const code=btn.closest('pre')?.querySelector('code')?.textContent;if(!code)return;
  navigator.clipboard.writeText(code).then(()=>{
    const orig=btn.textContent;btn.textContent='✓';
    setTimeout(()=>btn.textContent=orig,1200);
  });
});

/* ===== Active Nav ===== */
function setActiveNav(){
  const cur=location.pathname.split('/').pop()||'index.html';
  document.querySelectorAll('.nav-link').forEach(l=>{
    l.classList.toggle('active',(l.getAttribute('href')||'').split('/').pop()===cur);
  });
}

/* ===== Smooth Scroll ===== */
document.addEventListener('click',e=>{
  const a=e.target.closest('a[href^="#"]');if(!a)return;
  const t=document.querySelector(a.getAttribute('href'));if(!t)return;
  e.preventDefault();
  const header=document.querySelector('.topbar')?.offsetHeight||52;
  const top=t.getBoundingClientRect().top+window.pageYOffset-header-12;
  window.scrollTo({top,behavior:'smooth'});
  history.pushState(null,'',a.getAttribute('href'));
});

/* ===== Global Search ===== */
let globalIdx=[];
let searchDropdown=null;
let searchInput=null;

async function loadSearchIndex(){
  const embedded=document.getElementById('search-data');
  if(embedded?.textContent?.trim()){
    try{
      const data=JSON.parse(embedded.textContent);
      if(Array.isArray(data)&&data.length){
        globalIdx=data;
        return;
      }
    }catch(e){console.warn('Embedded search index parse failed:',e);}
  }
  try{
    const depth=location.pathname.split('/').length-1;
    const prefix=depth>0?Array(depth).fill('..').join('/')+'/':'';
    const res=await fetch(prefix+'api/search-index.json');
    if(res.ok)globalIdx=await res.json();
  }catch(e){console.error('Search index load failed:',e);}
}

function createDropdown(){
  if(searchDropdown)return;
  const box=document.querySelector('.search-wrapper');if(!box)return;
  searchDropdown=document.createElement('div');
  searchDropdown.className='search-dropdown';
  box.appendChild(searchDropdown);
}

function doSearch(query){
  if(!searchDropdown)createDropdown();
  if(!query.trim()){searchDropdown.classList.remove('active');return;}
  const q=query.toLowerCase().trim();
  const hits=globalIdx.filter(item=>{
    const text=(item.name+' '+(item.module||'')+' '+(item.moduleEn||'')+' '+(item.signature||'')+' '+(item.desc||'')).toLowerCase();
    return text.includes(q);
  }).slice(0,15);

  if(hits.length===0){
    searchDropdown.innerHTML='<div class="search-empty"><strong>未找到结果</strong>试试其他关键词</div>';
  }else{
    searchDropdown.innerHTML=hits.map(h=>{
      const depth=location.pathname.split('/').length-1;
      const prefix=depth>0?Array(depth).fill('..').join('/')+'/':'';
      return `<div class="search-result-item" data-href="${prefix}${h.url}">
        <div class="result-name">${escapeHtml(h.name)}</div>
        <div class="result-module">${escapeHtml(h.module||'')}</div>
        ${h.signature?`<div class="result-signature">${escapeHtml(h.signature)}</div>`:''}
        <div class="result-desc">${escapeHtml(h.desc||'')}</div>
      </div>`;
    }).join('');
  }
  searchDropdown.classList.add('active');
}

function escapeHtml(s){
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function closeDropdown(){searchDropdown?.classList.remove('active');}

/* Search event handlers */
document.addEventListener('input',e=>{
  const input=e.target.closest('.search-input');
  if(input)doSearch(input.value);
});

document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){closeDropdown();searchInput?.blur();}
  if((e.ctrlKey||e.metaKey)&&e.key==='k'){
    e.preventDefault();
    searchInput=document.querySelector('.search-input');
    if(searchInput){searchInput.focus();searchInput.select();}
  }
});

document.addEventListener('click',e=>{
  const item=e.target.closest('.search-result-item');
  if(item){location.href=item.dataset.href;return;}
  if(!e.target.closest('.search-wrapper'))closeDropdown();
});

/* ===== Init ===== */
document.addEventListener('DOMContentLoaded',()=>{
  setTheme(getTheme());
  setLang(getLang());
  setActiveNav();
  loadSearchIndex();
  document.querySelectorAll('.search-input[readonly]').forEach(el=>el.removeAttribute('readonly'));
});
})();
