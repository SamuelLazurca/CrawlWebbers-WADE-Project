import { useEffect, useState } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { useSidebarContext } from '../../context/sidebarContext';
import { getGraphData } from '../../lib/graph';
import { cn } from '../../lib/utils';
import type { GraphNode, GraphEdge } from '../../types';

export const ThreeDGraphVis = () => {
  const { baseDataset } = useSidebarContext();
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphEdge[] }>({
    nodes: [],
    links: [],
  });

  const startUri = baseDataset?.id === 'nist-nvd'
    ? 'https://nvd.nist.gov/vuln/detail/CVE-2021-44228'
    : 'https://www.imdb.com/title/tt0114709';

  useEffect(() => {
    async function loadGraph() {
      const res = await getGraphData(startUri);

      const nodes = res.nodes.map(n => ({ ...n, id: n.id }));
      const links = res.links.map(l => ({ ...l }));

      setGraphData({ nodes, links });
    }
    void loadGraph();
  }, [baseDataset, startUri]);

  return (
    <div className={cn(
      "rounded-2xl overflow-hidden border border-slate-700/50 h-150 bg-slate-950 relative",
      "shadow-2xl shadow-black/50"
    )}>
      <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700/50 p-3 rounded-xl text-xs text-slate-300 shadow-lg">
        <p className="font-semibold text-emerald-400 mb-1">Controls</p>
        <p>Left Click: Rotate</p>
        <p>Right Click: Pan</p>
        <p>Scroll: Zoom</p>
      </div>

      <ForceGraph3D
        graphData={graphData}
        nodeLabel="label"
        nodeAutoColorBy="group"
        backgroundColor="#020617"
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        nodeOpacity={0.9}
        linkOpacity={0.3}
        linkWidth={1}
      />
    </div>
  );
};
