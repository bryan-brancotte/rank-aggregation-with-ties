function multiline_plot() {
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
        xScale,
        yScale,
        xAxis,
        yAxis,
        line_generator,
        y_scale_is_log=true,
        is_scatterplot=false,
        is_multiline=true,
        color = d3.scaleOrdinal(d3.schemeCategory10);
    function chart(selection){
        selection.each(function() {
            target_selector=this;
            // set the ranges
            width = $(target_selector).width()
            var inner_width = width - margin.left - margin.right;
            var inner_height = height - margin.top - margin.bottom;
            xScale = d3.scaleLinear().range([0, inner_width]);
            yScale = (y_scale_is_log?d3.scaleLog():d3.scaleLinear()).range([inner_height, 0]);
            line_generator = d3.line()
                .x(function(d) { return xScale(d.x); })
                .y(function(d) { return yScale(d.y); });


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
            if(y_scale_is_log)
                yAxis.ticks(inner_height/30, ticksDuration);
            else
                yAxis.tickFormat(ticksDuration);
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            update = function(){
                data=row_data.filter(
                    function(d) {
                        return d.value>0 && d.descriptor=="mean";
                    });
                data.forEach(function(d) {
                    d.x = +d.n;
                    d.y = +d.value;
                    d.grp = d.algo;
                    console.log(d.algo+":"+d.x);
                });
                var data_grouped = d3.nest()
                    .key(function(d) {
                        return d.grp;
                    })
                    .entries(data);

                xScale.domain([d3.min(data, function(d) { return d.x; }), 1.1*d3.max(data, function(d) { return d.x; })]);
                yScale.domain([
                    d3.min(data, function(d) { return d.y<0?-d.y:d.y; })*0.5,
                    d3.max(data, function(d) { return d.y; })
                ]);

                // Add the scatterplot
                if(is_scatterplot)
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
                        .attr("cy", function(d) { return yScale(d.y); });

                // Add the multiline
                if(is_multiline)
                svg.selectAll(".line")
                        .data(data_grouped, function(d) { return d.key })
                    .enter().append("svg:path")
                        .attr('class', 'line')
                        .attr('d', function(d) { return line_generator(d.values)})
                        .attr("stroke", function(d) { return color(d.values[0].grp)} )
                        .attr('stroke-width', 2)
                        .attr('fill', 'none');

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

    function ticksDuration(d, i) {
        if(d<1)
            return Math.round(d*1000)+" μs";
        if(d<1000)
            return Math.round(d)+" ms";
        d/=1000;
        if(d<60)
            return Math.round(d)+" s";
        d/=60;
        return Math.round(d)+" h";
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