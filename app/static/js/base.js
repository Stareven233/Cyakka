let url = new URL(document.URL);

// 导航栏头像处hover时出现的工具栏
function add_tooltip() {
  let box = avatar.getBoundingClientRect();
  tip.style.left = box.left + pageXOffset - avatar.offsetWidth + 'px';
  tip.style.top = box.top + pageYOffset + avatar.offsetHeight + 'px';
}

let avatar = document.getElementById('c-avatar');
let tip = document.getElementById('tooltip');
if(tip && avatar.href.startsWith(`${url.origin}/space/`))
{
  add_tooltip();
  avatar.addEventListener('mouseenter', () => tip.style.display="block");
  avatar.addEventListener('mouseleave', () => tip.style.display="none");
  tip.addEventListener('mouseenter', () => tip.style.display="block");
  tip.addEventListener('mouseleave', () => tip.style.display="none");
}
window.addEventListener('resize', () => add_tooltip());


// 导航栏"大会员"hover时的弹出框
let vip_box = $('#popover-vip');
let is_vip = Number(!!vip_box.data('vip'));
let qr_code = $('<img>').attr('src', `${url.origin}/static/img/Furedorika.png`).width('1rem').height('1rem');
let vip_tip = $('<span></span>').html(['大会员竟可以畅享0种专属内容~', '您的大会员特权有0种正在生效'][is_vip]);
let vip_div = $('<div></div>').append(qr_code, vip_tip);

if(vip_box){
  vip_box.popover({
    trigger: 'hover',
    html: true,
    content: vip_div,
    placement: 'bottom',
  });
}
