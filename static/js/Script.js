// JavaScript source code

function format_date(date) {
    var h = date.getHours();
    var m = date.getMinutes();
    var ampm = h >= 12 ? 'PM' : 'AM';
    h %= 12;
    h = h ? h : 12;
    m = m < 10 ? '0' + m : m;
    var str = h + ':' + m + ' ' + ampm;
    return str;
}

function insert_chat(who, text) {
    var msg = "";
    var date = format_date(new Date());

    if (who == "user") {
        msg = '<li class="me animate-right">' +
            '<p>' + text + '</p>' +
            '<div class="dv1" />' +
            '<p><small class="fl">' + date + '</small></p>'
    }
    else {
        msg = '<li class="him animate-left">' +
            '<p>' + text + '</p>' +
            '<div class="dv2" />' +
            '<p><small class="fr">' + date + '</small></p>'
    }
    $("#msg-ul").append(msg).scrollTop($("ul").prop('scrollHeight'));
}

$("textarea").on("keydown", function (e) {
    if (e.which == 13) {
        var txt = $(this).val().trim();
        if (txt != "") {
            insert_chat("user", txt);
            $(this).val('');
            send_req(txt);
        }
        e.preventDefault();
    }
});

$("#send").on("click", function () {
    var t = $("textarea")[0];
    var txt = $(t).val().trim();
    if (txt != "") {
        insert_chat("user", txt);
        $(t).val('');
        send_req(txt);
    }
});

function send_req(qst) {
    $.ajax({
        type: "POST",
        url: "/receiver",
        data: JSON.stringify(qst),
        dataType: 'json',
        contentType: 'application/json;charset=UTF-16',
        success: function (res) { recieve_res(res); }
    });
}

function recieve_res(res) {
    var msg = res[0];
    var imgs_ids = res[1];
    if (msg === " # ") {
        msg = "أرقام القطع التي قمت بحجزها: ";
        reserved.forEach(function (i) {
            msg += i + "   ";
        });
    }
    if (male == false) {
        if (msg.indexOf("تفضل") != -1) {
            msg = msg.replace("تفضل", "تفضلي");
        }
        if (msg.indexOf("تكرم") != -1) {
            msg = msg.replace("تكرم", "تكرمي");
        }
        if (msg.indexOf("اعد") != -1) {
            msg = msg.replace("اعد", "اعيدي");
        }
    }
    insert_chat('him', msg);
    if (imgs_ids.length != 0) {
        add_imgs(imgs_ids);
        setTimeout(function () { $(".store-imgs").fadeIn() }, 800);
    }
}

$(".about").on("click", function () {
    var modal = document.getElementById('myModal1');

    modal.style.display = "block";

    $("#close2").on("click", function () {
        modal.style.display = "none";
    });
});

function add_imgs(ids) {
    setTimeout(function () { $(".store-imgs").fadeOut() }, 0);
    setTimeout(function () { $(".store-imgs").html("") }, 500);
    setTimeout(function () {
        for (var i = 0; i < ids.length; i++) {
            var im = '<div id="i' + ids[i] + '" class="img-cont">' +
                '<span class=\"img-id\">' + ids[i] + '</span>' +
                '<img src="/static/images/' + ids[i] + '.jpg" />' +
                '<div class="btns">' + '<button id="rbi' + ids[i] + '" class="btn">حجز</button>' +
                '<button id="ubi' + ids[i] + '" class="btn">إلغاء حجز</button>' + '</div></div>';
            $(".store-imgs").append(im);
        }
    }, 550);
    setTimeout(function () {
        for (var i = 0; i < ids.length; i++) {
            add_func(ids[i]);
        }
        $(".store-imgs div img").on("click", function () {
            var modal = document.getElementById('myModal');

            var modalImg = document.getElementById("img01");
            modal.style.display = "block";
            modalImg.src = this.src;

            $("#close1").on("click", function () {
                modal.style.display = "none";
            });
        });
    }, 650);
}

function add_func(i) {
    $("#rbi" + i).click(function () {
        $("#i" + i).css("opacity", 0.5);
        var tmp = reserved.indexOf(i);
        if (tmp == -1) {
            reserved.splice(0, 0, i);
            insert_chat("him", "تم حجز القطعة " + i + " باسم " + uname + ". شكرا لك");
            console.log(reserved);
        }
    });
    $("#ubi" + i).click(function () {
        $("#i" + i).css("opacity", 1);
        var tmp = reserved.indexOf(i);
        if (tmp != -1) {
            reserved.splice(tmp, 1);
            insert_chat("him", "تم إلغاء حجز القطعة " + i + " المحجوزة باسم " + uname);
            console.log(reserved);
        }
    });
    var tmp = reserved.indexOf(i);
    if (tmp != -1) {
        $("#i" + i).css("opacity", 0.5);
    }
}

function log_in() {
    var tmp_nm = $("#nm").val();
    if (tmp_nm == "") {
        alert("الرجاء إدخال الاسم");
        return;
    }
    uname = tmp_nm;
    insert_chat("bot", "أهلاً بكم في متجرنا..");
    $("#login").fadeOut();
}

var male = true;
var uname = "";
var reserved = [];

function genChoose(tmp) {
    male = tmp;
    console.log(male);
}

$(document).ready(function () {
    document.getElementById("login").style.display = "block";
    setTimeout(() => {
        document.getElementById("ld").style.display = "none";
        document.getElementById("nm").focus();
    }, 2000);
});

