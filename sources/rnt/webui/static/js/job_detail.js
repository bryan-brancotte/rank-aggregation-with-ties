var scatter,
    multiline;

stack_onload(function () {
    scatter=scatter_plot();
    d3.select("#scatter").call(scatter);
//    build_scatter_plot();
    multiline=multiline_plot();
    d3.select("#multiline").call(multiline);
//    build_multiline_plot();
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
            build_scatter_plot();
            build_multiline_plot();
        }
    });
});
function build_scatter_plot() {
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{'format': 'json','n':'False','m':'False'},
        url:get_job_results_url(),
        type:"GET",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            scatter.data(data)
        }
    });
}
function build_multiline_plot() {
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{'format': 'json','m':'False','distance_value':'False'},
        url:get_job_aggregated_results_url(),
        type:"GET",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            multiline.data(data)
        }
    });
}