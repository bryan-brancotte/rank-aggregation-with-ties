var plot;

stack_onload(function () {
    plot=scaterplot();
    d3.select("#scatter").call(plot);
    build_scaterplot();
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
            build_scaterplot();
        }
    });
});
function build_scaterplot() {
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{'format': 'json','n':'False','m':'False'},
        url:get_job_results_url(),
        type:"GET",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            plot.data(data)
        }
    });
}