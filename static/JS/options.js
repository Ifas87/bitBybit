console.log("bleep");

var fileInput = document.querySelector(".filesInput");
var switchInput = document.querySelector("#switch");
var Name = document.querySelector("#nameLabel");
var input = document.querySelector("#inputLabel");
var existingFileData = $('#my-data').data();
var formElement = document.querySelector("#mainform");
var message = " will be tracked using the version control software, Please add a description of changes.";
var fileList = document.querySelector(".allFilelList");

console.log( (existingFileData)["other"] );

$(document).ready(function() {
    Name.style.visibility = "hidden";
    input.style.visibility = "hidden";

    switchInput.addEventListener('change', function(){
        if (this.checked){
            input.setAttribute('required', '');
            
            Name.style.visibility = "Visible";
            input.style.visibility = "Visible";

            document.querySelector(".versionControlLogs").style.visibility = "Hidden";
        }
        else{
            Name.style.visibility = "hidden";
            input.style.visibility = "hidden";

            input.removeAttribute('required', '');
            document.querySelector(".versionControlLogs").style.visibility = "Visible";
        }
    });

    fileInput.addEventListener('change', function(){
        let allFiles = fileInput.files;
        fileList.innerHTML = "";

        for (let i=0; i<allFiles.length; i++){
            fileList.innerHTML += `${allFiles[i].name} <br>`;
        }

        for (let i=0; i<allFiles.length; i++){

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
            document.querySelector(".versionControlLogs").appendChild(buffer);
        }
    });

    formElement.addEventListener('submit', function(event) {
		event.preventDefault();
        console.log(formElement[1])

        let allFiles = fileInput.files;
		var formData = new FormData(formElement);
        /*
        for ( let i=0; i<allFiles.length; i++){
            formData.append("fileList[]", allFiles[i]);
        }
        */

        formData.append("switch", switchInput.checked);
        console.log("In form data: " + switchInput.checked);
        console.log(formData);

		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {

						console.log('Bytes Loaded: ' + e.loaded);
						console.log('Total Size: ' + e.total);
						console.log('Percentage Uploaded: ' + (e.loaded / e.total))

						var percent = Math.round((e.loaded / e.total) * 100);

						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
					}

				});

				return xhr;
			},
			type : 'POST',
			url : '/options',
			data : formData,
			processData : false,
			contentType : false,
			success : function() {
                window.location.href = "/chat";
			}
		});

	});

});

