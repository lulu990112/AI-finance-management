# AI Report 功能说明

## 概述

AI Report功能是基于用户的交易数据，使用GPT生成个性化的英语理财建议。报告包含三个部分：

1. **Financial Advice Summary** - 理财建议总结（约50字）
2. **Abnormal Alert** - 异常警报（约30字）
3. **Money Saving Tip** - 省钱建议（约300字）

## 功能特性

### 1. 智能数据分析
- 分析用户的交易分类分布
- 识别高价值交易
- 统计频繁商家
- 计算各分类的支出百分比

### 2. 个性化建议
- 基于实际消费模式生成建议
- 识别异常消费行为
- 提供具体的省钱策略

### 3. 报告缓存机制
- 7天内重复请求返回缓存报告
- 避免重复生成，节省API成本

## API端点

### 1. 生成AI报告
```
POST /api/ai_report/generate/
```

**请求参数：**
```json
{
    "analysis_period_days": 30  // 可选，默认30天
}
```

**响应示例：**
```json
{
    "message": "AI report generated successfully",
    "report": {
        "id": 1,
        "financial_advice_summary": "Based on your spending data...",
        "abnormal_alert": "The user's spending data shows...",
        "money_saving_tip": "To save money while still enjoying...",
        "report_date": "2025-08-06T17:44:12.483532Z",
        "analysis_period": "Last 30 days",
        "total_transactions": 2,
        "total_amount": "224.97",
        "is_generated": true,
        "generation_status": "completed"
    },
    "is_cached": false
}
```

### 2. 获取最新报告
```
GET /api/ai_report/latest/
```

**响应示例：**
```json
{
    "message": "Latest AI report retrieved successfully",
    "report": {
        // 报告数据
    }
}
```

### 3. 获取报告列表
```
GET /api/ai_report/reports/?page=1&page_size=10
```

**响应示例：**
```json
{
    "reports": [
        // 报告列表
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
}
```

### 4. 获取报告统计
```
GET /api/ai_report/stats/
```

**响应示例：**
```json
{
    "message": "AI report stats retrieved successfully",
    "stats": {
        "total_reports": 1,
        "completed_reports": 1,
        "failed_reports": 0,
        "latest_report_date": "2025-08-06T17:44:12.483532Z",
        "average_transactions_per_report": 2.0,
        "total_amount_analyzed": 224.97
    }
}
```

### 5. 删除报告
```
DELETE /api/ai_report/reports/{report_id}/
```

## 数据库模型

### AIReport 模型
```python
class AIReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 报告内容
    financial_advice_summary = models.TextField()
    abnormal_alert = models.TextField()
    money_saving_tip = models.TextField()
    
    # 元数据
    report_date = models.DateTimeField(auto_now_add=True)
    analysis_period = models.CharField(max_length=50)
    total_transactions = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # 状态
    is_generated = models.BooleanField(default=False)
    generation_status = models.CharField(max_length=20, default='pending')
```

## 使用流程

### 1. 准备数据
确保用户有交易数据：
```bash
# 同步邮件
python manage.py batch_process_emails

# 或通过API同步
POST /api/gpt/batch_sync_and_process/
```

### 2. 生成报告
```javascript
// 前端调用示例
fetch('/api/ai_report/generate/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        analysis_period_days: 30
    })
})
.then(response => response.json())
.then(data => {
    console.log('AI报告:', data.report);
});
```

### 3. 获取报告
```javascript
// 获取最新报告
fetch('/api/ai_report/latest/', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
})
.then(response => response.json())
.then(data => {
    console.log('最新报告:', data.report);
});
```

## 测试

### 运行测试脚本
```bash
python test_ai_report.py
```

### 手动测试
1. 确保有用户和交易数据
2. 运行测试脚本创建测试数据
3. 验证AI报告生成功能
4. 检查报告内容质量

## 配置要求

### 1. OpenAI API Key
确保在环境变量或`.env`文件中设置：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 分类设置
```bash
python manage.py setup_categories
```

## 错误处理

### 常见错误及解决方案

1. **没有交易数据**
   - 确保用户有交易记录
   - 先同步和处理邮件

2. **OpenAI API错误**
   - 检查API Key是否正确
   - 检查网络连接
   - 检查API配额

3. **报告生成失败**
   - 检查GPT服务是否正常
   - 查看日志获取详细错误信息

## 性能优化

### 1. 缓存机制
- 7天内重复请求返回缓存报告
- 避免重复调用GPT API

### 2. 异步处理
- 可以考虑将报告生成改为异步任务
- 使用Celery等任务队列

### 3. 数据预处理
- 优化交易数据查询
- 使用数据库索引提高查询性能

## 扩展功能

### 1. 报告模板
- 支持多种报告模板
- 根据用户偏好定制报告风格

### 2. 历史趋势分析
- 比较不同时期的消费模式
- 生成趋势图表

### 3. 预算建议
- 基于历史数据推荐预算分配
- 提供预算执行建议

## 安全考虑

1. **数据隐私**
   - 用户数据仅用于生成报告
   - 不存储敏感财务信息

2. **API安全**
   - 所有端点需要用户认证
   - 用户只能访问自己的报告

3. **错误处理**
   - 不暴露内部错误信息
   - 记录详细日志用于调试

## 监控和维护

### 1. 日志监控
- 监控报告生成成功率
- 跟踪API调用频率

### 2. 性能监控
- 监控报告生成时间
- 跟踪数据库查询性能

### 3. 质量监控
- 定期检查报告内容质量
- 收集用户反馈

## 总结

AI Report功能为用户提供了基于实际消费数据的个性化理财建议，帮助用户更好地管理财务。通过智能分析和GPT生成，提供了有价值的财务洞察和实用的省钱建议。 