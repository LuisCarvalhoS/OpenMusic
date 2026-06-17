"use client";

import {
  Download,
  FolderOpen,
  Folder,
  Link2,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { useState } from "react";

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [url, setUrl] = useState("");
  const [downloadDir, setDownloadDir] = useState("");
  const [editingDir, setEditingDir] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({
    type: "idle",
    message: "Selecione um diretório de download",
  });

  const handleDownload = async () => {
    if (!url.trim()) {
      setStatus({ type: "error", message: "Cole um link do YouTube" });
      return;
    }
    setLoading(true);
    setStatus({ type: "loading", message: "Baixando..." });
    try {
      const res = await fetch(`${API_BASE}/api/audio/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url.trim(),
          download_dir: downloadDir || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erro ao baixar");
      setStatus({
        type: "success",
        message: `Concluído — ${data.title}`,
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro desconhecido";
      setStatus({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenFolder = async () => {
    try {
      const path = downloadDir || ".";
      const res = await fetch(`${API_BASE}/api/audio/open-folder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Erro ao abrir pasta");
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Erro desconhecido";
      setStatus({ type: "error", message });
    }
  };

  const handleSaveDir = () => {
    setEditingDir(false);
    setStatus({
      type: "idle",
      message: downloadDir
        ? `Diretório: ${downloadDir}`
        : "Selecione um diretório de download",
    });
  };

  const statusColors = {
    idle: "text-gray-400",
    loading: "text-emerald-400",
    success: "text-emerald-400",
    error: "text-red-400",
  };

  const dotColors = {
    idle: "bg-emerald-400",
    loading: "bg-emerald-400 animate-pulse",
    success: "bg-emerald-400",
    error: "bg-red-400",
  };

  return (
    <main className="min-h-screen bg-[#020b08] text-white flex items-center justify-center px-4">
      <div className="w-full max-w-3xl flex flex-col items-center animate-[fadeIn_0.5s_ease]">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-center">
          <span className="text-gray-300">Open</span>{" "}
          <span className="text-emerald-400">Music</span>
        </h1>

        <p className="mt-4 text-gray-400 text-xl md:text-2xl font-mono text-center">
          Youtube to max <span className="text-emerald-400 font-semibold">wav</span> quality
        </p>

        <p className="mt-4 text-gray-500 text-lg md:text-xl font-mono text-center">
          <span className="text-emerald-400 font-semibold">WAV</span> 48kHz · PCM 24-bit · Stereo
        </p>

        <div className="w-full mt-12">
          <div className="relative">
            <Link2
              size={18}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-400"
            />
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleDownload()}
              placeholder='Cole o link do YouTube... "https://youtu.be/..."'
              className="w-full h-16 pl-12 pr-4 rounded-xl bg-[#0c1714] border border-emerald-900/40 text-gray-300 placeholder:text-gray-500 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition"
            />
          </div>

          {editingDir && (
            <div className="relative mt-3">
              <Folder
                size={18}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-400"
              />
              <input
                value={downloadDir}
                onChange={(e) => setDownloadDir(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSaveDir()}
                placeholder="Caminho do diretório de download..."
                autoFocus
                className="w-full h-14 pl-12 pr-4 rounded-xl bg-[#0c1714] border border-emerald-900/40 text-gray-300 placeholder:text-gray-500 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition"
              />
              <button
                onClick={handleSaveDir}
                className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-4 rounded-lg bg-emerald-700 hover:bg-emerald-600 transition text-sm font-semibold"
              >
                Salvar
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-5">
            <button
              onClick={handleDownload}
              disabled={loading}
              className="h-14 rounded-xl bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 font-semibold"
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Download size={18} />
              )}
              {loading ? "Baixando..." : "Baixar"}
            </button>

            <button
              onClick={() => setEditingDir(!editingDir)}
              className="h-14 rounded-xl bg-[#0c1714] border border-emerald-900/40 hover:border-emerald-600 transition flex items-center justify-center gap-2"
            >
              <Folder size={18} />
              Diretório
            </button>

            <button
              onClick={handleOpenFolder}
              className="h-14 rounded-xl bg-[#0c1714] border border-emerald-900/40 hover:border-emerald-600 transition flex items-center justify-center gap-2"
            >
              <FolderOpen size={18} />
              Abrir pasta
            </button>
          </div>

          <div
            className={`flex items-center justify-center gap-2 mt-6 text-sm font-mono ${statusColors[status.type]}`}
          >
            {status.type === "success" ? (
              <CheckCircle2 size={16} />
            ) : status.type === "error" ? (
              <XCircle size={16} />
            ) : (
              <span className={`w-2 h-2 rounded-full ${dotColors[status.type]}`} />
            )}
            {status.message}
          </div>
        </div>
      </div>
    </main>
  );
}
