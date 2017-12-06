function refresh_settings_from_datasets(form, callback){
    form=$(form);
    $("#updating-stats-indicator").show();
    $("#future-update-indicator").hide();
    $("#btn-compute").attr("disabled",true);
    $("#id_dataset").prop("readonly",true) ;
    $.ajax({
        type: form.attr('method'),
        url:form.attr('data-check-url'),
        data: form.serialize(),
        success: function (data, textStatus, xhr) {
            console.log(data);
            $("#id_dataset+.help-block").html(data["dataset_html_errors"]);
            if(data["dataset_html_errors"]!=""){
                $("#id_dataset+.help-block").parent().addClass("has-error");
            }else{
                $("#id_dataset+.help-block").parent().removeClass("has-error");
            }
            $("#stats-n").text(data["n"]);
            $("#stats-m").text(data["m"]);
            $("#stats-complet>.yes").toggle(data["complete"]);
            $("#stats-complet>.no").toggle(!data["complete"]);
            $("#stats-invalid").toggle(data["invalid"]);
            $("#btn-compute").attr("disabled",data["invalid"]);
            $("#id_dataset").prop("readonly",false) ;
            if($("#id_norm_auto").prop("checked")){
                $("#id_norm_auto").attr("data-default-value",data["norm"])
            }
            if($("#id_dist_auto").prop("checked")){
                $("#id_dist_auto").attr("data-default-value",data["dist"])
            }
            if($("#id_algo_auto").prop("checked")){
                $("#id_algo_auto").attr("data-default-value",data["algo"])
            }
            $(".param-auto").change();
            $("#auto-compute-host>.yes").toggle(data["auto-compute"]);
            $("#auto-compute-host>.no").toggle(!data["auto-compute"]);
            $("#auto-compute-host").attr("data-value", data["auto-compute"]);
            if (typeof callback != "undefined")
                callback(data);
            $("#updating-stats-indicator").fadeOut();
        },
        error: function (textStatus, xhr) {
            console.error(textStatus);
            console.error(xhr);
            $("#updating-stats-indicator").fadeOut();
        }
    });
}

//refresh_settings_from_datasets($('form'));
//https://stackoverflow.com/a/6217551/2144569
function delayed_onkeyup(action, instant_action){
    var callcount = 0;
    var action = action
    var delayAction = function(action, time){
        var expectcallcount = callcount;
        var delay = function(){
            if(callcount == expectcallcount){
                action();
            }
        }
        setTimeout(delay, time);
    }
    return function(eventtrigger){
        ++callcount;
        instant_action(eventtrigger);
        delayAction(action, 1200);
    }
}

function on_change_param_auto_checkbox(auto_checkbox){
    var name = $(auto_checkbox).attr("name");
    name=name.substring(0,name.lastIndexOf('_'));
    if($(auto_checkbox).prop("checked")){
        $("[name='"+name+"']").prop("checked",false);
        $("[name='"+name+"'][value='"+$(auto_checkbox).attr("data-default-value")+"']").prop("checked",true);
    }
}

function on_change_param_radio(input){
    var name = $(input).attr("name");
    $("[name='"+name+"_auto']").prop("checked",false).change()
}

function compute_consensus_from_dataset(form, callback){
    form=$(form);
    $("#computing-indicator").show();
    $("#btn-compute").attr("disabled",true);
    $("#id_dataset").prop("readonly",true) ;
    $.ajax({
        type: form.attr('method'),
        url:form.attr('data-submit-url'),
        data: form.serialize(),
        success: function (data, textStatus, xhr) {
            console.log(data);
            if (typeof results_table != "undefined"){
                results_table.destroy();
            }
            $('#results_table').empty(); // empty in case the columns change

            results_table = $('#results_table').DataTable( {
                data: data['results'],
                columns: [
                    {
                        data: "algo.name",
                        title: "Algo",
                    },
                    {
                        data: "duration",
                        title: "Duration (ms)",
                    },
                    {
                        data: "distance",
                        title: "Distance",
                    },
                    {
                        data: "consensus",
                        title: "Consensus",
                        render: function ( data, type, row ) {
                            return ranking_with_ties_to_str(data[0]);
                        },
                    },
                ]
            } );

            if (typeof callback != "undefined")
                callback(data);
            $("#computing-indicator").fadeOut();
            $("#btn-compute").attr("disabled",false);
            $("#id_dataset").prop("readonly",false) ;
            //fade_border_to_and_back($("#results-host").parent(),"#0D0");
            fade_background_to_and_back($("#results-host").parent(),"#f5fff5");
        },
        error: function (textStatus, xhr) {
            console.error(textStatus);
            console.error(xhr);
            $("#computing-indicator").fadeOut();
            $("#btn-compute").attr("disabled",false);
            $("#id_dataset").prop("readonly",false) ;
        }
    });
}
var results_table;

stack_onload(function () {
    $(".param-auto").change(function(event) {on_change_param_auto_checkbox(this);});
    $(".param-host input").change(function(event) {on_change_param_radio(this);});
    refresh_settings_from_datasets($('form'));
    $(".param-host").each(function() {
        var v = $(this).parent();
        $(v).collapse(getCookie($(v).attr("id"),"hide"));
    });

    //save in cookie the state of each panel
    $(".param-host").parent()
    .on('shown.bs.collapse', function () {
        setCookie($(this).attr("id"),"show");
    })
    .on('hidden.bs.collapse', function () {
        setCookie($(this).attr("id"),"hide");
    });

    //once typed in the text area, refresh the stats of the datasets
    $("#id_dataset").keyup(
        delayed_onkeyup(
            function(){
                var callback;
                if ($("#auto-compute-host").attr("data-value")){
                    refresh_settings_from_datasets(
                        $('form'),
                        function (){
                            compute_consensus_from_dataset($('form'))
                        }
                    );
                }else{
                    refresh_settings_from_datasets($('form'));
                }
            },
            function (){
                $("#btn-compute").attr("disabled",true);
                $("#future-update-indicator").fadeIn();
            }
        )
    );
});