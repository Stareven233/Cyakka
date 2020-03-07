// 用户信息修改 edit_xxx.html
let username = document.querySelector('#edit-profile #username');
if(username){
    username.setAttribute("disabled", "");
}

// 上传头像 upload_avatar.html
$(document).ready(function () {
    if (url.pathname !== '/edit/avatar')
        return false;

    let up_avatar = document.getElementById('avatar');
    let submit_btn = $('#submit');
    function check_file(target)
    {
        let size = target.files[0].size / 1024;
        if(size > 2000){
            alert('图片应小于2M');
            target.value = ""; //选择的文件路径
        }
        submit_btn.removeAttr('disabled');
    }
    //up_avatar.addEventListener('change', () => fileLimit(this)); 不可，此处this为Window
    up_avatar.setAttribute("onchange", "check_file(this)");
    submit_btn.attr('disabled', '');
});


// 侧边栏导航按钮高亮
$(document).ready(function () {
    if (!url.pathname.startsWith('/back/'))
        return false;
    let aa = $(`#back-nav > a.btn[href^='${url.pathname}']`).addClass('light-on');
});


// 稿件审核 video_audit.html
async function audit_video(row, status)
{
    let form = new FormData();
    form.set('av', row.firstElementChild.innerHTML);
    form.set('status', status);
    let response = await fetch(`${url.origin}/back/audit-video`, {
        method: 'POST',
        body: form
    });
    let result = await response.text();
    if(result === 'success')
        row.remove()
}

let up_items = document.querySelectorAll('#back-body .up-info');
for(let up of up_items) {
    up.lastElementChild.firstElementChild.addEventListener('click', () => audit_video(up, '1'));
    up.lastElementChild.lastElementChild.addEventListener('click', () => audit_video(up, '2'));
    //对应行末审核栏的ok与not
}


// 评论管理 comm_manage.html
async function audit_comment(info, op)
{
    let form = new FormData();
    let row = info.parentElement.parentElement;
    form.set('cid', row.dataset.cid);
    form.set('op', op);
    let response = await fetch(`${url.origin}/back/audit-comment`, {
        method: 'POST',
        body: form
    });
    let result = await response.text();
    if(result === 'finish')
        row.remove()
}
let comm_infos = document.querySelectorAll('#back-body .con .info');
for(let info of comm_infos){
    info.children[1].addEventListener('click', () => audit_comment(info, '1'));
    info.children[2].addEventListener('click', () => audit_comment(info, '0'));
}


// 用户管理 user_manage.html
// 全靠html组件了

// 搜索页面 search.html
$(document).ready(function () {
    if (url.pathname !== '/search')
        return false;
    //  高亮显示当前的搜索条件
    let _default = {type: 'videos', order: 'all', div: 'all', anchor: 'name'};
    for (let i of ['type', 'order', 'div', 'anchor']) {
        url.searchParams.append(i, _default[i]);    //添加默认值
        $(`#${i} input[value=${url.searchParams.get(i)}]`).siblings('label').addClass('light-on');
    }


    function search(kw = null) {
        if (kw)
            $.post(url.origin + '/search/history', {keyword: kw});
        // 但由于下方的页面重新加载，Network中看不到此次请求，调试时将其注释
        window.location = url.origin + '/search?' + $('.search-form').serialize();
    }

    //  搜索框按钮绑定搜索事件 -- 框似乎默认绑定了回车
    let search_input = $('#search-input').keydown(function (event) {
        if (event.key === 'Enter')
            search(search_input.val());
    });
    $('#server-search .label-primary').mouseup(function (event) {
            if (event.which === 1)
                search(search_input.val());
        }
    );
    //  搜索结果条件过滤、排序
    $('.search-form li label').mouseup(function (event) {
        if (event.which === 1) {
            this.click();
            search();
        }
    });

    // 搜索历史框
    let history_box = $('#server-search .search-history').css('display', 'none');
    let base_url = url.origin + '/search?keyword=';

    $.getJSON(`${url.origin}/search/history`, function (res) {
        for (let word of res.history) {
            let anchor = $('<a></a>').attr({href: base_url + word}, {target: '_blank'}).text(word);
            anchor.click(() => $.post(url.origin + '/search/history', {keyword: word}));
            let remove_btn = $('<span></span>').addClass('glyphicon glyphicon-remove');
            remove_btn.click(function () {
                $.ajax({
                    url: `${url.origin}/search/history`,
                    type: 'DELETE',
                    data: {keyword: anchor.text()},
                    success: row.remove()
                });
            });
            let row = $('<li></li>').append(anchor, remove_btn);
            history_box.append(row);
        }
    });

    let input_blur = () => history_box.css('display', 'none');
    let input_focus = () => history_box.css('display', 'block');
    search_input.blur(input_blur).focus(function () {
        search_input.val() ? input_blur() : input_focus();
    });
    search_input.on('input', function () {
        search_input.val() ? input_blur() : input_focus();
    });
    history_box.hover(() => search_input.off('blur', input_blur), () => search_input.on('blur', input_blur));

    function resize_history_box() {
        let size = search_input.offset();
        history_box.css('left', size.left + pageXOffset + 'px')
            .css('top', size.top + pageYOffset + search_input.outerHeight() + 'px');
    }

    resize_history_box();
    window.addEventListener('resize', () => resize_history_box());
});

//用户日志
$(document).ready(function () {
    if (url.pathname !== '/back/log-user')
        return false;
    let log_form = $('.log-form');
    let labels = $('.search-nav #op label');
    let uid_input = $('.search-input #uid');

    uid_input.change(function () {
        if(isNaN(uid_input.val()))
            uid_input.next('p').text('uid应只由数字组成!!')
    }).focus(() => uid_input.next('p').text(''));

    labels.siblings('input:checked').next('label').addClass('light-on');
    labels.mousedown(function (event) {
        if(isNaN(uid_input.val()) || event.which !== 1)
            return false;
        $(this).click();
        // $.get(url.href + '?' + log_form.serialize(), function (data, status) {
        //     console.log(data, status);
        // });
        window.location = url.origin + url.pathname + '?' + log_form.serialize();
    })
});

//管理日志
$(document).ready(function () {
    if (url.pathname !== '/back/log-admin')
        return false;
    let log_form = $('.log-form');
    let labels = $('.search-nav #op label');

    labels.siblings(`input[value=${url.searchParams.get('op')}]`).next('label').addClass('light-on');
    labels.mousedown(function (event) {
        if(event.which !== 1)
            return false;
        $(this).click();
        window.location = url.origin + '/back/log-admin?' + log_form.serialize();
    })
});

//用户个人空间
$(document).ready(function () {
    if (!url.pathname.startsWith('/space/'))
        return false;

    function async_update(e)
    {
        e.preventDefault();
        $.get($(e.target).closest('a').attr('href'), function (response, status, xhr) {
            if (status !== 'success')
                return false;
            $('.user-box .u-shows').html(response);
        });
    }
    $('.user-box').on('click', '.u-nav>a:not(:first), .u-shows ul.pagination>li>a', (e) => async_update(e));

    let light_now = $('.user-box .u-nav > a.home').addClass('light-on');
    $('.user-box .u-nav>a').on('click', function () {
        light_now.removeClass('light-on');
        light_now = $(this).addClass('light-on');
    });
});
