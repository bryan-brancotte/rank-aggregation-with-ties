function refresh_settings_from_datasets(form, callback){
    form=$(form);
    $.ajax({
        type: form.attr('method'),
        url:form.attr('data-check-url'),
        data: form.serialize(),
        success: function (data, textStatus, xhr) {
            console.log(data);
            $("#stats-n").text(data["n"]);
            $("#stats-m").text(data["m"]);
            if(data["complet"]){
                $("#stats-complet>.yes").show();
                $("#stats-complet>.no").hide();
            }else{
                $("#stats-complet>.yes").hide();
                $("#stats-complet>.no").show();
            }
            $("#stats-invalid").toggle(data["invalid"]);

            callback(data);
        },
        error: function (textStatus, xhr) {
            console.err(textStatus);
            console.err(xhr);
        }
    });
}