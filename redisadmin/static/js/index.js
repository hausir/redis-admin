function initTree() {
    $('#menu ul').treeview({
        collapsed: true,
        animated: "fast",
        control: "#sidetreecontrol",
        persist: "location"
    })
}

function createMenuNode(data) {
    if (data.length === 0) {
        return data;
    }

    var html = '<ul class="filetree">';
    $.each(data, function (i, d) {
        var text = '';
        if (d['children'].length) {
            text = '<a href="/#!/' + d['id'] + '"><span class="folder" data-root="' + d['id'] + '">' + d['text'] + '</span></a>';
        } else {
            text = '<a href="/#!/' + d['id'] + '" class="key" data-key="' + d['id'] + '">' + d['text'] + '</a>';
        }
        html += "<li>" + text + createMenuNode(d['children']) + "</li>";
    });
    html += '</ul>';
    return html;
}

function editValue(obj) {
    if (!obj.hasClass('edit') && !obj.parents('table').hasClass('info')) {
        var key = obj.parents('table').data('key');
        var type = obj.parents('table').data('type');
        var field = obj.text();
        if (type === 'hash') field = obj.prev().text();
        var del = '';
        if ($.inArray(type, ['hash', 'set', 'zset']) !== -1) {
            del = 'or you can <input type="button" value="Delete it" onclick="deleteFeild(\'' + key + '\', \'' + field + '\');" />';
        }
        var html = ' \
                <form> \
                <input type="hidden" name="k" value="' + key + '" /> \
                <input type="hidden" name="i" value="' + obj.prev().text() + '" /> \
                <input type="hidden" name="f" value="' + obj.text() + '" /> \
                <textarea name="v">' + obj.text() + '</textarea> \
                ' + del + '</form>';
        obj.addClass('edit').html(html);
    }
}

function append(key, type, pos) {
    // pos is used list.
    if (!$('#data-box table tbody tr:last').hasClass('append')) {
        var $tr = $('<tbody><tr class="append"><th></th><td><form></form></td></tr></tbody>');
        var $form = $tr.find('form');
        var $th = $tr.find('th');
        switch (type) {
            case 'string':
                $tr.find('th').remove();
                break;
            case 'list':
                $form.append('<input type="hidden" name="pos" value="' + pos + '" />');
                break;
            case 'hash':
                var field = prompt("Please input a field name by new value:");
                if (field === null || field === '') return
                $form.append('<input type="hidden" name="field" value="' + field + '" />');
                $th.html(field);
                break;
            case 'zset':
                var score = prompt("Please input a score by new member:");
                if (score === null || score === '') return
                $form.append('<input type="hidden" name="score" value="' + score + '" />');
                $th.html('score:' + score);
                break;
            default:
                break;
        }
        $form.append('<input type="hidden" name="key" value="' + key + '" />');
        $form.append('<textarea name="value"></textarea>');
        $('#data-box table tbody').append($tr.html()).find('textarea').focus();
    }
}


$(function () {
    var body = $('body');
    var data_box = $('#data-box');
    var q = $('#search form input[name=q]').val();
    if (q) getMenu(q);
    getInfo();
    $('#nav li a.info').click(function () {
        getInfo();
    });
    $('#nav li a.connection').click(function () {
        $('#connect-list').toggle('fast');
    });
    $('#nav li a.new').click(function () {
        $('#new-box').toggle('fast');
    });
    $('#new-box select').change(function () {
        if ($(this).val() === 'zset') {
            var tr_score = '\
                        <tr class="zset-score">\
                            <th><label for="new-score">Score:</label></th>\
                            <td><input id="new-score" name="score" type="text" /></td>\
                        </tr>';
            $(this).parents('tr').after(tr_score);
        } else {
            var next = $(this).parents('tr').next();
            if (next.hasClass('zset-score')) next.remove();
        }
    });
    $('#search form').submit(function () {
        getMenu($(this).find('input[name=q]').val());
        return false;
    });
    $('#connect-list li a').click(function () {
        var $this = $(this);
        var callback = function () {
            $('#menu').html('');
            $this.parents('ul').find('a').removeClass('current');
            $this.addClass('current');
            $('#nav a.connection').click();
            var q = $('#search form input[name=q]').val();
            if (q) getMenu(q);
        };
        var db = $this.data('db');
        connection(db, callback);
    });
    body.delegate('a.key', 'click', function () {
        getValue($(this).text());
    });
    $('#menu').delegate('li>a>span.folder', 'click', function () {
        getList($(this).data('root'), 1);
    });
    data_box.delegate('td', 'dblclick', function () {
        editValue($(this));
    });
    data_box.delegate('textarea[name=v]', 'keydown', function (event) {
        if (event.ctrlKey && event.keyCode === 13) {
            var form = $(this).parents('form');
            editDone(form);
        }
    });
    data_box.delegate('textarea[name=value]', 'keydown', function (event) {
        if (event.ctrlKey && event.keyCode === 13) {
            var form = $(this).parents('form');
            addValue(form);
        }
    });
    body.delegate('.pagination a', 'click', function () {
        getList($(this).data('root'), $(this).data('page'));
    });
});
