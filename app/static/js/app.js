if ('serviceWorker' in navigator) window.addEventListener('load',()=>navigator.serviceWorker.register('/static/sw.js'));
document.querySelectorAll('[data-toast]').forEach((toast)=>setTimeout(()=>toast.remove(),2500));
const toggle=document.getElementById('theme-toggle');
if(toggle){const apply=()=>document.documentElement.classList.toggle('dark-mode',localStorage.getItem('guestflow-dark')==='1');apply();toggle.addEventListener('click',()=>{localStorage.setItem('guestflow-dark',document.documentElement.classList.contains('dark-mode')?'0':'1');apply();});}
