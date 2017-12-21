function refresh_settings_from_datasets_and_compute_when_possible(){
    refresh_settings_from_datasets(
        $('form'),
        function (){
            if ($("#auto-compute-host").attr("data-value")){
                compute_consensus_from_dataset($('form'));
            }
        }
    );
}

function refresh_settings_from_datasets(form_param, callback){
    var form=$(form_param);
    $("#updating-stats-indicator").show();
    $("#future-update-indicator").hide();
    $("#btn-compute").attr("disabled",true);
    $("#id_dataset").prop("readonly",true) ;
    $.ajax({
        type: form.attr('method'),
        url:form.attr('data-check-url'),
        data: form.serialize(),
        success: function (data, textStatus, xhr) {
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
        $("[name='"+name+"'][value='"+$(auto_checkbox).attr("data-default-value")+"']").prop("checked",true).change()/**/;
    }
}

function on_change_param_radio(input){
    $(input).closest(".panel-group").find(".param-indicator").text("("+$(input).parent().text().trim()+")");
    var name = $(input).attr("name");
    var auto_checkbox=$("[name='"+name+"_auto']");
    if ($(auto_checkbox).attr("data-default-value") != $(input).attr("value")){
        auto_checkbox.prop("checked",false).change()
    }
}

function compute_consensus_from_dataset(form, callback){
    var form=$(form);
    if($(".in #id_dataset").length>0){
        $("#id_ranking_source").val("type");
    }else if($(".in #datasets_range_table").length>0){
        $("#id_ranking_source").val("range");
    }
    var data = form.serialize();
    $("#computing-indicator").show();
    $("#btn-compute").attr("disabled",true);
    $("#id_dataset").prop("readonly",true) ;
    form.find('input').prop("disabled",true);
    $.ajax({
        type: form.attr('method'),
        url:form.attr('data-submit-url'),
        data: data,
        success: function (data, textStatus, xhr) {
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
                        data: "dataset.name",
                        title: "Dataset",
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
                            s=ranking_with_ties_to_str(data[0])
                            for(var i=1;i<data.length;i++){
                                s+="<br/>"+ranking_with_ties_to_str(data[i]);
                            }
                            return s;
                        },
                    },
                ]
            } );

            if (typeof callback != "undefined")
                callback(data);
            $("#computing-indicator").fadeOut();
            $("#btn-compute").attr("disabled",false);
            $("#id_dataset").prop("readonly",false) ;
            fade_background_to_and_back($("#results-host").parent(),"#f5fff5", "white");
            form.find('input').prop("disabled",false);
        },
        error: function (textStatus, xhr) {
            console.error(textStatus);
            console.error(xhr);
            $("#computing-indicator").fadeOut();
            $("#btn-compute").attr("disabled",false);
            $("#id_dataset").prop("readonly",false) ;
            form.find('input').prop("disabled",false);
        }
    });
}
var results_table;
var datasets_range_table;

function row_in_range(min,val,max){
    min = parseInt( min, 10 );
    max = parseInt( max, 10 );
    val = parseInt( val, 10);

    if ( ( isNaN( min ) && isNaN( max ) ) ||
         ( isNaN( min ) && val <= max ) ||
         ( min <= val   && isNaN( max ) ) ||
         ( min <= val   && val <= max ) )
    {
        return true;
    }
    return false;
}

$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        if(settings['sTableId'] != "datasets_range_table")
            return true;
        return row_in_range($("#nb-elt .min").val(),data[2],$("#nb-elt .max").val())
        && row_in_range($("#nb-ranking .min").val(),data[3],$("#nb-ranking .max").val())
        //&& row_in_range($("#nb-step .min").val(),data['step'],$("#nb-step .max").val())
        ;
    }
);

