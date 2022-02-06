console.log("Imported Successfully");

var repeater;
var newval = ``;
var roomname = document.querySelector(".subtitle");
console.log(roomname.innerHTML);

function doWork() {
    $.ajax({
        url: '/updater',
        data: roomname.innerHTML,
        type: 'POST',
        dataType: 'json',

        success: function(response){
            $.each(response, function( index, value ) {
                if (index.startsWith('tEXt')){
                    newval += `<div class="msgboxes"> ${value} </div>`;
                }

                else if(index.startsWith('DEL')){
                    newval += `<div class="msgboxes"> ${value} </div>`;
                }

                else {
                    newval += `<div class="msgboxes">
                    <form action="/downloader/?data-status=${value}" method="post">
                        <label class="point">
                            <div class="iamge"></div>
                            <input name="retrieval" class="retrieval" value="${index}" type="submit">${index}
                        </label>
                    </form>
                </div>`;
                }
            });
            document.querySelector(".content").innerHTML = newval;
            newval="";
            console.log(newval);
        },
        error: function(error){
            console.log(error);
        }
    });
    repeater = setTimeout(doWork, 5000);
}

doWork();
