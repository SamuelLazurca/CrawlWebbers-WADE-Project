// import type { Concept, FilterFacet, ChartData, GraphNode, GraphEdge } from '../types';
//
// export const mockConcepts: Concept[] = [
//   {
//     uri: 'http://dbpedia.org/resource/Artificial_intelligence',
//     label: 'Artificial Intelligence',
//     definition: 'Intelligence demonstrated by machines',
//     category: 'Technology',
//     relatedCount: 342,
//     color: '#0ea5e9',
//   },
//   {
//     uri: 'http://dbpedia.org/resource/Machine_learning',
//     label: 'Machine Learning',
//     definition: 'Subset of AI focused on learning',
//     category: 'Technology',
//     relatedCount: 285,
//     color: '#06b6d4',
//   },
//   {
//     uri: 'http://dbpedia.org/resource/Deep_learning',
//     label: 'Deep Learning',
//     definition: 'ML using neural networks',
//     category: 'Technology',
//     relatedCount: 198,
//     color: '#10b981',
//   },
//   {
//     uri: 'http://dbpedia.org/resource/Data_science',
//     label: 'Data Science',
//     definition: 'Interdisciplinary field using data',
//     category: 'Technology',
//     relatedCount: 276,
//     color: '#f59e0b',
//   },
//   {
//     uri: 'http://dbpedia.org/resource/Knowledge_graph',
//     label: 'Knowledge Graph',
//     definition: 'Structured representation of knowledge',
//     category: 'Semantic Web',
//     relatedCount: 165,
//     color: '#ec4899',
//   },
// ];
//
// export const mockFilterFacets: FilterFacet[] = [
//   {
//     property: 'Category',
//     values: [
//       { label: 'Technology', count: 2341 },
//       { label: 'Semantic Web', count: 1824 },
//       { label: 'Data Science', count: 1456 },
//       { label: 'Business', count: 892 },
//     ],
//     isExpanded: true,
//   },
//   {
//     property: 'Status',
//     values: [
//       { label: 'Active', count: 4200 },
//       { label: 'Deprecated', count: 342 },
//       { label: 'Proposed', count: 156 },
//     ],
//     isExpanded: true,
//   },
//   {
//     property: 'Language',
//     values: [
//       { label: 'English', count: 3892 },
//       { label: 'German', count: 2341 },
//       { label: 'French', count: 1823 },
//       { label: 'Spanish', count: 1456 },
//     ],
//     isExpanded: false,
//   },
//   {
//     property: 'Creation Date',
//     values: [
//       { label: '2024', count: 1823 },
//       { label: '2023', count: 2456 },
//       { label: '2022', count: 1892 },
//       { label: 'Earlier', count: 1456 },
//     ],
//     isExpanded: false,
//   },
// ];
//
// export const mockChartData: ChartData[] = [
//   { label: 'Technology', value: 2341, percentage: 32, trend: 'up' },
//   { label: 'Business', value: 1892, percentage: 26, trend: 'stable' },
//   { label: 'Science', value: 1456, percentage: 20, trend: 'up' },
//   { label: 'Arts', value: 892, percentage: 12, trend: 'down' },
//   { label: 'Other', value: 615, percentage: 10, trend: 'stable' },
// ];
//
// export const mockGraphData = {
//   nodes: [
//     { id: 'ai', label: 'AI', color: '#0ea5e9' },
//     { id: 'ml', label: 'ML', color: '#06b6d4' },
//     { id: 'dl', label: 'Deep Learning', color: '#10b981' },
//     { id: 'nlp', label: 'NLP', color: '#f59e0b' },
//     { id: 'cv', label: 'Computer Vision', color: '#ec4899' },
//     { id: 'kg', label: 'Knowledge Graphs', color: '#8b5cf6' },
//   ],
//   edges: [
//     { source: 'ai', target: 'ml' },
//     { source: 'ml', target: 'dl' },
//     { source: 'ml', target: 'nlp' },
//     { source: 'ml', target: 'cv' },
//     { source: 'ai', target: 'kg' },
//     { source: 'dl', target: 'cv' },
//   ],
// };
//
// export const mockTrendData = [
//   { date: 'Jan 1', value: 340, volume: 240 },
//   { date: 'Jan 5', value: 420, volume: 340 },
//   { date: 'Jan 10', value: 380, volume: 280 },
//   { date: 'Jan 15', value: 520, volume: 420 },
//   { date: 'Jan 20', value: 680, volume: 540 },
//   { date: 'Jan 25', value: 750, volume: 620 },
// ];
