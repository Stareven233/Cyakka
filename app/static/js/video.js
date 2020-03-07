// 我的投稿 - 编辑与删除视频 video/manage.html
async function del_video(edit)
{
    if(!confirm('确定要删除该视频吗'))
        return false;
    let row = edit.parentElement.parentElement;
    let response = await fetch(`${url.origin}/video/manage`, {
        method: 'POST',
        body: row.dataset.av  //av号
    });
    let result = await response.text();
    if(result === 'success')
        row.remove()
}
//  删除按钮
let edits = document.querySelectorAll('.vd-list .v-edit');
for(let edit of edits) {
    edit.lastElementChild.addEventListener('click', () => del_video(edit));
}

//  编辑按钮
$(document).ready(function () {
    if (url.pathname !== '/video/manage')
        return false;
    let edit_modal = $('#edit-modal');
    let selected_li = undefined;

    edit_modal.on('show.bs.modal', function(event) {
        selected_li = $(event.relatedTarget).parents('li');
        edit_modal.find('#title').val(selected_li.find('a.title').text());
        edit_modal.find('#desc').val(selected_li.find('div.v-desc').text());
        edit_modal.find('#type').val(selected_li.data('div'));
    });

    $('.modal-footer .btn-primary').click(() => edit_modal.find('#submit').click());

    edit_modal.find('.modal-body .form').submit(async (e) => {
            e.preventDefault();
            let form = new FormData(document.querySelector('.modal-body .form'));
            form.append('av', selected_li.data('av'));
            let response = await fetch(`${url.origin}/video/reload`, {
                method: 'POST',
                body: form
            });
            let result = await response.text();
            if(result === 'success')
                window.location = url.href
        })
    }
);


// 视频播放 play.html
$(document).ready(function () {
    if (!url.pathname.startsWith('/video/av'))
        return false;
    // 播放器初始化 play.html
    let video_zone = document.getElementById('dplayer');

    let danmaku_setting = {
            // id: md5(video_zone.dataset.id + video_zone.dataset.file),
            // api: 'https://dplayer.moerats.com/',
            id: video_zone.dataset.id,
            api: `${url.origin}/api/danmaku`,
            // token: 'aka-c_ya_kk!#ak]aw^,su=gi-$',
            // maximum: 1000,
            // addition: ['https://api.prprpr.me/dplayer/v3/bilibili?aid=4157142'],
            user: video_zone.dataset.user,
            bottom: '15%',
            // unlimited: true,
        };

    const dp = new DPlayer({
    container: video_zone,
    theme: '#b46b6d',
    hotkey: true,
    screenshot: true,
    video: {
        url: '../../static/videos/' + video_zone.dataset.file,
        pic: '../../static/video_faces/' + video_zone.dataset.face,
    },
    contextmenu: [
        {
            text: '关灯',
            click: () => {},
        },
        {
            text: '播放器',
            click: (player) => {
                console.log(player);
            },
        }],
    highlight: [
        {
            time: 20,
            text: '这是第 20 秒',
        },
        {
            time: 60,
            text: '这是 1 分钟',
        },
    ],
    danmaku: video_zone.dataset.user ? danmaku_setting: null,
});


    // 视频简介及展开 play.html
    let desc_box = document.querySelector('#v-desc .desc');
    let desc_more = document.querySelector('#v-desc .btn-more');
    desc_more.addEventListener('click', function () {
        // desc_box.classList.contains('open')? desc_box.classList.remove('open'): desc_box.classList.add('open')
        if(desc_box.classList.contains('open')){
            desc_box.classList.remove('open');
            desc_more.innerHTML = "展开更多";
        }
        else{
            desc_box.classList.add('open');
            desc_more.innerHTML = "收起";
        }
    });

    // 发布评论 play.html
    async function post_comment()
    {
        let comm_area = document.querySelector('#v-comment .comm-input');
        if(!comm_area.value || comm_area.value.length>150)
            return false;
        let response = await fetch(`${url.origin}/video/comment?av=` + video_zone.dataset.id, {
            method: 'POST',
            body: comm_area.value
        });
        let result = await response.text();
        if(result === 'success')
            comm_area.value = "";
    }

    let comm_btn = document.querySelector('#v-comment .comm-submit');
    comm_btn.addEventListener('click', () => post_comment());

    // 评论举报功能 play.html
    async function tip_comment(tip_btn)
    {
        let comm = tip_btn.parentElement.parentElement.parentElement;
        // console.log(comm, comm.dataset.cid);
        let response = await fetch(`${url.origin}/video/comment/tip`, {
            method: 'POST',
            body: comm.dataset.cid
        });
        let result = await response.text();
        if(result === 'success')
            alert('举报成功，请耐心等待处理结果');
    }
    let comm_tip_btn = document.querySelectorAll('#v-comment .comm-item .tip-off');
    for(let btn of comm_tip_btn) {
        btn.addEventListener('click', () => tip_comment(btn));
    }


    // 点赞投币收藏 play.html
    async function get_statistic(action)
    {
        let response = await fetch(`${url.origin}/video/is_${action}?av=${video_zone.dataset.id}`);
        return await response.text();
    }
    //  遍历，若当前用户已经点过则点亮对应图标
    (async function() {
        let statistics = document.querySelectorAll('#v-toolbar .ops>span');
        for(let s of statistics)
        {
            if(await get_statistic(s.className) === 'None') // async函数必定返回promise
                continue;
            // console.log(!sta, !!sta, s.className);
            s.classList.add('on');
        }
    })();

    //  向服务器提交点赞、收藏、硬币
    async function post_statistic(action, btn)
    {
        let form = new FormData();
        let light_on = (await get_statistic(action) !== 'None');  //点赞等是否点亮
        if(action === 'coin' && light_on)  //投币后不可再取消
            return false;

        form.set(action, light_on.toString());
        form.set('av', video_zone.dataset.id);
        let response = await fetch(`${url.origin}/video/ops_${action}`, {
            method: 'POST',
            body: form
        });
        if(response.redirected) {
            window.location = response.url.slice(0, response.url.lastIndexOf('?next=')+6) + `/video/av${video_zone.dataset.id}`;
            return false;
        }

        let result = await response.text();
        if (result !== 'success')
            return false;
        light_on ? btn.classList.remove('on') : btn.classList.add('on');
        let light_num = Number(btn.lastElementChild.innerHTML);
        if(isNaN(light_num)) //NaN说明数大于1万，格式不同，正好就不处理
            return ;
        light_num += light_on ? -1 : 1;
        btn.lastElementChild.innerHTML = light_num.toString();
        console.log(light_num);
    }

    let like_btn = document.querySelector('#v-toolbar .like');
    let collect_btn = document.querySelector('#v-toolbar .collect');
    let coin_btn = document.querySelector('#v-toolbar .coin');
    like_btn.addEventListener('click', () => post_statistic('like', like_btn));
    collect_btn.addEventListener('click', () => post_statistic('collect', collect_btn));
    coin_btn.addEventListener('click', () => post_statistic('coin', coin_btn));
});
