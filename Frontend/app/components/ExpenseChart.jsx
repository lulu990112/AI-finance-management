import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAllTransactions } from "../services/api";

// Default data (when API data is not available)
const mockCategories = [
  { name: "Dining", value: 320, color: "#ff7ca3" },
  { name: "Transport", value: 180, color: "#4ecbff" },
  { name: "Shopping", value: 120, color: "#ffe08f" },
  { name: "Entertainment", value: 80, color: "#5adbb5" },
];

export default function ExpenseChart() {
  const router = useRouter();
  const [activeIndex, setActiveIndex] = useState(null);
  const [categories, setCategories] = useState(mockCategories);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Process real transaction data, group by category
  const processTransactionData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return mockCategories;
    }

    // Get date range for the last week
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay() + 1); // Set to Monday of this week
    startOfWeek.setHours(0, 0, 0, 0);
    
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6); // Set to Sunday of this week
    endOfWeek.setHours(23, 59, 59, 999);

    console.log('📅 ExpenseChart week data range:', startOfWeek.toISOString(), 'to', endOfWeek.toISOString());

    // Filter transactions for the last week
    const weeklyTransactions = transactions.filter(tx => {
      const txDate = new Date(tx.transaction_date);
      return txDate >= startOfWeek && txDate <= endOfWeek;
    });

    console.log('📊 ExpenseChart weekly transaction count:', weeklyTransactions.length);

    // Group by category and calculate amount
    const categoryMap = {};
    weeklyTransactions.forEach(tx => {
      const categoryName = typeof tx.category === 'object' ? tx.category.name : tx.category;
      if (!categoryMap[categoryName]) {
        categoryMap[categoryName] = 0;
      }
      categoryMap[categoryName] += parseFloat(tx.amount || 0);
    });

    // Convert to array format and assign colors
    const processedCategories = Object.entries(categoryMap)
      .filter(([name, value]) => value > 0) // Only show categories with expenses
      .map(([name, value]) => ({
        name,
        value: Math.round(value * 100) / 100, // Keep two decimal places
        color: getDefaultCategoryColor(name)
      }))
      .sort((a, b) => b.value - a.value); // Sort by amount in descending order

    console.log('📊 ExpenseChart processed category data:', processedCategories);
    return processedCategories.length > 0 ? processedCategories : mockCategories;
  };

  // Get default color
  const getDefaultCategoryColor = (categoryName) => {
    const colorMap = {
      'Dining': '#ff7ca3',
      'Transport': '#4ecbff',
      'Shopping': '#ffe08f',
      'Entertainment': '#5adbb5',
      'Healthcare': '#a084e8',
      'Education': '#5adbb5',
      'Other': '#666666'
    };
    
    return colorMap[categoryName] || '#666666';
  };

  // Get real data
  useEffect(() => {
    const fetchTransactionData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 ExpenseChart start fetching transaction data...');
        const transactions = await getAllTransactions();
        
        if (transactions && transactions.length > 0) {
          console.log('✅ ExpenseChart successfully fetched transaction data:', transactions.length, 'items');
          const processedData = processTransactionData(transactions);
          setCategories(processedData);
        } else {
          console.log('⚠️ ExpenseChart transaction data not found, using default data');
          setCategories(mockCategories);
        }
      } catch (err) {
        console.error('❌ ExpenseChart failed to fetch transaction data:', err);
        setError('Failed to fetch data');
        setCategories(mockCategories);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactionData();
  }, []);

  const totalAmount = categories.reduce((sum, c) => sum + c.value, 0);

  // When there's only one category, the arc's start and end points are the same, causing SVG arc to degenerate into an invisible path.
  // Special handling here: directly draw a full circle to display the category.
  const hasSingleCategory = categories.length === 1 && totalAmount > 0;

  // Calculate path for each sector (multiple categories)
  let acc = 0;
  const arcs = hasSingleCategory
    ? (
        <circle
          key="single"
          cx={100}
          cy={100}
          r={90}
          fill={categories[0].color}
          opacity={activeIndex === 0 ? 1 : 0.7}
          onMouseEnter={() => setActiveIndex(0)}
          onMouseLeave={() => setActiveIndex(null)}
          style={{ cursor: 'pointer' }}
        />
      )
    : categories.map((cat, i) => {
        const start = totalAmount === 0 ? 0 : acc / totalAmount;
        acc += cat.value;
        const end = totalAmount === 0 ? 0 : acc / totalAmount;
        // Avoid numerical errors causing end === start degeneration
        const epsilon = 1e-6;
        const clampedEnd = Math.min(1 - epsilon, end);
        const large = clampedEnd - start > 0.5 ? 1 : 0;
        const a = 2 * Math.PI * start;
        const b = 2 * Math.PI * clampedEnd;
        const x1 = 100 + 90 * Math.sin(a);
        const y1 = 100 - 90 * Math.cos(a);
        const x2 = 100 + 90 * Math.sin(b);
        const y2 = 100 - 90 * Math.cos(b);
        return (
          <path
            key={i}
            d={`M100,100 L${x1},${y1} A90,90 0 ${large} 1 ${x2},${y2} Z`}
            fill={cat.color}
            stroke="#fff"
            strokeWidth={2}
            opacity={activeIndex === i ? 1 : 0.7}
            onMouseEnter={() => setActiveIndex(i)}
            onMouseLeave={() => setActiveIndex(null)}
            style={{ cursor: 'pointer' }}
          />
        );
      });

  return (
    <div style={{ position: 'relative', width: 240, height: 240 }}>
      {loading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(255,255,255,0.9)',
          padding: '16px',
          borderRadius: '8px',
          zIndex: 5
        }}>
                          <div style={{ color: '#666', fontSize: 14 }}>Loading...</div>
        </div>
      )}
      <svg width={240} height={240} viewBox="0 0 200 200">
        <g>{arcs}</g>
        <circle cx={100} cy={100} r={60} fill="#fff" />
      </svg>
      {activeIndex !== null && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
            background: 'rgba(255,255,255,0.97)',
            borderRadius: 12,
            boxShadow: '0 2px 8px #eee',
            padding: '16px 24px',
            pointerEvents: 'none',
            minWidth: 120,
            textAlign: 'center',
            zIndex: 10
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 16 }}>{categories[activeIndex].name}</div>
          <div style={{ color: categories[activeIndex].color, fontWeight: 600, fontSize: 18 }}>${categories[activeIndex].value}</div>
          <div style={{ color: '#888', fontSize: 14 }}>
            {((categories[activeIndex].value / totalAmount) * 100).toFixed(1)}%
          </div>
          <div style={{ color: '#aaa', fontSize: 12, marginTop: 4 }}>
            {categories === mockCategories ? 'Last week (default data)' : 'Last week (real-time data)'}
          </div>
        </div>
      )}
    </div>
  );
} 