'use client';

import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface ChartData {
  labels: string[];
  data: number[];
}

interface DashboardChartProps {
  title: string;
  chartData: ChartData;
  chartType: 'line' | 'bar';
  chartId: string;
  colorClass?: string;
}

export default function DashboardChart({
  title,
  chartData,
  chartType,
  chartId,
  colorClass = 'rgb(59, 130, 246)' // 默认蓝色
}: DashboardChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 销毁旧图表实例
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // 创建新图表
    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: chartType,
      data: {
        labels: chartData.labels,
        datasets: [{
          label: title,
          data: chartData.data,
          fill: chartType === 'line' ? false : undefined,
          backgroundColor: chartType === 'line' ? undefined : colorClass,
          borderColor: chartType === 'line' ? colorClass : undefined,
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: title
          }
        }
      }
    });

    // 清理函数
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData, chartType, title, colorClass]);

  return (
    <div className="min-w-0 p-4 bg-white rounded-lg shadow-xs dark:bg-gray-800">
      <h4 className="mb-4 font-semibold text-gray-800 dark:text-gray-300">
        {title}
      </h4>
      <canvas id={chartId} ref={chartRef}></canvas>
    </div>
  );
}
