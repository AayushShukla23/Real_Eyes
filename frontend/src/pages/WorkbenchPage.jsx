import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import VideoUploader from '../components/VideoUploader';
import LiveTerminal from '../components/LiveTerminal';
import ReportView from '../components/ReportView';
import { useVideoPrediction, STATES } from '../hooks/useVideoPrediction';
import { fetchReportById } from '../services/api';

export default function WorkbenchPage() {
  const { state, progress, result, error, analyze, reset } = useVideoPrediction();
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeReport, setActiveReport] = useState(null);

  const handleExecute = () => {
    if (selectedFile) {
      setActiveReport(null);
      analyze(selectedFile);
    }
  };

  const handleSelectReport = async (reportId) => {
    reset();
    setSelectedFile(null);
    try {
      const data = await fetchReportById(reportId);
      setActiveReport(data);
    } catch (err) {
      console.error('Failed to load report:', err);
    }
  };

  const handleNewAnalysis = () => {
    reset();
    setSelectedFile(null);
    setActiveReport(null);
  };

  const currentDisplayReport = result || activeReport;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        <Sidebar
          onSelectReport={handleSelectReport}
          onNewAnalysis={handleNewAnalysis}
          activeReportId={currentDisplayReport?.report_id}
        />

        <main className="flex-1 w-full space-y-6">
          {!currentDisplayReport && state === STATES.IDLE && (
            <div className="space-y-6">
              <VideoUploader onFileSelect={setSelectedFile} disabled={false} />
              <button
                type="button"
                onClick={handleExecute}
                disabled={!selectedFile}
                className={`w-full border-4 border-black px-4 py-4 text-sm font-black uppercase tracking-wide transition ${
                  selectedFile
                    ? 'bg-[#141414] text-white shadow-[6px_6px_0_#e2a100] hover:translate-x-[2px] hover:translate-y-[2px] cursor-pointer'
                    : 'bg-[#d9d3c5] text-[#7a7468] cursor-not-allowed'
                }`}
              >
                Execute Forensic Check
              </button>
            </div>
          )}

          {(state === STATES.UPLOADING || state === STATES.PROCESSING) && (
            <LiveTerminal progress={progress} state={state} />
          )}

          {currentDisplayReport && (
            <ReportView report={currentDisplayReport} onReset={handleNewAnalysis} />
          )}

          {state === STATES.ERROR && (
            <div className="border-4 border-black bg-[#c43c2d] p-5 text-sm font-bold text-white shadow-[8px_8px_0_#000] space-y-3">
              <p>{error}</p>
              <button
                type="button"
                onClick={handleNewAnalysis}
                className="border-2 border-black bg-white text-black px-3 py-1.5 text-xs font-black uppercase"
              >
                Reset Workbench
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}