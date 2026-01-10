import {useEffect, useState} from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import {useSidebarContext} from '../../context/sidebarContext';
import {getGraphData} from '../../lib/graph';
import {cn} from '../../lib/utils';
import type {GraphEdge, GraphNode} from '../../types';

export const GraphVis = () => {
  const { baseDataset } = useSidebarContext();
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphEdge[] }>({
    nodes: [],
    links: [],
  });

  // Default URIs for demo purposes if dataset is selected
  const startUri = baseDataset?.id === 'nist-nvd'
    ? 'https://nvd.nist.gov/vuln/detail/CVE-2021-44228' // Log4j
    : 'https://www.imdb.com/title/tt0114709'; // Toy Story

  useEffect(() => {
    async function loadGraph() {
      const res = await getGraphData(startUri);

      const nodes = res.nodes.map(n => ({
        id: n.id,
        label: n.label,
        group: n.group,
        value: n.value
      }));

      const links = res.links.map(l => ({
        source: l.source,
        target: l.target,
        relationship: l.relationship,
        weight: l.weight
      }));

      setGraphData({ nodes, links });
    }

    void loadGraph();
  }, [baseDataset, startUri]);

  const handleNodeClick = async (node: any) => { // 'node' type is internal to ForceGraph
    console.log("Expanding node:", node.id);
    const res = await getGraphData(node.id);

    setGraphData(prev => {
      const existingNodeIds = new Set(prev.nodes.map(n => n.id));
      const newNodes = res.nodes.filter(n => !existingNodeIds.has(n.id));

      return {
        nodes: [...prev.nodes, ...newNodes],
        links: [...prev.links, ...res.links]
      };
    });
  };

  return (
    <div className={cn(
      "rounded-2xl overflow-hidden border border-slate-700/50 h-96 bg-slate-900",
      "shadow-inner shadow-slate-950/50"
    )}>
      <ForceGraph2D
        graphData={graphData}
        nodeLabel="label"
        nodeAutoColorBy="group"
        onNodeClick={handleNodeClick}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        backgroundColor="#0f172a" // Matches slate-900
      />
    </div>
  );
};
