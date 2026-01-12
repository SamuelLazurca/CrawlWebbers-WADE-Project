import { useEffect, useRef, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import ForceGraph3D from 'react-force-graph-3d';
import { useSidebarContext } from '../../context/sidebarContext';
import { getGraphData } from '../../lib/graph';
import { cn } from '../../lib/utils';
import { Focus, Box, Cuboid } from 'lucide-react';
import type { GraphEdge, GraphEmptyState, GraphNode } from '../../types';

export default function CombinedGraphVis() {
  const { baseDataset, currentView } = useSidebarContext();
  const containerRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  const [is3D, setIs3D] = useState<boolean>(false);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphEdge[] }>({
    nodes: [],
    links: [],
  });

  // Explicit dimensions state to fix centering issues
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const startUri = currentView?.example_resource ?? baseDataset?.example_resource ?? '';

  const graphState: GraphEmptyState = !baseDataset
    ? { kind: 'no-dataset' }
    : startUri === ''
      ? { kind: 'missing-start-uri' }
      : { kind: 'ready', startUri };

  // 1. Measure container size on mount and resize
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });

        // Re-center when dimensions change significantly (e.g. sidebar toggle)
        if (fgRef.current) {
          // Small timeout to allow render cycle to finish
          setTimeout(() => {
            if (is3D) {
              fgRef.current.cameraPosition({ x: 0, y: 0, z: 300 }, { x: 0, y: 0, z: 0 }, 500);
            } else {
              fgRef.current.zoomToFit(400, 50);
            }
          }, 100);
        }
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, [is3D]); // Re-run if mode changes to ensure ref is attached

  // 2. Load Data
  useEffect(() => {
    if (graphState.kind !== 'ready') return;

    async function loadGraph() {
      const res = await getGraphData(startUri, currentView?.id);

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
  }, [baseDataset, currentView, graphState.kind, startUri]);

  // 3. Robust Reset/Center Logic
  const handleResetCamera = useCallback(() => {
    if (!fgRef.current) return;

    if (is3D) {
      fgRef.current.cameraPosition(
        { x: 0, y: 0, z: 300 },
        { x: 0, y: 0, z: 0 },
        1000
      );
    } else {
      fgRef.current.zoomToFit(400, 50);
      // For 2D, sometimes we also need to reset the center strictly
      fgRef.current.centerAt(0, 0, 1000);
    }
  }, [is3D]);

  // 4. Handle Node Click (Centering)
  const handleNodeClick = async (node: GraphNode) => {
    try {
      if (fgRef.current) {
        if (is3D) {
          const dist = 150;
          const distRatio = 1 + dist/Math.hypot(node.x || 1, node.y || 1, node.z || 1);
          fgRef.current.cameraPosition(
            { x: (node.x || 0) * distRatio, y: (node.y || 0) * distRatio, z: (node.z || 0) * distRatio },
            { x: node.x, y: node.y, z: node.z },
            1000
          );
        } else {
          // 2D Centering: animate coordinates
          fgRef.current.centerAt(node.x, node.y, 1000);
          fgRef.current.zoom(2, 1000);
        }
      }

      console.log('Expanding node:', node.id);
      const res = await getGraphData(node.id, currentView?.id);

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

  const renderEmptyState = () => {
    if (graphState.kind === 'ready') return null;
    const message = graphState.kind === 'no-dataset'
      ? { title: 'No dataset selected', body: 'Please select a dataset to explore its graph.' }
      : { title: 'Graph unavailable', body: 'The selected view does not define a starting resource.' };

    return (
      <div className="absolute inset-0 z-20 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm">
        <div className="max-w-md text-center p-6 rounded-xl border border-slate-700 bg-slate-900 shadow-xl">
          <h3 className="text-lg font-semibold text-amber-400 mb-2">{message.title}</h3>
          <p className="text-sm text-slate-300">{message.body}</p>
        </div>
      </div>
    );
  };

  return (
    <div
      ref={containerRef} // Attach ref here to measure this div
      className={cn(
        'rounded-2xl overflow-hidden border border-slate-700/50 h-96 bg-slate-900 relative',
        'shadow-2xl shadow-black/50'
      )}
    >
      <div className="absolute top-4 right-4 z-30 flex flex-col gap-2">
        <button
          onClick={() => setIs3D(prev => !prev)}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600 text-slate-100 shadow backdrop-blur transition-all"
          title={is3D ? 'Switch to 2D' : 'Switch to 3D'}
        >
          {is3D ? <Box size={20} /> : <Cuboid size={20} />}
        </button>
        <button
          onClick={handleResetCamera}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-600 text-slate-100 shadow backdrop-blur transition-all"
          title="Recenter Graph"
        >
          <Focus size={20} />
        </button>
      </div>

      {renderEmptyState()}

      {graphState.kind === 'ready' && dimensions.width > 0 && (
        is3D ? (
          <ForceGraph3D
            ref={fgRef}
            width={dimensions.width}   // Explicit Width
            height={dimensions.height} // Explicit Height
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
            cooldownTicks={100}
            onEngineStop={() => {
              // Initial Center
              fgRef.current?.cameraPosition({ x: 0, y: 0, z: 300 }, { x: 0, y: 0, z: 0 }, 100);
            }}
          />
        ) : (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}   // Explicit Width
            height={dimensions.height} // Explicit Height
            graphData={graphData}
            nodeLabel="label"
            nodeAutoColorBy="group"
            onNodeClick={handleNodeClick}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            backgroundColor="#0f172a"
            cooldownTicks={100}
            onEngineStop={() => {
              // Initial Center
              fgRef.current?.zoomToFit(400, 50);
            }}
          />
        )
      )}
    </div>
  );
}
