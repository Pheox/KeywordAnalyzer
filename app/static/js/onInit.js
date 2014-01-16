
cookieName="page_scroll"
expdays=365


window.onload = init;
window.onunload = finish;

function init() {
    var kwSelect = document.getElementById("keyword");
    if (kwSelect){
        kwSelect.onchange = handleChangeKw;
    }

    var langSelect = document.getElementById("language");
    if (langSelect){
        langSelect.onchange = handleChangeLang;
    }

    var engineSelect = document.getElementById("search_engine");
    if (engineSelect){
        engineSelect.onchange = handleChangeEngine;
    }

    loadScroll();
}


function finish() {
    saveScroll();
}


/* Handlers */

function handleChangeKw() {
    var form = document.getElementById("frm1");
    form.switch.value = "kw";
    form.submit();
}

function handleChangeLang() {
    var form = document.getElementById("frm1");
    form.switch.value = "lang";
    form.submit();
}

function handleChangeEngine() {
    var form = document.getElementById("frm1");
    form.switch.value = "engine";
    form.submit();
}


/***** JQUERY *****/

/* Highlight selected tab. */
$(function(){

    var $page = window.location.pathname;
    $('#menu ul li a').each(function(){
        var $href = $(this).attr('href');
        if ( ($href == $page) || ($href == '') ||
             ($page == '/' && $href == '/')) {
            $(this).addClass('on');
        } else {
            $(this).removeClass('on');
        }
    });
});



function saveScroll(){ // added function
    console.log("saveScroll");
    var expdate = new Date();
    expdate.setTime (expdate.getTime() + (expdays*24*60*60*1000));

    var x = (document.pageXOffset?document.pageXOffset:document.body.scrollLeft);
    var y = (document.pageYOffset?document.pageYOffset:document.body.scrollTop);
    Data=x + "_" + y;
    setCookie(cookieName,Data,expdate);
}


function loadScroll(){ // added function
    console.log("loadScroll");
    inf = getCookie(cookieName)
    if(!inf){
        console.log("??");
        return;
    }
    var ar = inf.split("_");
    console.log(ar);
    if(ar.length == 2){
        window.scrollTo(parseInt(ar[0]), parseInt(ar[1]));
    }
}
