var palette = {
      "lightgray": "#819090",
      "gray": "#708284",
      "mediumgray": "#536870",
      "darkgray": "#475B62",

      "darkblue": "#0A2933",
      "darkerblue": "#042029",

      "paleryellow": "#FCF4DC",
      "paleyellow": "#EAE3CB",
      "yellow": "#A57706",
      "orange": "#BD3613",
      "red": "#D11C24",
      "pink": "#C61C6F",
      "purple": "#595AB7",
      "blue": "#2176C7",
      "green": "#259286",
      "yellowgreen": "#738A05"
  }

function createLineGraph(data, chartId, svgId) {

    var averagedata = []
    var filenames = []

    var links = [];

    for (var i = 0; i < data.length; i++){
      averagedata.push(data[i].average)
      filenames.push(data[i].filename)
    }

    var margin = {top:30, right:30, bottom:150, left:50}

    var height = 500 - margin.top - margin.bottom,
      width = window.innerWidth - margin.left - margin.right;

    var tempColor;

    var circleWidth = 1;

    var maxValue = 1.2 * d3.max(averagedata);
    var minValue = 0
    if (d3.min(averagedata) > 0)
      minValue = 0.8 * d3.min(averagedata);
    else
      minValue = 1.2 * d3.min(averagedata);

    var xOffset = (width/(averagedata.length + 1))/2

    var yScale = d3.scale.linear()
      .domain([minValue, maxValue])
      .range([0,height], .2);

    var xScale = d3.scale.ordinal()
      .domain(d3.range(0, filenames.length))
      .rangeBands([0, width]);

    var tooltip = d3.select('body').append('div')
                .style('position', 'absolute')
                .style('paddng','0 10px')
                .style('background', 'white')
                .style('opacity',0);

    var myGroup = d3.select(chartId).append('svg')
      .attr('id',svgId)
      .style('background', '#F7F5EF')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
      .style('background', '#C9D7D6')




    var myLineChart = myGroup.selectAll('circle')
      .data(averagedata)
      .enter().append('circle')
          .attr('cx', function(d, i) { return i * width/averagedata.length + xOffset; })
          .attr('cy', function(d) { return height-yScale(d); })
          .attr('r', circleWidth )
          .attr('fill', palette.darkblue)

      .on('mouseover', function(d) {

          tooltip.transition()
              .style('opacity', .9)

          tooltip.html(d)
              .style('left', (d3.event.pageX - 35) + 'px')
              .style('top', (d3.event.pageY - 30) + 'px')

          tempColor = this.style.fill;
          d3.select(this)
          .style('opacity', 5)
          .style('fill','yellow')
      })

      .on('mouseout', function(d) {
          d3.select(this)
              .style('opacity', 1)
              .style('fill', tempColor)
      })


    var vGuideScale = d3.scale.linear()
      .domain([minValue, maxValue])
      .range([height,0]);

    var vAxis = d3.svg.axis()
      .scale(vGuideScale)
      .orient('left')
      .ticks(10);

    var vGuide = d3.select('svg#'+svgId).append('g')
      vAxis(vGuide)
      vGuide.attr('transform','translate(' + margin.left + ',' + margin.top + ')')
      vGuide.selectAll('path')
          .style({ fill: 'none', stroke: "#000"})
      vGuide.selectAll('line')
          .style({ stroke: "#000"});

    var hAxis = d3.svg.axis()
      .scale(xScale)
      .orient('bottom')
      .tickValues(function(d,i){
        var values = [0];
        var distance = Math.ceil(filenames.length/20);
        var value = distance;
        while (value < filenames.length){
          values.push(value)
          value += distance;
        }
        return values;
      })
      .tickFormat(function(d,i){
          name = filenames[d];
          if (name.length > 20)
            return name.slice(0, 17) + '...';
          return name;
      });


    var hGuide = d3.select('svg#'+svgId).append('g')
      hAxis(hGuide)
      hGuide.attr('transform','translate(' + margin.left + ',' + (height +
          margin.top) + ')')

      hGuide.selectAll('path')
          .style({ fill: 'none', stroke: "#000"})
      hGuide.selectAll('line')
          .style({ stroke: "#000"});



      hGuide.selectAll("text")
              .style("text-anchor", 'end')
              .attr("dx", "-.02em")
              .attr("dy", ".05em")
              .attr("transform", "rotate(-65)" )


    var lineGen = d3.svg.line()
    .x(function(d, i) {
      return xScale(i);
    })
    .y(function(d) {
      return yScale(d.average);
    });

    myGroup.attr("class", "line")
          .selectAll("line").data(averagedata)
          .enter().append("line")
          .style("stroke", "gray")
          .attr("x1", function(d, i) { return i * width/averagedata.length + xOffset; })
          .attr("y1", function(d) { return height - yScale(d); })
          .attr("x2", function(d, i) {
              if (i < averagedata.length - 1){
                  return (i+1) * width/averagedata.length + xOffset;
              }
              else{
                  return i * width/averagedata.length + xOffset;
              }
          })
          .attr("y2", function(d, i) {
              if (i < averagedata.length - 1){
                  return height-yScale(averagedata[i+1]);
              }
              else {
                  return height-yScale(averagedata[i]);
              }
          })

}







