/* Javascript for UcDockerXBlock. */
function IBMDockerTestXBlock(runtime, element) {

    var createDockerHandlerUrl = runtime.handlerUrl(element, 'create_docker');
    var deleteDockerHandlerUrl = runtime.handlerUrl(element, 'delete_docker');
    
    function create_jsCallback(response) {
        if (response.result == true) {
	    alert("create success")
            window.location.reload(true);
        } else {
	    alert("create failed")
            $('.error-message', element).html('Error: ' + response.message);
        }
    }

    function delete_jsCallback(response) {
        if (response.result == true) {
	    alert("delete success")
            window.location.reload(true);
        } else {
	    alert("delete failed")
            $('.error-message', element).html('Error: ' + response.message);
        }
    }
    
    function resultCallback(response){
        if(response.message){
            console.log("fsfsfsdfsdf"+response.message)
            var ll=response.message.join('<br>');
            console.log(ll)
            $('.result', element).html(ll);
       }
    }

    $('#create_docker_btn', element).click(function(eventObject) {
	alert("creating ...,please wait for about 2 minutes")
	params={
        };
        $.ajax({
            type: "POST",
            url: createDockerHandlerUrl,
	    data: JSON.stringify(params),
            success: create_jsCallback
        });
        $('.error-message', element).html();
    });

    $('#delete_docker_btn', element).click(function(eventObject) {
	alert("deleting ...,please wait for about 2 minutes")
	params={
        };
        $.ajax({
            type: "POST",
            url: deleteDockerHandlerUrl,
	    data: JSON.stringify(params),
            success: delete_jsCallback
        });
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
