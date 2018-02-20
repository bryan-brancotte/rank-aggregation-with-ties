$.ajax({
    headers: {
        'X-CSRFToken':getCookie('csrftoken'),
    },
    url:'http://0.0.0.0:8030/jobs/zApsqTzOH0Z041Tn2Qo8zji3EnRJsSsg/',
    type:"GET",
    contentType: "application/json;charset=utf-8",
    success: function (data, textStatus, xhr) {
        console.log("ee");
    }
});