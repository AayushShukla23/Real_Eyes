import { useRef, useState } from 'react';

const ALLOWED = ['mp4', 'avi', 'mov', 'mkv'];
const MAX_MB = 100;

export default function VideoUploader({ onFileSelect, disabled }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const validate = (selected) => {
    const ext = selected.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED.includes(ext)) {
      setError(`Only ${ALLOWED.join(', ').toUpperCase()} files are accepted.`);
      return false;
    }
    if (selected.size > MAX_MB * 1024 * 1024) {
      setError(`Max file size is ${MAX_MB}MB.`);
      return false;
    }
    setError('');
    return true;
  };

  const takeFile = (selected) => {
    if (!selected) return;
    if (!validate(selected)) return;
    setFile(selected);
    onFileSelect(selected);
  };

  const clear = () => {
    setFile(null);
    setError('');
    onFileSelect(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="w-full">
      {!file ? (
        <button
          type="button"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            takeFile(e.dataTransfer.files?.[0]);
          }}
          className={`w-full border-4 border-black bg-[#fffdf8] px-6 py-10 text-left shadow-[8px_8px_0_#000] transition ${
            dragOver ? 'translate-x-[2px] translate-y-[2px] shadow-[4px_4px_0_#000]' : ''
          } ${disabled ? 'opacity-50' : 'hover:bg-[#fff8e8]'}`}
        >
          <p className="mb-2 text-xs font-black uppercase tracking-[0.2em] text-[#5c564c]">
            Evidence Intake
          </p>
          <p className="mb-3 text-3xl font-black leading-none">Drop the video here</p>
          <p className="max-w-md text-sm font-medium text-[#5c564c]">
            Drag a clip in, or click to browse. We sample frames, extract spatial features,
            then run temporal classification.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {ALLOWED.map((ext) => (
              <span
                key={ext}
                className="border-2 border-black bg-[#e2a100] px-2 py-1 text-xs font-black uppercase"
              >
                {ext}
              </span>
            ))}
            <span className="border-2 border-black bg-white px-2 py-1 text-xs font-black uppercase">
              max {MAX_MB}mb
            </span>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={(e) => takeFile(e.target.files?.[0])}
          />
        </button>
      ) : (
        <div className="flex items-center justify-between gap-4 border-4 border-black bg-white p-4 shadow-[8px_8px_0_#000]">
          <div className="min-w-0">
            <p className="text-xs font-black uppercase tracking-[0.18em] text-[#5c564c]">
              Loaded Clip
            </p>
            <p className="truncate text-lg font-black">{file.name}</p>
            <p className="text-sm font-medium text-[#5c564c]">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
          {!disabled && (
            <button
              type="button"
              onClick={clear}
              className="border-2 border-black bg-[#f3efe6] px-3 py-2 text-xs font-black uppercase hover:bg-[#e2a100]"
            >
              Remove
            </button>
          )}
        </div>
      )}

      {error && (
        <div className="mt-3 border-4 border-black bg-[#c43c2d] px-4 py-3 text-sm font-bold text-white">
          {error}
        </div>
      )}
    </div>
  );
}