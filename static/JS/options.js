console.log("bleep");

var fileInput = document.querySelector(".files");
var switchInput = document.querySelector("#switch");
var Name = document.querySelector("#nameLabel");
var checkbox = document.querySelector("#inputLabel");

$(document).ready(function() {
    //Name.style.visibility = "hidden";
    //checkbox.style.visibility = "hidden";
    switchInput.addEventListener('change', function(){
        if (this.checked){
            Name.fadeIn("slow");
            checkbox.fadeIn("slow");
            //Name.style.visibility = "visible";
            //checkbox.style.visibility = "visible";
        }
        else{
            Name.fadeOut("slow");
            checkbox.fadeOut("slow");
            //Name.style.visibility = "hidden";
            //checkbox.style.visibility = "hidden";
        }
    });
});

