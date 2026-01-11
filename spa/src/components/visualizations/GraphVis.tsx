import {useEffect, useState} from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import ForceGraph3D from 'react-force-graph-3d';
import {useSidebarContext} from '../../context/sidebarContext';
import {getGraphData} from '../../lib/graph';
import {cn} from '../../lib/utils';
import type {GraphEdge, GraphNode} from '../../types';

export default function CombinedGraphVis() {
  const { baseDataset } = useSidebarContext();
  const [is3D, setIs3D] = useState<boolean>(false);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphEdge[] }>({
    nodes: [],
    links: [],
  });
  const startUri = baseDataset?.id === 'nist-nvd'
    ? 'https://nvd.nist.gov/vuln/detail/CVE-1999-0199'
    : 'https://www.imdb.com/title/tt0114709';

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

  const handleNodeClick = async (node: GraphNode) => {
    try {
      console.log('Expanding node:', node.id);
      const res = await getGraphData(node.id);

      setGraphData(prev => {
        const existingNodeIds = new Set(prev.nodes.map(n => n.id));
        const newNodes = res.nodes
          .map(n => ({ id: n.id, label: n.label, group: n.group, value: n.value }))
          .filter(n => !existingNodeIds.has(n.id));

        const mergedLinks = [...prev.links, ...res.links.map(l => ({
          source: l.source,
          target: l.target,
          relationship: l.relationship,
          weight: l.weight
        }))];

        return {
          nodes: [...prev.nodes, ...newNodes],
          links: mergedLinks,
        };
      });
    } catch (err) {
      console.error('Failed to expand node', err);
    }
  };

  return (
    <div className={cn(
      'rounded-2xl overflow-hidden border border-slate-700/50 h-150 bg-slate-900 relative',
      'shadow-2xl shadow-black/50'
    )}>
      {is3D && (
      <div className="absolute top-4 left-4 z-20 bg-slate-900/90 backdrop-blur border border-slate-700/50 p-3 rounded-xl text-xs text-slate-300 shadow-lg">
        <p className="font-semibold text-emerald-400 mb-1">Controls</p>
        <p>Left Click: Rotate</p>
        <p>Right Click: Pan</p>
        <p>Scroll: Zoom</p>
      </div>
      )}

      <div className="absolute top-4 right-4 z-30 p-2">
        <button
          onClick={() => setIs3D(prev => !prev)}
          className="px-3 py-1 rounded-lg text-sm font-medium bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600 text-slate-100 shadow"
          aria-pressed={is3D}
        >
          {is3D ? 'Switch to 2D' : 'Switch to 3D'}
        </button>
      </div>

      {is3D ? (
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
          onNodeClick={handleNodeClick}
        />
      ) : (
        <ForceGraph2D
          graphData={graphData}
          nodeLabel="label"
          nodeAutoColorBy="group"
          onNodeClick={handleNodeClick}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          backgroundColor="#0f172a"
        />
      )}
    </div>
  );
}