stack_onload(function () {
    $(".param-auto").change(function(event) {on_change_param_auto_checkbox(this);});
    $(".param-host input").change(function(event) {on_change_param_radio(this);});
    $(".param-host").parent()
    .each(function() {
        var v = $(this);
        $(v).collapse(getCookie($(v).attr("id"),"hide"),);
    });
    $('#accordion .panel-collapse')
    .each(function() {
        var v = $(this);
        if("show"!=getCookie($(v).attr("id"),($(v).attr("id")=="collapse-type"?"show":"hide")))
            return;
        $(v).collapse({
            "toggle": true,
            'parent': '#accordion'
        });
    });

    //save in cookie the state of each panel
    $(".param-host").parent().add('#accordion .panel-collapse')
    .on('shown.bs.collapse', function () {
        setCookie($(this).attr("id"),"show");
    })
    .on('hidden.bs.collapse', function () {
        setCookie($(this).attr("id"),"hide");
    });

    //once typed in the text area, refresh the stats of the datasets
    $("#id_dataset").keyup(
        delayed_onkeyup(
            refresh_settings_from_datasets_and_compute_when_possible,
            function (){
                $("#btn-compute").attr("disabled",true);
                $("#future-update-indicator").fadeIn();
            }
        )
    );

    $('#accordion').on('shown.bs.collapse',function(e){
        $("#is-complete").slider("refresh");
    });

    $("#id_dbdatasets").addClass("compact").dataTable();

    $.ajax({
        type: 'GET',
        url:webapi_dataset_list,
        data: '',
        success: function (data, textStatus, xhr) {
            if (typeof datasets_range_table != "undefined"){
                datasets_range_table.destroy();
            }
            $('#datasets_range_table').empty(); // empty in case the columns change

            datasets_range_table = $('#datasets_range_table').DataTable( {
                data: data,
                columns: [
                    {
                        data: "pk",
                        title: "Use it",
                        render: function ( data, type, row ) {
                            return '<input type="checkbox" name="dbdatasets" value="'+data+'">';
                        },
                    },
                    {
                        data: "name",
                        title: "Name",
                    },
                    {
                        data: "n",
                        title: "n",
                    },
                    {
                        data: "m",
                        title: "m",
                    },
                    {
                        data: "complete",
                        title: "Complete",
                    },
                ]
            } );
            var min_m, max_m, min_n, max_n, min_st, max_st;
            datasets_range_table.data().toArray().forEach(function(row, i) {
                if(i==0){
                    min_m  = row['m'];
                    max_m  = row['m'];
                    min_n  = row['n'];
                    max_n  = row['n'];
                    min_st = row['step'];
                    max_st = row['step'];
                }
                min_m  = Math.min(min_m , row['m']);
                max_m  = Math.max(max_m , row['m']);
                min_n  = Math.min(min_n , row['n']);
                max_n  = Math.max(max_n , row['n']);
                min_st = Math.min(min_st, row['st']);
                max_st = Math.max(max_st, row['st']);
            });
            if(Number.isNaN(min_st))
                min_st=0;
            if(Number.isNaN(max_st))
                max_st=0;
            $("#nb-elt .slider").attr("data-slider-min",min_n);
            $("#nb-elt .slider").attr("data-slider-max",max_n);
            $("#nb-ranking .slider").attr("data-slider-min",min_m);
            $("#nb-ranking .slider").attr("data-slider-max",max_m);
            $("#nb-step .slider").attr("data-slider-min",min_st);
            $("#nb-step .slider").attr("data-slider-max",max_st);
            $("#nb-elt .slider").attr("data-slider-value",'['+min_n+','+max_n+']');
            $("#nb-ranking .slider").attr("data-slider-value",'['+min_m+','+max_m+']');
            $("#nb-step .slider").attr("data-slider-value",'['+min_st+','+max_st+']');

            $(".slider")
                .slider({});

            $(".slider")
                .change(function(e){
                    var val = $(this).val();
                    if ($(e.target).closest(".range-slider").length==0 || val == "")
                        return;
                    var val = val.split(',');
                    var tr = $(this).closest(".slider-host");
                    tr.find('.min').val(val[0]);
                    tr.find('.max').val(val[1]);
                    datasets_range_table.draw();
                })
                .change();
        },
        error: function (textStatus, xhr) {
            console.error(textStatus);
            console.error(xhr);
        }
    });

    $("#range-host .uncheck").click(function(){
        datasets_range_table.rows( { filter : 'applied'} ).data().each(
            function(row){
                $('[name="dbdatasets"][value="'+row['pk']+'"]').prop("checked",false);
            }
        );
    });
    $("#range-host .toggle-check").click(function(){
        datasets_range_table.rows( { filter : 'applied'} ).data().each(
            function(row){
                $('[name="dbdatasets"][value="'+row['pk']+'"]').prop("checked",!$('[name="dbdatasets"][value="'+row['pk']+'"]').prop("checked"));
            }
        );
    });
    $("#range-host .check").click(function(){
        datasets_range_table.rows( { filter : 'applied'} ).data().each(
            function(row){
                $('[name="dbdatasets"][value="'+row['pk']+'"]').prop("checked",true);
            }
        );
    });
    refresh_settings_from_datasets('form');
});
