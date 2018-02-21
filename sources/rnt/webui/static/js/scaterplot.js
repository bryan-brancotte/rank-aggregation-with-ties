
function scaterplot() {
    var margin = {top: 10, right: 50, bottom: 50, left: 80},
        width = 960 ,
        height = 500,
        svg,
        duration=750,
        row_data,
        data_url,
        update,
        debug=false,
        legendRectSize = 18,
        legendSpacing = 4,
        color = d3.scaleOrdinal(d3.schemeCategory10);
    function chart(selection){
        selection.each(function() {
            target_selector=this;
            // set the ranges
            width = $(target_selector).width()
            var inner_width = width - margin.left - margin.right;
            var inner_height = height - margin.top - margin.bottom;
            var xScale = d3.scaleLinear().range([0, inner_width]);
            var yScale = d3.scaleLog().range([inner_height, 0]);

            svg = d3.select(target_selector).append("svg")
                        .attr("width", inner_width + margin.left + margin.right)
                        .attr("height", inner_height + margin.top + margin.bottom)
                    .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Add the X Axis
            xAxis = d3.axisBottom(xScale);
            svg.append("g")
                .attr("transform", "translate(0," + inner_height + ")")
                .attr("class", "x axis")
                .call(xAxis);

            // Add the Y Axis
            yAxis = d3.axisLeft(yScale);
            yAxis.ticks(15, function(d, i) {
                if(d<1)
                    return Math.round(d*1000)+" μs";
                if(d<1000)
                    return Math.round(d)+" ms";
                d/=1000;
                if(d<60)
                    return Math.round(d)+" s";
                d/=60;
                return Math.round(d)+" h";
            });
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            update = function(){
                data=row_data.filter(
                    function(d) {
                        return d.duration>0;
                    });
                data.forEach(function(d) {
                    d.x = +d.distance_value;
                    d.y = +d.duration;
                    d.grp = d.algo.key_name;
                });

                xScale.domain([0, 1.1*d3.max(data, function(d) { return d.x; })]);
                yScale.domain([
                    d3.min(data, function(d) { return d.y<0?-d.y:d.y; })*0.5,
                    d3.max(data, function(d) { return d.y; })
                ]);

                // Add the scatterplot
                svg.selectAll(".dot")
                        .data(data, function(d) { return d.__d3js_id || (d.__d3js_id = d.algo.id+"-"+d.dataset); })
                    .enter().append("circle")
                        .attr('class', 'dot')
                        .attr("r", 5)
                        .attr("cx", function(d) { return xScale(d.x); })
                        .attr("cy", function(d) { return yScale(yScale.domain()[0]); })
                        .attr("fill", function(d) { return color(d.grp)} )
                        .transition()
                        .duration(duration)
                        .attr("cy", function(d) { return yScale(d.y); })

                svg.select(".x.axis") // change the x axis
                    .transition()
                    .duration(duration)
                    .call(xAxis);

                svg.select(".y.axis") // change the y axis
                    .transition()
                    .duration(duration)
                    .call(yAxis);

                var legend = svg.selectAll('.legend')
                    .data(color.domain())
                    .enter()
                    .append('g')
                    .attr("opacity",0);
                legend
                    .attr('transform', function(d, i) {
                        var vert = i * (legendRectSize + legendSpacing) ;
                        return 'translate(' + inner_width + ',' + vert + ')';
                    })
                    .transition()
                    .duration(duration)
                    .attr("opacity",1)
                    .attr('class', 'legend');

                legend.append('rect')
                    .attr('width', legendRectSize)
                    .attr('height', legendRectSize)
                    .style('fill', color)
                    .style('stroke', color);

                legend.append('text')
                    .attr('x',- legendRectSize + 2*legendSpacing)
                    .attr('y', legendRectSize - legendSpacing)
                    .attr('text-anchor','end')
                    .text(function(d) { return d; });

            }
        });
    }


    /**
     * Accessor configuring the animation's duration
     * @param {boolean} value
     */
    chart.duration = function(value) {
        if (!arguments.length) return duration;
        duration = value;
        return chart;
    };
    /**
     * Accessor to the url where the json formatted tree can be found
     * @param {string} value - a valid url
     */
    chart.data_url = function(value) {
        if (!arguments.length) return data_url;
        identifierToElement={};
        data_url = value;
        d3.json(value, function(json) {
            chart.data(json)
        });
        return chart;
    };
    /**
     * Accessor to the url where the json formatted tree can be found
     * @param {string} value - a valid url
     */
    chart.data = function(value) {
        if (!arguments.length) return row_data;
        row_data = value;
        update()
        return chart;
    };
    return chart;
}