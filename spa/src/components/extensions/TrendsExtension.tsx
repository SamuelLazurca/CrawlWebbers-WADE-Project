// // src/components/TrendsExtension.tsx
// import {
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   Tooltip,
//   ResponsiveContainer,
//   CartesianGrid,
// } from 'recharts';
// import type { TrendPoint } from '../../types';
//
// export const TrendsExtension = ({ data }: { data: TrendPoint[] }) => {
//   return (
//     <div className='p-6 bg-white rounded-xl shadow-md border border-slate-200'>
//       <h3 className='text-lg font-bold mb-6 text-slate-800'>
//         Trend Analysis & Distributions
//       </h3>
//       <div className='h-[300px] w-full'>
//         <ResponsiveContainer width='100%' height='100%'>
//           <BarChart data={data}>
//             <CartesianGrid strokeDasharray='3 3' vertical={false} />
//             <XAxis dataKey='label' />
//             <YAxis />
//             <Tooltip
//               contentStyle={{
//                 borderRadius: '8px',
//                 border: 'none',
//                 boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
//               }}
//             />
//             <Bar dataKey='count' fill='#6366f1' radius={[4, 4, 0, 0]} />
//           </BarChart>
//         </ResponsiveContainer>
//       </div>
//     </div>
//   );
// };
