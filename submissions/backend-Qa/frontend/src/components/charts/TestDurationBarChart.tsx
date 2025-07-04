
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

interface DurationData {
  name: string;
  min: number;
  avg: number;
  max: number;
}

interface TestDurationBarChartProps {
  data: DurationData[];
}

const TestDurationBarChart: React.FC<TestDurationBarChartProps> = ({ data }) => {
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
        <Tooltip formatter={(value: number) => [`${value} seconds`, '']} />
        <Legend />
        <Bar dataKey="min" name="Min Duration" fill="#3b82f6" />
        <Bar dataKey="avg" name="Avg Duration" fill="#10b981" />
        <Bar dataKey="max" name="Max Duration" fill="#f97316" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default TestDurationBarChart;
