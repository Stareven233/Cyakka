// 登录页面 login.html
$(document).ready(function () {
    if (url.pathname !== '/auth/login')
        return false;

    $('#submit').after($('#login'));
    let login_form = $('.login-box .form');
    login_form.attr('autocomplete', 'off');

    login_form.submit(async function (event) {
        event.preventDefault();
        let form = new FormData(this);
        $.getScript('http://pv.sohu.com/cityjson?ie=utf-8', function () {
            form.set('ip', returnCitySN["cip"] + ' '+ returnCitySN["cname"]);
            $.ajax({
              url: url.href,
              type: "POST",
              data: form,
              processData: false,  // 不处理数据
              contentType: false,   // 不设置内容类型
              success: (doc) => {
                  if(doc.startsWith('/'))
                      window.location = doc;
                  document.querySelector('html').innerHTML = doc;
              }//不允许$('html').html(doc)
            });
        });
    });
});

// 注册页面
$(document).ready(function () {
    if (url.pathname !== '/auth/register')
        return false;
    $('.form').attr('autocomplete', 'off');
});
