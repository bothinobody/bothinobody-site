(function(){
  var r=document.documentElement;
  function setLang(l){r.dataset.lang=l;r.lang=l;var a=document.getElementById('b-es'),b=document.getElementById('b-en');if(a)a.setAttribute('aria-pressed',l==='es');if(b)b.setAttribute('aria-pressed',l==='en');try{localStorage.setItem('bothi-lang',l)}catch(e){}}
  var v=null;try{v=localStorage.getItem('bothi-lang')}catch(e){}setLang(v==='en'?'en':'es');
  document.querySelectorAll('.lang button').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.set)})});
  document.querySelectorAll('[data-u]').forEach(function(el){el.textContent=el.dataset.u.split('').reverse().join('')+'@'+el.dataset.d.split('').reverse().join('')});
  document.querySelectorAll('[data-copy]').forEach(function(btn){btn.addEventListener('click',function(){
    var el=document.getElementById(btn.dataset.copy),txt=el.textContent,orig=btn.innerHTML;
    function ok(){btn.textContent=r.dataset.lang==='en'?'Copied':'Copiada';setTimeout(function(){btn.innerHTML=orig},1600)}
    function sel(){var g=document.createRange();g.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(g)}
    try{navigator.clipboard.writeText(txt).then(ok,sel)}catch(e){sel()}
  })});
})();
