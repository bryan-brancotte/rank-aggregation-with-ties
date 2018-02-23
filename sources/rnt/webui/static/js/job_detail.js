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
            refresh_progression();
            build_scatter_plot("#scatter");
            build_multiline_plot("#multiline-n-duration","n","duration");
            build_multiline_plot("#multiline-m-duration","m","duration");
        }
    });
    $("#job_name").keyup(delayed_save_name());
    $("#job_name").keyup(
        function(){
            $(".job_name").text($("#job_name").val());
        }
    );
    refresh_progression();
});

function refresh_progression(){
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{},
        url:get_api_job_progress_url(),
        type:"GET",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            if(data.todo > 0)
                $("#progress-host").show();
            var refresh = parseInt($(".progress.job").attr("data-refresh"));
            console.log(refresh);
            var todo = Math.round(data.todo/data.total*100);
            var error = Math.round(data.error/data.total*100);
            var running = Math.round(data.running/data.total*100);
            var done = 100 - todo - error - running;
            $(".progress.job .todo").css("width",todo+"%");
            $(".progress.job .error").css("width",error+"%");
            $(".progress.job .running").css("width",running+"%");
            $(".progress.job .done").css("width",done+"%");
            refresh = Math.min(refresh*2,5000);
            $(".progress.job").attr("data-refresh", refresh);
            if (todo>0){
                setTimeout(refresh_progression,refresh);
            }
        }
    });
    $("#job_name").keyup(delayed_save_name());
    $("#job_name").keyup(
        function(){
            $(".job_name").text($("#job_name").val());
        }
    );
}

function delayed_save_name(){
    return delayed_action(
        function(){
            $("#job_name").attr("disabled",true);
            $.ajax({
                headers: {
                    'X-CSRFToken':getCookie('csrftoken'),
                },
                data:{
                    name: $("#job_name").val()
                },
                url:get_api_job_url(),
                type:"PATCH",
                dataType:'json',
                success: function (data, textStatus, xhr) {
                    $("#job_name").attr("disabled",false);
                },
                error: function (data, textStatus, xhr) {
                    $("#job_name").attr("disabled",false);
                }
            });
        },
        function (){
        }
    )
}

function build_scatter_plot(target) {
    var plot=reusabled_plot()
        .is_scatterplot(true)
        .y_scale_is_log(true)
        .y_scale_is_duration(true)
        .data_filter(function(d){return d.duration>0})
        .data_identifier(function(d){return d.algo.id+"-"+d.dataset})
        .x_accessor(function(d){return d.distance_value})
        .y_accessor(function(d){return d.duration})
        .x_label("Distance")
        .y_label("Computation time")
        .series_accessor(function(d){return d.algo.key_name})
        .tooltip_builder(function(d){
            return '<table class="table table-condensed" style="margin-bottom:0px;"><tbody>'+
                '<tr><th>distance</th><td>'+plot.x_accessor()(d)+'</td></tr>'+
                '<tr><th>duration</th><td>'+plot.y_ticks_formatter()(plot.y_accessor()(d))+'</td></tr>'+
                '<tr><th>algo</th><td>'+plot.series_accessor()(d)+'</td></tr>'+
                '<tr><th>dataset</th><td>'+
                    '<a href="'+get_dataset_url(d.dataset)+'" target="_blank">'+
                        d.dataset+
                        '&nbsp;<i class="glyphicon glyphicon-new-window"></i>'+
                    '</a>'+
                '</td></tr>'+
                '</tbody></table>';
        })
    ;
    d3.select(target).call(plot);
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

function build_multiline_plot(target, abscissa, ordinate) {
    var plot=reusabled_plot()
        .data_filter(function(d){return d.count>0})
        .data_identifier(function(d){return d.algo.id+"-"+d.dataset})
        .x_accessor(function(d){return d[abscissa]})
        .y_accessor(function(d){return d.mean})
        .y_scale_is_duration(true)
        .x_label("n: #elements")
        .y_label("Computation time")
        .series_accessor(function(d){return d.algo})
        .tooltip_builder(function(d){
            return "<table class='table table-condensed' style='margin-bottom:0px;'><tbody>"+
                "<tr><th>#elt</th><td>"+plot.x_accessor()(d)+"</td></tr>"+
                "<tr><th>algo</th><td>"+plot.series_accessor()(d)+"</td></tr>"+
                "<tr><th>mean</th><td>"+plot.y_ticks_formatter()(d["mean"])+"</td></tr>"+
                "<tr><th>std</th><td>"+plot.y_ticks_formatter()(d["std"])+"</td></tr>"+
                "<tr><th>min</th><td>"+plot.y_ticks_formatter()(d["mean"])+"</td></tr>"+
                "<tr><th>25%</th><td>"+plot.y_ticks_formatter()(d["25%"])+"</td></tr>"+
                "<tr><th>50%</th><td>"+plot.y_ticks_formatter()(d["50%"])+"</td></tr>"+
                "<tr><th>75%</th><td>"+plot.y_ticks_formatter()(d["75%"])+"</td></tr>"+
                "<tr><th>max</th><td>"+plot.y_ticks_formatter()(d["max"])+"</td></tr>"+
                "<tr><th>count</th><td>"+d["count"]+"</td></tr>"+
                "</tbody></table>";
        })
        ;
    d3.select(target).call(plot);
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        data:{
            'format': 'json',
            'm':abscissa==="m",
            'n':abscissa==="n",
            'distance_value':ordinate==="distance_value",
            'duration':ordinate==="duration",
        },
        url:get_job_aggregated_results_url(),
        type:"GET",
        dataType:'json',
        success: function (data, textStatus, xhr) {
            plot.data(data)
        }
    });
}