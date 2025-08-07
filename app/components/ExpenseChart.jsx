import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAllTransactions } from "../services/api";

// 默认数据（当API数据不可用时）
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

  // 处理真实交易数据，按分类分组
  const processTransactionData = (transactions) => {
    if (!transactions || transactions.length === 0) {
      return mockCategories;
    }

    // 获取最近一周的日期范围
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay() + 1); // 设置为本周一
    startOfWeek.setHours(0, 0, 0, 0);
    
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6); // 设置为本周日
    endOfWeek.setHours(23, 59, 59, 999);

    console.log('📅 ExpenseChart 周数据范围:', startOfWeek.toISOString(), '到', endOfWeek.toISOString());

    // 过滤最近一周的交易
    const weeklyTransactions = transactions.filter(tx => {
      const txDate = new Date(tx.transaction_date);
      return txDate >= startOfWeek && txDate <= endOfWeek;
    });

    console.log('📊 ExpenseChart 本周交易数量:', weeklyTransactions.length);

    // 按分类分组并计算金额
    const categoryMap = {};
    weeklyTransactions.forEach(tx => {
      const categoryName = typeof tx.category === 'object' ? tx.category.name : tx.category;
      if (!categoryMap[categoryName]) {
        categoryMap[categoryName] = 0;
      }
      categoryMap[categoryName] += parseFloat(tx.amount || 0);
    });

    // 转换为数组格式并分配颜色
    const processedCategories = Object.entries(categoryMap)
      .filter(([name, value]) => value > 0) // 只显示有消费的分类
      .map(([name, value]) => ({
        name,
        value: Math.round(value * 100) / 100, // 保留两位小数
        color: getDefaultCategoryColor(name)
      }))
      .sort((a, b) => b.value - a.value); // 按金额降序排列

    console.log('📊 ExpenseChart 处理后的分类数据:', processedCategories);
    return processedCategories.length > 0 ? processedCategories : mockCategories;
  };

  // 获取默认颜色
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

  // 获取真实数据
  useEffect(() => {
    const fetchTransactionData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 ExpenseChart 开始获取交易数据...');
        const transactions = await getAllTransactions();
        
        if (transactions && transactions.length > 0) {
          console.log('✅ ExpenseChart 成功获取交易数据:', transactions.length, '条');
          const processedData = processTransactionData(transactions);
          setCategories(processedData);
        } else {
          console.log('⚠️ ExpenseChart 未找到交易数据，使用默认数据');
          setCategories(mockCategories);
        }
      } catch (err) {
        console.error('❌ ExpenseChart 获取交易数据失败:', err);
        setError('获取数据失败');
        setCategories(mockCategories);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactionData();
  }, []);

  const totalAmount = categories.reduce((sum, c) => sum + c.value, 0);

  // Calculate path for each sector
  let acc = 0;
  const arcs = categories.map((cat, i) => {
    const start = acc / totalAmount;
    acc += cat.value;
    const end = acc / totalAmount;
    const large = end - start > 0.5 ? 1 : 0;
    const a = 2 * Math.PI * start;
    const b = 2 * Math.PI * end;
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
          <div style={{ color: '#666', fontSize: 14 }}>加载中...</div>
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
            {categories === mockCategories ? 'Last week (默认数据)' : 'Last week (实时数据)'}
          </div>
        </div>
      )}
    </div>
  );
} 