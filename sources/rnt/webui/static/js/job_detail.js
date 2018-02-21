stack_onload(function () {
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{
            status: 2
        },
        url:get_api_job_url(),
        type:"PATCH",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            console.log("ee");
        }
    });
});