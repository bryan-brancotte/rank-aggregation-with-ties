function reusabled_plot() {
    var margin = {top: 10, right: 50, bottom: 50, left: 80},
        width = 960 ,
        height = 500,
        svg,
        tooltip,
        duration=300,
        data,
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
        y_scale_is_duration=false,
        is_scatterplot=false,
        is_multiline=true,
        data_filter = function(d) {return true;},
        series_accessor = function(d) {return d.series;},
        x_accessor = function(d) {return d.x;},
        y_accessor = function(d) {return d.y;},
        y_ticks_formatter = ticksDefault,
        x_label = "",
        y_label = "",
        tooltip_builder = function(d){
            return "<table class='table table-condensed' style='margin-bottom:0px;'><tbody>"+
                "<tr><th>x</th><td>"+plot.x_accessor()(d)+"</td></tr>"+
                "<tr><th>y</th><td>"+plot.y_ticks_formatter()(plot.y_accessor()(d))+"</td></tr>"+
                "</tbody></table>";
        }
        color = d3.scaleOrdinal(d3.schemeCategory10);
    function chart(selection){
        selection.each(function() {
            target_selector=this;
            // set the ranges
            width = $(target_selector).width()
                - parseFloat($(target_selector).css("padding-left").replace("px", ""))
                - parseFloat($(target_selector).css("padding-right").replace("px", ""));
            var inner_width = width - margin.left - margin.right;
            var inner_height = height - margin.top - margin.bottom;
            xScale = d3.scaleLinear().range([0, inner_width]);
            yScale = (y_scale_is_log?d3.scaleLog():d3.scaleLinear()).range([inner_height, 0]);
            line_generator = d3.line()
                .x(function(d) { return xScale(d.x); })
                .y(function(d) { return yScale(d.y); });


            svg = d3.select(target_selector).append("svg")
                        .attr("class", "reusabled_plot")
                        .attr("width", inner_width + margin.left + margin.right)
                        .attr("height", inner_height + margin.top + margin.bottom)
                    .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            /*tooltip = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);*/
            tooltip = d3.tip()
                .attr('class', 'd3-tip')
                .offset([-8, 0])
                .html(tooltip_builder);
            svg.call(tooltip);

            // Add the X Axis
            xAxis = d3.axisBottom(xScale);
            svg.append("g")
                .attr("transform", "translate(0," + inner_height + ")")
                .attr("class", "x axis")
                .call(xAxis)
                .attr("opacity",0);
            svg.append("g")
                .attr("transform", "translate("+inner_width/2+"," + (inner_height+margin.bottom/2) + ")")
                .append("text")
                .attr("class", "x axis label")
                .attr("opacity",0)
                .attr('text-anchor','middle')
                .text(typeof(x_label) === 'function'?x_label():x_label);

            // Add the Y Axis
            yAxis = d3.axisLeft(yScale);
            if(y_scale_is_duration){
                if(y_scale_is_log)
                    yAxis.ticks(inner_height/30, ticksDuration);
                else
                    yAxis.tickFormat(ticksDuration);
            }
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .attr("opacity",0);
            svg.append("g")
                .attr("transform", "translate(" + -margin.right + ',' + inner_height/2 + ")")
                .append("text")
                .attr("class", "y axis label")
                .attr("transform", "rotate(-90)")
                .attr("opacity",0)
                .attr('text-anchor','middle')
                .text(typeof(y_label) === 'function'?y_label():y_label);

            update = function(){
                data=row_data.filter(data_filter);
                data.forEach(function(d) {
                    d.x = +x_accessor(d);
                    d.y = +y_accessor(d);
                    d.grp = series_accessor(d);
                });
                var data_grouped = d3.nest()
                    .key(function(d) {
                        return d.grp;
                    })
                    .sortValues(function(a,b) {
                        return x_accessor(a) - x_accessor(b);
                    })
                    .entries(data);

                xScale.domain([
                    d3.min(data, function(d) { return d.x; }),
                    d3.max(data, function(d) { return d.x; })
                ]);
                xScale.domain([
                    xScale.domain()[0]-(xScale.domain()[1]-xScale.domain()[0])*0.01,
                    xScale.domain()[1]*1.1
                ]);
                yScale.domain([
                    d3.min(data, function(d) { return d.y<0?-d.y:d.y; })*0.5,
                    d3.max(data, function(d) { return d.y; })
                ]);

                // Add the scatterplot
                //if(is_scatterplot)
                svg.selectAll(".dot")
                        .data(data, function(d) { return d.__d3js_id || (d.__d3js_id = data_identifier(d)) })
                    .enter().append("circle")
                        .attr('class', 'dot')
                        .attr("r", 0)
                        .style('cursor', 'pointer')
                        .attr("cx", function(d) { return xScale(d.x); })
                        .attr("cy", function(d) { return yScale(d.y); })
                        .attr("fill", function(d) { return color(d.grp)})
                        .attr('data-series', function(d, i) {return d.grp})
                        .attr('data-series-toggled', 'true')
                        .on('mouseover', tooltip.show)
                        .on('mouseout',  function(d,i){
                            if($(this).attr("data-keep-tooptip")!="true")
                                tooltip.hide(d,i);
                        })
                        .on('click', function(d){
                            $(this).attr("data-keep-tooptip",$(this).attr("data-keep-tooptip")!="true");
                        })
                        .transition()
                        .duration(duration)
                        .attr("r", 5);


                // Add the multiline
                if(is_multiline)
                svg.selectAll(".line")
                        .data(data_grouped, function(d) { return d.key })
                    .enter().append("svg:path")
                        .attr('class', 'line')
                        .attr('data-series', function(d, i) {return d.key})
                        .attr('data-series-toggled', 'true')
                        .attr('d', function(d) { return line_generator(d.values)})
                        .attr("stroke", function(d) { return color(d.values[0].grp)} )
                        .attr('stroke-width', 0)
                        .attr('fill', 'none')
                        .transition()
                        .duration(duration)
                        .attr('stroke-width', 2);

                svg.select(".x.axis") // change the x axis
                    .call(xAxis);
                svg.selectAll(".x.axis")
                    .transition()
                    .duration(duration)
                    .attr("opacity",1);

                svg.select(".y.axis") // change the y axis
                    .call(yAxis);
                svg.selectAll(".y.axis")
                    .transition()
                    .duration(duration)
                    .attr("opacity",1);

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
                    .attr('data-series', function(d, i) {return d})
                    .attr('data-series-toggled', 'true')
                    .style('fill', color)
                    .style('stroke', color)
                    .style('cursor', 'pointer')
                    .on("click", function(d){
                        d3.selectAll("[data-series='"+d+"'][data-series-toggled='true']")
                            .transition()
                            .duration(duration)
                            .attr("opacity",0.4)
                            .attr('stroke-opacity', 0.4)
                            .attr('data-series-toggled', 'false');
                        d3.selectAll("[data-series='"+d+"'][data-series-toggled='true'].dot")
                            .transition()
                            .duration(duration)
                            .attr("opacity",0.15)
                            .attr('data-series-toggled', 'false');
                        d3.selectAll("[data-series='"+d+"'][data-series-toggled='false']")
                            .transition()
                            .duration(duration)
                            .attr("opacity",1)
                            .attr('stroke-opacity', 1)
                            .attr('data-series-toggled', 'true');
                    })
                    .on("mouseover", function(d){
                        d3.selectAll("[data-series='"+d+"']")
                            .attr("r",8)
                            .attr('stroke-width', 5);
                    })
                    .on("mouseout", function(d){
                        d3.selectAll("[data-series='"+d+"']")
                            .attr("r",5)
                            .attr('stroke-width', 2);
                    });

                legend.append('text')
                    .attr('x',- legendRectSize + 2*legendSpacing)
                    .attr('y', legendRectSize - legendSpacing)
                    .attr('text-anchor','end')
                    .text(function(d) { return d; });

            }
        });
    }

    function ticksDuration(d) {
        if(d<1)
            return Math.round(d*1000*1000)/1000+" μs";
        if(d<1000)
            return Math.round(d*1000)/1000+" ms";
        d/=1000;
        if(d<60)
            return Math.round(d*1000)/1000+" s";
        d/=60;
        return Math.round(d*100)/100+" h";
    }

    function ticksDefault(d) {return d;}


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
     * Accessor configuring whether we do a scatter plot or a line chart
     * @param {boolean} value
     */
    chart.is_scatterplot = function(value) {
        if (!arguments.length) return is_scatterplot;
        is_scatterplot = value;
        is_multiline=!value;
        return chart;
    };
    /**
     * Accessor configuring whether we do a scatter plot or a line chart
     * @param {boolean} value
     */
    chart.is_multiline = function(value) {
        if (!arguments.length) return is_multiline;
        is_multiline = value;
        is_scatterplot=!value;
        return chart;
    };
    chart.y_scale_is_log = function(value) {
        if (!arguments.length) return y_scale_is_log;
        y_scale_is_log = value;
        return chart;
    };
    chart.y_scale_is_duration = function(value) {
        if (!arguments.length) return y_scale_is_duration;
        y_scale_is_duration = value;
        if(y_ticks_formatter === ticksDefault || y_ticks_formatter === ticksDuration)
            y_ticks_formatter = ( y_scale_is_duration ? ticksDuration : ticksDefault );
        return chart;
    };
    chart.y_ticks_formatter = function(value) {
        if (!arguments.length) return y_ticks_formatter;
        y_ticks_formatter = value;
        return chart;
    };
    chart.data_filter = function(value) {
        if (!arguments.length) return data_filter;
        data_filter = value;
        return chart;
    };
    chart.data_identifier = function(value) {
        if (!arguments.length) return data_identifier;
        data_identifier = value;
        return chart;
    };
    chart.series_accessor = function(value) {
        if (!arguments.length) return series_accessor;
        series_accessor = value;
        return chart;
    };
    chart.x_accessor = function(value) {
        if (!arguments.length) return x_accessor;
        x_accessor = value;
        return chart;
    };
    chart.y_accessor = function(value) {
        if (!arguments.length) return y_accessor;
        y_accessor = value;
        return chart;
    };
    chart.x_label = function(value) {
        if (!arguments.length) return x_label;
        x_label = value;
        return chart;
    };
    chart.y_label = function(value) {
        if (!arguments.length) return y_label;
        y_label = value;
        return chart;
    };
    chart.tooltip_builder = function(value) {
        if (!arguments.length) return tooltip_builder;
        tooltip_builder = value;
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