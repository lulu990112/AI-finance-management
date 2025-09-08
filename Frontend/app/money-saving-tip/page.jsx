"use client";
import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { getAIReportList } from "../services/api";
import { FaArrowLeft, FaLightbulb, FaChartLine } from "react-icons/fa";

export default function MoneySavingTipPage() {
  const [aiReport, setAiReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMoneySavingTip = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('💡 Starting to fetch latest Money Saving Tip data...');
      // Get latest AI Report (first page, first report)
      const reportResponse = await getAIReportList(1, 1);
      
      if (reportResponse && reportResponse.reports && reportResponse.reports.length > 0) {
        const latestReport = reportResponse.reports[0];
        console.log('✅ Successfully got latest AI Report:', latestReport);
        console.log('💡 Money Saving Tip:', latestReport.money_saving_tip);
        setAiReport(latestReport);
      } else {
        console.log('⚠️ No latest AI Report data found');
        setAiReport(null);
      }
    } catch (err) {
      console.error('❌ Failed to get Money Saving Tip:', err);
      setError('Failed to get Money Saving Tip');
      setAiReport(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoneySavingTip();
  }, []);

  // Default content
  const defaultTip = "To save money while still enjoying entertainment, consider exploring alternative and cost-effective activities such as outdoor picnics, movie nights at home, or utilizing subscription services for music and movies. Setting a monthly entertainment budget can also help in managing expenses and prioritizing savings goals.";

  return (
    <div style={{ background: "#f7fafd", minHeight: "100vh", fontFamily: 'PingFang SC, Segoe UI, Arial, sans-serif' }}>
      <Navbar />
      <div style={{ maxWidth: 800, margin: "0 auto", padding: "32px 16px 48px 16px" }}>
        {/* Back button */}
        <div style={{ marginBottom: 24 }}>
          <a 
            href="/ai-report" 
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              color: "#4ecbff",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: 16
            }}
          >
            <FaArrowLeft size={16} />
            Back to AI Report
          </a>
        </div>

        {/* Header */}
        <div style={{ 
          background: "linear-gradient(135deg, #5adbb5 0%, #4ecbff 100%)", 
          borderRadius: 16, 
          padding: "32px", 
          marginBottom: 32,
          textAlign: "center",
          color: "#fff",
          boxShadow: "0 4px 20px rgba(94, 219, 181, 0.3)"
        }}>
          <div style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>
            <FaLightbulb style={{ marginRight: 12 }} />
            Money Saving Tips
          </div>
          <div style={{ fontSize: 18, opacity: 0.9 }}>
            Personalized financial advice to help you save more and spend smarter
          </div>
          <button
            onClick={() => {
              setLoading(true);
              fetchMoneySavingTip();
            }}
            style={{
              background: "rgba(255,255,255,0.2)",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.3)",
              borderRadius: 8,
              padding: "8px 16px",
              marginTop: 16,
              cursor: "pointer",
              fontSize: 14,
              fontWeight: 600
            }}
          >
            🔄 Refresh Latest Tips
          </button>
        </div>

        {/* Error display */}
        {error && (
          <div style={{
            background: "#fff2f0",
            border: "1px solid #ffccc7",
            borderRadius: 12,
            padding: "20px",
            marginBottom: 24,
            color: "#ff4d4f"
          }}>
            {error}
          </div>
        )}

        {/* Main content */}
        <div style={{ 
          background: "#fff", 
          borderRadius: 16, 
          boxShadow: "0 2px 16px rgba(0,0,0,0.08)", 
          padding: "40px",
          marginBottom: 32
        }}>
          {loading ? (
            <div style={{ textAlign: "center", padding: "40px" }}>
              <div style={{ fontSize: 18, color: "#666" }}>Loading...</div>
            </div>
          ) : (
            <>
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 12, 
                marginBottom: 24,
                paddingBottom: 16,
                borderBottom: "2px solid #f0f0f0"
              }}>
                <FaChartLine color="#5adbb5" size={24} />
                <h1 style={{ 
                  fontSize: 28, 
                  fontWeight: 700, 
                  color: "#222",
                  margin: 0
                }}>
                  Your Personalized Money Saving Advice
                </h1>
              </div>
              
              <div style={{ 
                fontSize: 18, 
                lineHeight: 1.8, 
                color: "#444",
                background: "#f8f9fa",
                padding: "24px",
                borderRadius: 12,
                borderLeft: "4px solid #5adbb5"
              }}>
                {aiReport?.money_saving_tip || defaultTip}
              </div>
            </>
          )}
        </div>

        {/* Additional tips section */}
        <div style={{ 
          background: "#fff", 
          borderRadius: 16, 
          boxShadow: "0 2px 16px rgba(0,0,0,0.08)", 
          padding: "32px"
        }}>
          <h2 style={{ 
            fontSize: 24, 
            fontWeight: 700, 
            color: "#222",
            marginBottom: 24
          }}>
            Additional Tips for Financial Success
          </h2>
          
          <div style={{ display: "grid", gap: 20 }}>
            <div style={{ 
              padding: "20px", 
              background: "#f8f9fa", 
              borderRadius: 12,
              borderLeft: "4px solid #4ecbff"
            }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, color: "#222", marginBottom: 8 }}>
                Track Your Spending
              </h3>
              <p style={{ color: "#666", lineHeight: 1.6 }}>
                Monitor your daily expenses to identify patterns and areas where you can cut back. Use budgeting apps or simple spreadsheets to keep track.
              </p>
            </div>
            
            <div style={{ 
              padding: "20px", 
              background: "#f8f9fa", 
              borderRadius: 12,
              borderLeft: "4px solid #ff7ca3"
            }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, color: "#222", marginBottom: 8 }}>
                Set Financial Goals
              </h3>
              <p style={{ color: "#666", lineHeight: 1.6 }}>
                Define clear, achievable financial goals. Whether it's saving for a vacation, emergency fund, or retirement, having specific targets helps you stay motivated.
              </p>
            </div>
            
            <div style={{ 
              padding: "20px", 
              background: "#f8f9fa", 
              borderRadius: 12,
              borderLeft: "4px solid #ffe08f"
            }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, color: "#222", marginBottom: 8 }}>
                Automate Your Savings
              </h3>
              <p style={{ color: "#666", lineHeight: 1.6 }}>
                Set up automatic transfers to your savings account. This ensures you save consistently without having to think about it every month.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ 
          textAlign: "center", 
          marginTop: 48, 
          padding: "24px",
          color: "#666",
          fontSize: 14
        }}>
          {aiReport ? (
            <>
                             <p>📊 Report ID: {aiReport.id}</p>
               <p>📅 Generated: {aiReport.report_date ? new Date(aiReport.report_date).toLocaleDateString() : 'Unknown'}</p>
               <p>⏱️ Analysis Period: {aiReport.analysis_period || 'Last 30 days'}</p>
               <p>💡 Data Source: Latest AI Financial Report</p>
            </>
          ) : (
            <>
                             <p>📅 Generated: Today</p>
               <p>⏱️ Analysis Period: Last 30 days</p>
                             <p>⚠️ Currently showing default tips</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}



