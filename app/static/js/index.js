$(document).ready(function () {
    if (url.pathname !== '/')
        return false;

    // header的搜索框
    let search_btn = $('#c-header .search-box .glyphicon-search');
    let search_input = $('#search-input');

    search_btn.click(function() {
        if(search_input.val())
            $.post(url.origin + '/search/history', {keyword: search_input.val()});
        window.open( url.origin +  '/search?' + search_input.serialize());
    });
    search_input.keydown(function (event) {
        if(event.key === 'Enter')
            search_btn.click();
    });

    (function () {
        $('#c-wrapper .spread-module').hover(
        function () {
            $(this).children('p.info').animate({top:'0'}, "20");
        },function () {
            $(this).children('p.info').animate({top:'-0.28rem'}, "20");
        });
    })();

    //各分区视频展示的换一换
    $('#c-wrapper .wrap-module>header .read-push').click(function () {
        let div = $(this).data('div');
        let storey_box = $(`#cya_${div} .storey-box`);

        $.get(`${url.origin}?div=${div}`, function (res, status) {
            if(status !== 'success')
                return false;
            storey_box.html(res);
        })
    });
});
