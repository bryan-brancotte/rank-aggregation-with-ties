function ranking_with_ties_to_str(ranking){
    var ret = "";
    for (var i in ranking) {
        if (i>0){
            ret+=', ';
        }
        ret+="["+(ranking[i].join(', '))+"]";
    }
    return "["+ret+"]";
}