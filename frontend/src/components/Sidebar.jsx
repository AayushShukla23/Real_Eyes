import { useEffect, useState } from 'react';
import { fetchRecentReports, seedSampleReports } from '../services/api';

export default function Sidebar({ onSelectReport, onNewAnalysis, activeReportId }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      let data = await fetchRecentReports();
      if (!data || data.length === 0) {
        await seedSampleReports();
        data = await fetchRecentReports();
      }
      setReports(data || []);
    } catch (err) {
      console.error('Failed to load reports from MongoDB:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [activeReportId]);

  return (
    <aside className="w-full lg:w-80 border-4 border-black bg-[#fffdf8] p-4 shadow-[6px_6px_0_#000] flex flex-col justify-between">
      <div>
        <button
          type="button"
          onClick={onNewAnalysis}
          className="w-full border-4 border-black bg-[#e2a100] px-4 py-3 text-xs font-black uppercase tracking-wider shadow-[4px_4px_0_#000] hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0_#000] transition cursor-pointer mb-6"
        >
          + New Video Analysis
        </button>

        <div className="flex items-center justify-between mb-3 border-b-2 border-black pb-2">
          <span className="text-xs font-black uppercase tracking-[0.15em] text-[#5c564c]">
            MongoDB Atlas History
          </span>
          <button
            type="button"
            onClick={loadHistory}
            className="text-[10px] font-bold uppercase underline hover:text-[#e2a100]"
          >
            Refresh
          </button>
        </div>

        {loading ? (
          <p className="text-xs font-bold text-[#5c564c] py-4">Querying database...</p>
        ) : reports.length === 0 ? (
          <p className="text-xs font-medium text-[#5c564c] py-4">No reports recorded yet.</p>
        ) : (
          <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            {reports.map((rep) => {
              const isFake = rep.prediction === 'FAKE';
              const isSelected = activeReportId === rep.report_id;

              return (
                <button
                  key={rep.report_id}
                  type="button"
                  onClick={() => onSelectReport(rep.report_id)}
                  className={`w-full text-left border-2 border-black p-2.5 transition flex items-center justify-between cursor-pointer ${
                    isSelected
                      ? 'bg-[#141414] text-white shadow-[3px_3px_0_#e2a100]'
                      : 'bg-white hover:bg-[#fff8e8]'
                  }`}
                >
                  <div className="min-w-0 pr-2">
                    <p className="text-xs font-black truncate">{rep.filename}</p>
                    <p className="text-[10px] opacity-70 font-mono mt-0.5">{rep.report_id}</p>
                  </div>
                  <span
                    className={`text-[10px] font-black px-2 py-0.5 border border-black uppercase shrink-0 ${
                      isFake
                        ? 'bg-[#c43c2d] text-white'
                        : 'bg-[#1f6b4a] text-white'
                    }`}
                  >
                    {rep.prediction}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-6 pt-3 border-t-2 border-black text-[10px] font-mono font-bold text-[#5c564c] flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span>MongoDB Atlas Stream Online</span>
      </div>
    </aside>
  );
}