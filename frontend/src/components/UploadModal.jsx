import React, { useState } from "react";
import { X, UploadCloud, FileText, Database, Phone, Activity } from "lucide-react";
import * as api from "../services/api";

export default function UploadModal({ isOpen, onClose, onRefresh }) {
  const [firs, setFirs] = useState([]);
  const [cdr, setCdr] = useState(null);
  const [transactions, setTxns] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const handleFirs = (e) => setFirs([...e.target.files]);
  const handleCdr = (e) => setCdr(e.target.files[0]);
  const handleTxns = (e) => setTxns(e.target.files[0]);

  const handleUpload = async () => {
    if (!firs.length && !cdr && !transactions) {
      setStatusMsg("⚠️ Select at least one file before uploading.");
      return;
    }

    const form = new FormData();
    firs.forEach((f) => form.append("firs", f));
    if (cdr) form.append("cdr", cdr);
    if (transactions) form.append("transactions", transactions);

    try {
      setLoading(true);
      setStatusMsg("🔄 Uploading and processing...");

      const res = await api.default.post("/api/upload/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setStatusMsg("✅ " + res.data.message);

      // Clear the form
      setFirs([]);
      setCdr(null);
      setTxns(null);

      // Refresh the dashboard
      setTimeout(() => {
        onRefresh && onRefresh();
        onClose();
      }, 1000);
    } catch (e) {
      console.error(e);
      let errorDetail = e.response?.data?.detail || e.message || "Upload failed – see console for details.";
      if (typeof errorDetail === "object") {
        if (Array.isArray(errorDetail)) {
          errorDetail = errorDetail.map(err => err.msg || JSON.stringify(err)).join(", ");
        } else {
          errorDetail = errorDetail.msg || JSON.stringify(errorDetail);
        }
      }
      setStatusMsg("❌ " + errorDetail);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0, 0, 0, 0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        style={{
          background: "#131b2c",
          border: "1px solid #2e3c54",
          borderRadius: 12,
          padding: 24,
          width: "90%",
          maxWidth: 500,
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.8)",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 20,
          }}
        >
          <h3 style={{ color: "#e2e8f0", margin: 0, fontSize: "1.2rem", display: "flex", alignItems: "center", gap: 10 }}>
            <UploadCloud size={24} color="#00f0ff" /> Upload Evidence
          </h3>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              color: "#94a3b8",
              padding: 0,
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {/* FIRs */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: 16,
                background: "#1b263b",
                border: "2px dashed #2e3c54",
                borderRadius: 8,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#00f0ff";
                e.currentTarget.style.background = "rgba(0, 240, 255, 0.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#2e3c54";
                e.currentTarget.style.background = "#1b263b";
              }}
            >
              <FileText size={20} color="#3b82f6" />
              <span style={{ color: "#e2e8f0", fontSize: "0.95rem" }}>
                FIR / Case Diary (*.txt / *.pdf) – Drop multiple files
              </span>
              <input
                type="file"
                accept=".txt,.pdf"
                multiple
                onChange={handleFirs}
                style={{ display: "none" }}
              />
            </label>
            {firs.length > 0 && (
              <p style={{ color: "#10b981", fontSize: "0.85rem", margin: 0, paddingLeft: 4 }}>
                ✓ {firs.length} FIR file(s) selected
              </p>
            )}
          </div>

          {/* CDR */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: 16,
                background: "#1b263b",
                border: "2px dashed #2e3c54",
                borderRadius: 8,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#06b6d4";
                e.currentTarget.style.background = "rgba(6, 182, 212, 0.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#2e3c54";
                e.currentTarget.style.background = "#1b263b";
              }}
            >
              <Phone size={20} color="#06b6d4" />
              <span style={{ color: "#e2e8f0", fontSize: "0.95rem" }}>
                Call Detail Record (*.csv)
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleCdr}
                style={{ display: "none" }}
              />
            </label>
            {cdr && (
              <p style={{ color: "#10b981", fontSize: "0.85rem", margin: 0, paddingLeft: 4 }}>
                ✓ {cdr.name} selected
              </p>
            )}
          </div>

          {/* Transactions */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <label
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: 16,
                background: "#1b263b",
                border: "2px dashed #2e3c54",
                borderRadius: 8,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#10b981";
                e.currentTarget.style.background = "rgba(16, 185, 129, 0.05)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#2e3c54";
                e.currentTarget.style.background = "#1b263b";
              }}
            >
              <Database size={20} color="#10b981" />
              <span style={{ color: "#e2e8f0", fontSize: "0.95rem" }}>
                Financial Transactions (*.csv)
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleTxns}
                style={{ display: "none" }}
              />
            </label>
            {transactions && (
              <p style={{ color: "#10b981", fontSize: "0.85rem", margin: 0, paddingLeft: 4 }}>
                ✓ {transactions.name} selected
              </p>
            )}
          </div>

          {/* Status Message */}
          {statusMsg && (
            <div
              style={{
                padding: 12,
                background: statusMsg.includes("❌") ? "rgba(239, 68, 68, 0.1)" : "rgba(16, 185, 129, 0.1)",
                border: statusMsg.includes("❌") ? "1px solid #ef4444" : "1px solid #10b981",
                borderRadius: 6,
                color: statusMsg.includes("❌") ? "#ef4444" : "#10b981",
                fontSize: "0.85rem",
              }}
            >
              {statusMsg}
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            display: "flex",
            gap: 12,
            marginTop: 24,
            justifyContent: "flex-end",
          }}
        >
          <button
            onClick={onClose}
            disabled={loading}
            style={{
              background: "#1e293b",
              border: "1px solid #334155",
              color: "#e2e8f0",
              padding: "10px 20px",
              borderRadius: 6,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.5 : 1,
            }}
          >
            Cancel
          </button>

          <button
            onClick={handleUpload}
            disabled={loading}
            style={{
              background: "#3b82f6",
              border: "none",
              color: "#fff",
              padding: "10px 20px",
              borderRadius: 6,
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: "0.95rem",
              fontWeight: 500,
            }}
          >
            {loading ? <Activity size={16} className="animate-spin" /> : <UploadCloud size={16} />}
            {loading ? "Processing..." : "Start Ingestion"}
          </button>
        </div>
      </div>
    </div>
  );
}
