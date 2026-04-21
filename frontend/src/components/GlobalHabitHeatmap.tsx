import { useEffect, useState } from "react";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import { getAllHabitsHeatmap } from "../api";

interface Value {
  date: string;
  count: number;
}

interface Props {
  refreshKey?: number;
}

export default function GlobalHabitHeatmap({ refreshKey }: Props) {
  const [values, setValues] = useState<Value[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getAllHabitsHeatmap();
        setValues(data);
      } catch (err) {
        console.error("Global heatmap error:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [refreshKey]);

  if (loading) {
    return <p style={{ fontSize: "0.85rem", color: "#888" }}>Loading activity...</p>;
  }

  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 365);

  return (
    <div style={{ marginBottom: "25px" }}>
      <h3 style={{ marginBottom: "8px" }}>
        📊 All Habits Activity (Last 365 Days)
      </h3>
      <CalendarHeatmap
        startDate={startDate}
        endDate={endDate}
        values={values}
        classForValue={(value) => {
          if (!value || value.count === 0) return "color-empty";
          if (value.count === 1) return "color-scale-1";
          if (value.count === 2) return "color-scale-2";
          return "color-scale-3";
        }}
        tooltipDataAttrs={(value: any) => {
          if (!value || !value.date) return {};
          const date = new Date(value.date + 'T00:00:00').toLocaleDateString(
            'en-US',
            { month: 'short', day: 'numeric', year: 'numeric' }
          );
          return {
            "data-tip": `${date}: ${value.count ?? 0} ${value.count === 1 ? "log" : "logs"}`
          } as any;
        }}
        showWeekdayLabels
      />
    </div>
  );
}