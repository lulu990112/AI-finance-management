import React, { useState } from "react";
import { useRouter } from "next/navigation";

// 近一周 mock 数据
const mockCategories = [
  { name: "餐饮", value: 320, color: "#ff7ca3" },
  { name: "交通", value: 180, color: "#4ecbff" },
  { name: "购物", value: 120, color: "#ffe08f" },
  { name: "娱乐", value: 80, color: "#5adbb5" },
];
const totalAmount = mockCategories.reduce((sum, c) => sum + c.value, 0);

export default function ExpenseChart() {
  const router = useRouter();
  const [activeIndex, setActiveIndex] = useState(null);

  // 计算每个扇区的路径
  let acc = 0;
  const arcs = mockCategories.map((cat, i) => {
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
        onClick={() => router.push('/category-dashboard')}
        style={{ cursor: 'pointer' }}
      />
    );
  });

  return (
    <div style={{ position: 'relative', width: 240, height: 240 }}>
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
          <div style={{ fontWeight: 700, fontSize: 16 }}>{mockCategories[activeIndex].name}</div>
          <div style={{ color: '#ff7ca3', fontWeight: 600, fontSize: 18 }}>{mockCategories[activeIndex].value} 元</div>
          <div style={{ color: '#888', fontSize: 14 }}>
            {((mockCategories[activeIndex].value / totalAmount) * 100).toFixed(1)}%
          </div>
          <div style={{ color: '#aaa', fontSize: 12, marginTop: 4 }}>近一周</div>
        </div>
      )}
    </div>
  );
} 