console.log("bleep");

var fileInput = document.querySelector(".files");
var switchInput = document.querySelector("#switch");
var Name = document.querySelector("#nameLabel");
var input = document.querySelector("#inputLabel");
var existingFileData = $('#my-data').data();
var formElement = document.querySelector("#mainform");
var message = " will be tracked using the version control software, Please add a description of changes.";

console.log( (existingFileData)["other"] );

$(document).ready(function() {
    Name.style.visibility = "hidden";
    input.style.visibility = "hidden";

    switchInput.addEventListener('change', function(){
        if (this.checked){
            input.setAttribute('required', '');
            
            Name.style.visibility = "Visible";
            input.style.visibility = "Visible";
        }
        else{
            Name.style.visibility = "hidden";
            input.style.visibility = "hidden";

            input.removeAttribute('required', '');
        }
    });

    fileInput.addEventListener('change', function(){
        let allFiles = fileInput.files;
        for (let i=0; i<allFiles.length; i++){
            // if (existingFileData["other"].includes(allFiles[i].name)) {
            let buffer = document.createElement("div");
            buffer.classList.add("buffer");

            let currentLabels = document.createElement("label");
            currentLabels.classList.add("labels2");
            currentLabels.setAttribute("for", allFiles[i].name+"textarea");
            currentLabels.innerHTML = allFiles[i].name + message; 

            let textarea = document.createElement("textarea");
            textarea.classList.add("msg_box");
            textarea.setAttribute("name", allFiles[i].name+"textarea");
            textarea.setAttribute("form", "mainform");
            textarea.setAttribute("value", "Some changes");

            buffer.appendChild(currentLabels);
            buffer.appendChild(textarea);
            document.querySelector(".wrapper").appendChild(buffer);
            //}
        }
        
    });

});

