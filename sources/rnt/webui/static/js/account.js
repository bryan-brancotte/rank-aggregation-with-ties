stack_onload(function () {
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        url:get_jobs_url(),
        type:"GET",
        contentType: "application/json;charset=utf-8",
        success: function (data, textStatus, xhr) {
            $('#results_table').DataTable( {
                aaSorting: [[1,'asc']],
                data: data,
                columns: [
                    {
                        data: "identifier",
                        title: "Identifier",
                        render: function ( data, type, row ) {
                            return '<a href="'+get_job_url(data)+'">'+data.substring(0,8)+'</a>';
                        },
                    },
                    {
                        data: "name",
                        title: "Name",
                    },
                    {
                        data: "dist",
                        title: "Distance",
                    },
                    {
                        data: "norm",
                        title: "Normalisation",
                    },
                    {
                        data: "creation",
                        title: "Created on",
                    },
                    {
                        data: "task_count",
                        title: "# results",
                    },
                ]
            } );
        }
    });
})