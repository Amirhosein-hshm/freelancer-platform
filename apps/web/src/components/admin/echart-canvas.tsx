'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface EChartCanvasProps {
  options: echarts.EChartsOption;
  height?: number | string;
  className?: string;
}

export function EChartCanvas({ options, height = 320, className = '' }: EChartCanvasProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Detect dark mode from root html element
    const isDark = document.documentElement.classList.contains('dark');
    
    // Initialize chart
    const instance = echarts.init(chartRef.current, isDark ? 'dark' : undefined, {
      renderer: 'svg',
    });
    chartInstance.current = instance;
    instance.setOption({
      backgroundColor: 'transparent',
      ...options,
    });

    // Resize listener
    const resizeObserver = new ResizeObserver(() => {
      instance.resize();
    });
    resizeObserver.observe(chartRef.current);

    // Dark mode observer
    const themeObserver = new MutationObserver(() => {
      if (!chartRef.current) return;
      const nextDark = document.documentElement.classList.contains('dark');
      instance.dispose();
      const nextInstance = echarts.init(chartRef.current, nextDark ? 'dark' : undefined, {
        renderer: 'svg',
      });
      chartInstance.current = nextInstance;
      nextInstance.setOption({
        backgroundColor: 'transparent',
        ...options,
      });
    });
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => {
      resizeObserver.disconnect();
      themeObserver.disconnect();
      instance.dispose();
      chartInstance.current = null;
    };
  }, [options]);

  return (
    <div
      ref={chartRef}
      style={{ height, width: '100%' }}
      className={className}
      dir="ltr"
    />
  );
}
