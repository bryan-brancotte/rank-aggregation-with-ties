function stack_onload(f) {
    var old = window.onload;
    if (typeof window.onload != 'function')
        window.onload = f;
    else
        window.onload = function() {
            if (old)
                old()
            f();
        }
}
//https://www.w3schools.com/js/js_cookies.asp
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

//https://www.w3schools.com/js/js_cookies.asp
function getCookie(cname, default_value) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    if (typeof default_value != "undefined")
        return default_value;
    return "";
}

//https://www.w3schools.com/js/js_cookies.asp
function checkCookie() {
    var user = getCookie("username");
    if (user != "") {
        alert("Welcome again " + user);
    } else {
        user = prompt("Please enter your name:", "");
        if (user != "" && user != null) {
            setCookie("username", user, 365);
        }
    }
}

function fade_border_to_and_back(target,color, color_org){
    if (typeof color_org == "undefined")
        color_org = $(target).css("border-color");
    $(target)
    .animate({borderColor: color}, 200 )
    .animate({borderColor: color_org}, 900 );
}

function fade_background_to_and_back(target,color, color_org){
    if (typeof color_org == "undefined")
        color_org = $(target).css("background-color");
    $(target)
    .animate({backgroundColor: color}, 200 )
    .animate({backgroundColor: color_org}, 900 );
}

$.fn.attrThatBeginWith = function(begins){
    return [].slice.call(this.get(0).attributes).filter(function(attr) {
        return attr && attr.name && attr.name.indexOf(begins) === 0
    });
};

function format_uuid(data){
    return data.substring(0,8) +
    data.substring(8,12) + '-' +
    data.substring(12,16) + '-' +
    data.substring(16,20) + '-' +
    data.substring(20);
}

function short_uuid(data, reduced){
    return '<span title="'+format_uuid(data,false)+'">'+data.substring(0,8) +'</span>';
}