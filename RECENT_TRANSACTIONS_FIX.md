# RecentTransactions 修复验证

## 问题描述

RecentTransactions模块显示所有交易的category和subcategory都为"Other"。

## 问题原因

在 `RecentTransactions.jsx` 的 `formatTransaction` 函数中：

```javascript
// 错误的代码
title: `${transaction.item_name || 'Unknown'} (${transaction.subcategory?.name || 'Other'})`,

// 修复后的代码
title: `${transaction.item_name || 'Unknown'} (${transaction.subcategory || 'Other'})`,
```

## 问题分析

1. **数据结构不匹配**：
   - 代码期望：`transaction.subcategory.name`（对象格式）
   - 实际API返回：`transaction.subcategory`（字符串格式）

2. **API数据格式**：
   ```javascript
   {
     "category": "Shopping",        // 字符串
     "subcategory": "Clothing",     // 字符串
     "amount": "50.00"
   }
   ```

3. **错误逻辑**：
   - `transaction.subcategory?.name` 返回 `undefined`
   - 最终显示为 `'Other'`

## 修复内容

将 `transaction.subcategory?.name` 改为 `transaction.subcategory`，直接使用字符串值。

## 预期结果

### 修复前
- 所有交易显示为：`"Item Name (Other)"`

### 修复后
- 交易应该显示正确的子分类：
  - `"BronchoStop Cough Syrup for Dry and Chesty Coughs - 240ml (Medicine)"`
  - `"Yeezy 500 Jn99 Stone Salt 4.5 (37.3) (Clothing)"`
  - `"Polo NY Sweatshirt Ld34 Andover Heather 10 (S) (Clothing)"`
  - `"TNF Hikesteller Ld00 COSMO PINK 10 (S) (Clothing)"`

## 测试步骤

1. **刷新页面**：访问主页
2. **检查Recent Transactions区域**：查看交易标题
3. **验证子分类显示**：确认不再显示"(Other)"
4. **检查控制台**：查看调试信息

## 验证点

- [ ] Recent Transactions不再显示"(Other)"
- [ ] 交易标题显示正确的子分类名称
- [ ] 控制台显示正确的交易数据结构
- [ ] 所有4条最新交易都显示正确的子分类 