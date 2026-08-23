/*
 * Interactive behaviour for the cost tables on the Cost Tables page:
 * the expand/collapse toggles and the server-generation switcher.
 *
 * Previously this was inlined at the bottom of tips.html and copied into
 * all seven translations; it is identical in every language, so it now
 * lives here and is loaded as a normal script.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Collapse buttons
  document.querySelectorAll('.th-section').forEach(function(section){
    section.querySelectorAll('.th-tablecard').forEach(function(card,idx){
      const btn=card.querySelector('.th-collapse'), body=card.querySelector('.th-tablebody');
      const open=idx===0; body.hidden=!open?true:false; btn.textContent=open?'-':'+'; btn.setAttribute('aria-expanded', open?'true':'false');
      btn.addEventListener('click',function(){ const exp=btn.getAttribute('aria-expanded')==='true'; body.hidden=exp; btn.setAttribute('aria-expanded',exp?'false':'true'); btn.textContent=exp?'+':'-'; });
    });
  });

  // Tabs
  document.querySelectorAll('.th-tabs').forEach(function(tabs){
    const section=tabs.closest('.th-section');
    const btns=tabs.querySelectorAll('.th-tab');
    const wraps=section.querySelectorAll('.th-subtables .th-wrap');
    function show(id){
      wraps.forEach(w=>w.classList.toggle('th-visible', w.id===('wrap-'+id)));
      btns.forEach(b=>b.classList.toggle('th-active', b.getAttribute('data-target')===id));
      wraps.forEach(function(w){
        const visible=w.classList.contains('th-visible');
        const cards=w.querySelectorAll('.th-tablecard');
        cards.forEach(function(card,idx){
          const btn=card.querySelector('.th-collapse'), body=card.querySelector('.th-tablebody');
          if(visible){ const open=idx===0; body.hidden=!open; btn.textContent=open?'-':'+'; btn.setAttribute('aria-expanded',open?'true':'false'); }
          else { body.hidden=true; btn.textContent='+'; btn.setAttribute('aria-expanded','false'); }
        });
      });
    }
    btns.forEach(btn=>btn.addEventListener('click',()=>show(btn.getAttribute('data-target'))));
  });

  // Castle switcher
  (function(){
    const sel=document.getElementById('castle-switch');
    const base=document.getElementById('wrap-castle-base'), w108=document.getElementById('wrap-castle-108'), w1107=document.getElementById('wrap-castle-1107'), wold=document.getElementById('wrap-castle-older');
    function setState(v){
      [base,w108,w1107,wold].forEach(el=>el.classList.remove('th-visible'));
      if(v==='108'){ base.classList.add('th-visible'); w108.classList.add('th-visible'); }
      else if(v==='1107'){ base.classList.add('th-visible'); w1107.classList.add('th-visible'); }
      else { wold.classList.add('th-visible'); }
      [base,w108,w1107,wold].forEach(function(wrap){
        if(!wrap.classList.contains('th-visible')) return;
        wrap.querySelectorAll('.th-tablecard').forEach(function(card,idx){
          const btn=card.querySelector('.th-collapse'), body=card.querySelector('.th-tablebody');
          const open=idx===0; body.hidden=!open; btn.textContent=open?'-':'+'; btn.setAttribute('aria-expanded',open?'true':'false');
        });
      });
    }
    setState(sel.value); sel.addEventListener('change', function(){ setState(this.value); });
  })();
});
