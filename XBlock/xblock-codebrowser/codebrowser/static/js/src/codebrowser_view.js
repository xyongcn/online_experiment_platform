function CodeBrowserBlock(runtime, element) {
  $(element).find('#generate_btn').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'generate');
    var data = {
      lab: $("#lab", element).val()
    };
    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      window.location.reload(true);
    });
  });

  $(element).find('#edit_btn').bind('click', function() {
    var handlerUrl = runtime.handlerUrl(element, 'edit');
    
    var data = {
      src: parent.document.getElementById("codeview").contentWindow.location.href
    };
    $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
      if (response.result == true) {
      window.location.href = "http://172.16.14.147/courses/Tsinghua/CS101/2015_T1/courseware/65a2e6de0e7f4ec8a261df82683a2fc3/5355e890fdbd457fa7bf7822257d681b/";
     } else {
            $('.error-message', element).html('Error: ' + response.message);
     }
     
    });
  });
}
