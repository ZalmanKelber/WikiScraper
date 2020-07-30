const canvas = d3.select("#ranks");
ctx = canvas.node().getContext("2d");
width = canvas.attr("width");
height = canvas.attr("height");
r = width / 2;
// color = d3.scaleOrdinal(d3.schemeCategory20)

ids = {}
ranks.forEach((page, index) => {
  ids[page.id] = index
});


function drawNode(node) {
  ctx.beginPath();
  ctx.fillStyle = node.selected ? "rgba(127, 0, 0, .6)" : "rgba(60, 120, 255, .8)";
  ctx.moveTo(node.x, node.y);
  ctx.arc(node.x, node.y, Math.ceil(r * node.rank) + 1, 0, 2* Math.PI);
  ctx.fill();
  ctx.closePath();
}

function drawLink(link) {
  ctx.beginPath();
  ctx.strokeStyle = `rgba(63, 63, 63, ${findOpacity(ranks.length)})`;
  ctx.moveTo(ranks[ids[link.from_id]].x, ranks[ids[link.from_id]].y);
  ctx.lineTo(ranks[ids[link.to_id] || 0].x, ranks[ids[link.to_id] || 0].y);
  ctx.stroke();
  ctx.closePath();
}

function findOpacity(numNodes) {
  if (numNodes > 1000) {
    return .01
  }
  if (numNodes > 300) {
    return .03
  }
  return .1
}

function render() {
  ctx.clearRect(0, 0, width, height);
  routes.forEach(drawLink);
  ranks.forEach(drawNode);
}

sim = d3.forceSimulation()
  .force("x", d3.forceX(width / 2))
  .force("y", d3.forceY(height / 2))
  .force("charge", d3.forceManyBody().strength(findConstant(ranks.length)))
  .on("tick", render);
sim.nodes(ranks)

function findConstant(numNodes) {
  if (numNodes > 1000) {
    return -3;
  }
  if (numNodes > 300) {
    return -5;
  }
  if (numNodes > 100) {
    return -9;
  }
  if (numNodes > 50) {
    return -25;
  }
  if (numNodes > 20) {
    return -50;
  }
  return -100;
}

function dragsubject() {
  return sim.find(d3.event.x, d3.event.y);
}

function dragstarted() {
  if (!d3.event.active) sim.alphaTarget(0.3).restart();
  d3.event.subject.fx = d3.event.subject.x;
  d3.event.subject.fy = d3.event.subject.y;
  ranks.forEach(rank => rank.selected = false);
  d3.event.subject.selected = true;
  renderArticleDisplay(d3.event.subject);
}

function dragged() {
  d3.event.subject.fx = d3.event.x;
  d3.event.subject.fy = d3.event.y;
}

function dragended() {
  if (!d3.event.active) sim.alphaTarget(0);
  d3.event.subject.fx = null;
  d3.event.subject.fy = null;
}

function renderArticleDisplay(article) {
  p = document.getElementById("article-display");
  p.innerHTML = `<a href="https://en.wikipedia.org/wiki/${article.url}" target="_blank">
                  ${article.title}
                </a>
                , rank: ${(article.rank * 100).toFixed(4)}%`
}
canvas
  .call(d3.drag()
    .container(canvas.node())
    .subject(dragsubject)
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

render();
