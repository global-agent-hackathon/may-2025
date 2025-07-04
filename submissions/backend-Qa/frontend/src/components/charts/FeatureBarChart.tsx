
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface FeatureData {
  name: string;
  passed: number;
  failed: number;
  skipped: number;
}

interface FeatureBarChartProps {
  data: FeatureData[];
}

const FeatureBarChart: React.FC<FeatureBarChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={data}
        margin={{
          top: 20,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="passed" stackId="a" fill="#4ade80" />
        <Bar dataKey="failed" stackId="a" fill="#f87171" />
        <Bar dataKey="skipped" stackId="a" fill="#94a3b8" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default FeatureBarChart;
