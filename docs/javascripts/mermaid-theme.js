(function () {
  function patch() {
    var m = window.mermaid;
    if (!m || m.__forbayPatched) return !!m;
    m.__forbayPatched = true;

    var css = [
      "svg{background:transparent!important}",
      ".node rect,.cluster rect{rx:6px!important;ry:6px!important}",
      ".cluster rect{fill:transparent!important;stroke:var(--md-default-fg-color--lighter)!important}",
      ".cluster span,.cluster-label{color:var(--md-default-fg-color)!important}",
      ".node rect,.node circle,.node ellipse,.node polygon,.node path{fill:var(--md-mermaid-node-bg-color)!important;stroke:var(--md-mermaid-node-fg-color)!important}",
      ".nodeLabel,.nodeLabel p,.label{color:var(--md-mermaid-label-fg-color)!important}",
      ".nodeLabel p,.nodeLabel{line-height:1.35!important}",
      "g.cluster[id$='-MAIN'] .cluster-label,g.cluster[id$='-REMOTE'] .cluster-label,g.cluster[id$='-CLOUD'] .cluster-label{font-weight:700!important;font-size:18px!important}",
      "g.cluster[id$='-MAIN'] .cluster-label span,g.cluster[id$='-REMOTE'] .cluster-label span,g.cluster[id$='-CLOUD'] .cluster-label span{font-weight:700!important;font-size:18px!important}",
      ".edgePath .path,.flowchart-link{stroke:var(--md-mermaid-edge-color)!important}",
      ".edge-pattern-dotted,path.edge-pattern-dotted,.flowchart-link.edge-pattern-dotted{stroke-dasharray:2 4!important;stroke-linecap:round!important}",
      ".edgeLabel,.edgeLabel p{background-color:var(--md-mermaid-label-bg-color)!important;color:var(--md-mermaid-edge-color)!important}",
      // Per-category node colors (Material renders Mermaid in a closed shadow root,
      // so these must live in themeCSS, not in the site stylesheet).
      ".node.baremetal rect,.node.baremetal circle,.node.baremetal ellipse,.node.baremetal polygon,.node.baremetal path{fill:var(--forbay-bm-fill)!important;stroke:var(--forbay-bm-stroke)!important}",
      ".node.baremetal .nodeLabel,.node.baremetal .nodeLabel p,.node.baremetal .label{color:var(--forbay-bm-text)!important}",
      ".node.vm rect,.node.vm circle,.node.vm ellipse,.node.vm polygon,.node.vm path{fill:var(--forbay-vm-fill)!important;stroke:var(--forbay-vm-stroke)!important}",
      ".node.vm .nodeLabel,.node.vm .nodeLabel p,.node.vm .label{color:var(--forbay-vm-text)!important}",
      ".node.lxc rect,.node.lxc circle,.node.lxc ellipse,.node.lxc polygon,.node.lxc path{fill:var(--forbay-lxc-fill)!important;stroke:var(--forbay-lxc-stroke)!important}",
      ".node.lxc .nodeLabel,.node.lxc .nodeLabel p,.node.lxc .label{color:var(--forbay-lxc-text)!important}",
      ".node.network rect,.node.network circle,.node.network ellipse,.node.network polygon,.node.network path{fill:var(--forbay-net-fill)!important;stroke:var(--forbay-net-stroke)!important}",
      ".node.network .nodeLabel,.node.network .nodeLabel p,.node.network .label{color:var(--forbay-net-text)!important}",
      // PVE host subgraphs = bare metal hosts.
      "g.cluster[id$='-PVE1'] rect,g.cluster[id$='-PVE2'] rect,g.cluster[id$='-PVE3'] rect,g.cluster[id$='-PVE4'] rect{fill:var(--forbay-bm-fill)!important;stroke:var(--forbay-bm-stroke)!important}",
      "g.cluster[id$='-PVE1'] .cluster-label,g.cluster[id$='-PVE2'] .cluster-label,g.cluster[id$='-PVE3'] .cluster-label,g.cluster[id$='-PVE4'] .cluster-label,g.cluster[id$='-PVE1'] span,g.cluster[id$='-PVE2'] span,g.cluster[id$='-PVE3'] span,g.cluster[id$='-PVE4'] span{color:var(--forbay-bm-text)!important}"
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
