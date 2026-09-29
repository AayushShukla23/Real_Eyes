export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 space-y-8">
      <div className="border-4 border-black bg-[#fffdf8] p-8 shadow-[10px_10px_0_#000] space-y-4">
        <h1 className="text-4xl font-black">About RealEyes</h1>
        <p className="text-sm font-medium text-[#5c564c] leading-relaxed">
          Developed as a defensible portfolio project for AI/ML and full-stack software engineering technical interviews.
        </p>
        <div className="pt-4 border-t-2 border-black flex items-center justify-between text-xs font-bold">
          <span>Stack: FastAPI • TensorFlow • React • Tailwind • MongoDB Atlas</span>
          <a
            href="https://github.com/AayushShukla1438/RealEyes"
            target="_blank"
            rel="noreferrer"
            className="underline hover:text-[#e2a100]"
          >
            GitHub Repository
          </a>
        </div>
      </div>
    </div>
  );
}