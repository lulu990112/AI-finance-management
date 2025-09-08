import React, { useState, useEffect } from "react";
import { getAIReportList } from "../services/api";

export default function AbnormalAlert() {
  const [alertData, setAlertData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAlertData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🚨 Start fetching abnormal alert data...');
        // Use report list API, get first page data, take the first (latest) report
        const response = await getAIReportList(1, 1);
        
        if (response && response.reports && response.reports.length > 0) {
          const latestReport = response.reports[0];
          console.log('✅ Successfully got latest report:', latestReport);
          
          if (latestReport.abnormal_alert) {
            setAlertData(latestReport.abnormal_alert);
          } else {
            console.log('⚠️ No abnormal alert data in latest report');
            setAlertData(null);
          }
        } else {
          console.log('⚠️ Report data not found, using default content');
          setAlertData(null);
        }
      } catch (err) {
        console.error('❌ Failed to get abnormal alert:', err);
        if (err.message && err.message.includes('Authentication failed')) {
          setError('Authentication failed, please login again');
        } else {
          setError('Failed to get abnormal alert');
        }
        setAlertData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAlertData();
  }, []);

  // Default content
  const defaultAlert = "A $200 overseas transaction has been detected, which is inconsistent with your usual spending habits. Please confirm if this was made by you.";

  return (
    <div style={{
      background: "#fff",
      borderRadius: 10,
      padding: "18px 24px",
      marginBottom: 16,
      boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
      fontSize: 15,
      border: "1px solid #eee"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600, fontSize: 16, marginBottom: 6 }}>
        <span role="img" aria-label="alert">🔒</span> Abnormal Spending Alert
        {loading && <span style={{ fontSize: 12, color: "#666", marginLeft: 8 }}>(Loading...)</span>}
      </div>
      <div style={{ color: "#444" }}>
        {loading ? (
                      <div style={{ color: "#666", fontStyle: "italic" }}>Loading...</div>
        ) : error ? (
          <div style={{ color: "#ff4d4f" }}>{error}</div>
        ) : alertData ? (
          alertData
        ) : (
          defaultAlert
        )}
      </div>
      <a href="/ai-report" style={{
        display: "inline-block",
        marginTop: 12,
        background: "#faad14",
        color: "#fff",
        borderRadius: 6,
        padding: "6px 18px",
        fontWeight: 600,
        fontSize: 15,
        textDecoration: "none",
        boxShadow: "0 1px 4px #ffe08f",
        transition: "background 0.2s"
      }}>View Details</a>
    </div>
  );
} 