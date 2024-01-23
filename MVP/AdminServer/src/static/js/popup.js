const POPUP = document.getElementById("sliding-popup");

function slide(elem){
    elem.style.right = "2%";
}

function disapear(elem){
    elem.style.top = "-200px";
}

if(POPUP){
    setTimeout(function(){slide(POPUP)}, 500);
    setTimeout(function(){disapear(POPUP)}, 4000);
}