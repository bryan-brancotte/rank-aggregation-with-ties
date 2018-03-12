function handleFileSelect(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    var files = evt.dataTransfer.files; // FileList object.

    // files is a FileList of File objects. List some properties.
    var output = [];

    for (var i = 0, f; f = files[i]; i++) {
        var is_the_dataset = false;
        if(f.name.endsWith("_GS")){
            dataset_filename = f.name.substring(0,f.name.length-3);
        }else if(f.name.endsWith("_GS.err")){
        }else if(f.name.endsWith("_GS.log")){
        }else {
            dataset_filename = f.name;
            is_the_dataset = true;
        }
        if(!dataset_filename)
            continue
        dataset_dict=get_dict_for_dataset(dataset_filename);
        if(is_the_dataset){
            dataset_dict.size=f.size;
            dataset_dict.lastModifiedDate=f.lastModifiedDate;
        }
//        output.push('<li><strong>', escape(f.name), '</strong> (', f.type || 'n/a', ') - ',
//                  f.size, ' bytes, last modified: ',
//                  f.lastModifiedDate ? f.lastModifiedDate.toLocaleDateString() : 'n/a',
//                  '</li>');
        var reader = new FileReader();
        reader.onload = (function(theFile) {
            return function(e) {
//                console.log(theFile);
//                console.log(this);
//                console.log(e);
                if(theFile.name.endsWith("_GS")){
                    dataset_dict=get_dict_for_dataset(theFile.name.substring(0,theFile.name.length-3));
                    dataset_dict.gs=this.result;
                    refresh_row(dataset_dict);
                }else if(theFile.name.endsWith("_GS.err")){
                }else if(theFile.name.endsWith("_GS.log")){
                }else {
                    handle_dropped_dataset(theFile, this.result);
                }
            };
        })(f);
        reader.readAsText(f);
    }
    dataset_table.rows().draw(false);
}

function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}

function refresh_row(dataset_dict){
    var tr=$('#'+dataset_dict.filename).parents('tr');
    var row = dataset_table.row( tr );
    if(row.length>0){
        row.data(dataset_dict).invalidate();
        tr.find('[data-toggle="popover"]').popover();
    }
}

function get_dict_for_dataset(name){
    if (escape(name) in datasets){
        dataset_dict = datasets[escape(name)];
    }else{
        dataset_dict={
            'filename':escape(name),
            'size':0,
            'lastModifiedDate':'N/A',
            'content':'loading',
            'n':'loading',
            'm':'loading',
            'complete':null,
            'gs':'N/A',
            'should_upload':false,
            'note':'',
        };
        datasets[escape(name)] = dataset_dict;
        dataset_table.row.add(dataset_dict);
    }
    return dataset_dict;
}

function handle_dropped_dataset(file,content){
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        type: "POST",
        url:dataset_evaluate,
        data: {"dataset":content,'name':file.name},
        success: function (data, textStatus, xhr) {
            dataset_dict=get_dict_for_dataset(file.name);
            dataset_dict.content = content;
            dataset_dict.n = data.n;
            dataset_dict.m = data.m;
            dataset_dict.complete = data.complete;
            dataset_dict.should_upload = !data.has_homonym;
            dataset_dict.note = data.has_homonym?"Has homonym":"";
            refresh_row(dataset_dict);
        },
    });
}

function upload_datasets(){
    $("[name='dataset_to_upload']:checked").each(function(pos,elt){
        upload_dataset($(elt).attr("value"));
    });
}

function upload_dataset(filename){
    var dataset_dict=get_dict_for_dataset(filename);
    $.ajax({
        headers: {
            'X-CSRFToken':getCookie('csrftoken'),
        },
        type: "POST",
        url:webapi_dataset_list,
        data: {
            'name':filename,
            'content':dataset_dict.content,
            'n':dataset_dict.n,
            'm':dataset_dict.m,
            'complete':dataset_dict.complete,
            'step':$("#id_step").val(),
            'public':$("#id_public").prop("checked")
        },
        success: function (data, textStatus, xhr) {
            var dataset_dict=get_dict_for_dataset(data.name);
            dataset_dict.note="Created";
            dataset_dict.should_upload=false;
            refresh_row(dataset_dict);
        },
    });
}

stack_onload(function () {
    dataset_table = $('#dataset_table').DataTable( {
        paging:false,
        columnDefs: [
            { "width": "1%", "targets": 0 },
            { "width": "1%", "targets": 3 },
            { "width": "1%", "targets": 4 },
            { "width": "1%", "targets": 5 },
            { "width": "1%", "targets": 7 },
            {"className": "text-center", "targets": "_all"}
        ],
        columns: [
            {
                data: "filename",
                title: "Upload",
                render: function ( data, type, row ) {
                    return '<input type="checkbox" name="dataset_to_upload" value="'+data+'"'+(row.should_upload?' checked':'')+'>';
                },
            },
            {
                data: "filename",
                title: "Filename",
                render: function ( data, type, row ) {
                    return '<span id="'+data+'" class="filename">'+data+'</span>';
                },
            },
            {
                data: "content",
                title: "Content",
                render: function ( data, type, row ) {
                    return '<a data-toggle="popover" title="Content of the dataset" data-placement="bottom" data-content="'+data.replace(/\n/g,"<br/>")+'" data-html="true" data-trigger="hover click">See it <i class="glyphicon glyphicon-eye-open"></i></a>';
                },
            },
            {
                data: "n",
                title: "n:&nbsp;#Elements",
            },
            {
                data: "m",
                title: "m:&nbsp;#Rankings",
            },
            {
                data: "complete",
                title: "Complete",
                render: function ( data, type, row ) {
                    return data == null ? "N/A": data ? "Complete" : "Not&nbsp;complete";
                },
            },
            {
                data: "gs",
                title: "Gold standard",
                render: function ( data, type, row ) {
                    if(data=="N/A")
                        return data;
                    return '<a data-toggle="popover" title="Gold standard" data-placement="bottom" data-content="'+data.replace(/\n/g,"<br/>")+'" data-html="true" data-trigger="hover click">See it <i class="glyphicon glyphicon-eye-open"></i></a>';
                },
            },
            {
                data: "size",
                title: "File&nbsp;size",
            },
            {
                data: "lastModifiedDate",
                title: "Last modified",
            },
            {
                data: "note",
                title: "Note",
            },
        ]
    } );
});