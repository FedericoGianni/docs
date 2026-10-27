(function () {
  function patch() {
    var m = window.mermaid;
    if (!m || m.__forbayPatched) return !!m;
    m.__forbayPatched = true;

    var css = [
      "svg{background:transparent!important}",
      ".cluster rect{fill:transparent!important;stroke:var(--md-default-fg-color--lighter)!important}",
      ".cluster span,.cluster-label{color:var(--md-default-fg-color)!important}",
      ".node rect,.node circle,.node ellipse,.node polygon,.node path{fill:var(--md-mermaid-node-bg-color)!important;stroke:var(--md-mermaid-node-fg-color)!important}",
      ".nodeLabel,.nodeLabel p,.label{color:var(--md-mermaid-label-fg-color)!important}",
      ".edgePath .path,.flowchart-link{stroke:var(--md-mermaid-edge-color)!important}",
      ".edgeLabel,.edgeLabel p{background-color:var(--md-mermaid-label-bg-color)!important;color:var(--md-mermaid-edge-color)!important}"
    ].join("\n");

    var orig = m.initialize.bind(m);
    m.initialize = function (cfg) {
      cfg = cfg || {};
      cfg.themeCSS = (cfg.themeCSS || "") + "\n" + css;
      return orig(cfg);
    };
    return true;
  }

  if (!patch()) {
    var t = setInterval(function () {
      if (patch()) clearInterval(t);
    }, 50);
    setTimeout(function () { clearInterval(t); }, 5000);
  }
})();
