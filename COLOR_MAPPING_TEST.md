# 子分类颜色映射测试

## 扩展的颜色映射

### Dining 分类的子分类
- `Snacks` / `Snack`: `#ff7ca3` (粉色)
- `Meals`: `#4ecbff` (蓝色)
- `Drinks` / `Drink`: `#ffe08f` (黄色)
- `Restaurant`: `#5adbb5` (绿色)
- `Daily meal`: `#4ecbff` (蓝色)
- `Daily`: `#ffe08f` (黄色)

### Transport 分类的子分类
- `Bus`: `#4ecbff` (蓝色)
- `Subway`: `#5adbb5` (绿色)
- `Taxi`: `#a084e8` (紫色)
- `Train`: `#a084e8` (紫色)

### Shopping 分类的子分类
- `Clothing`: `#ff7ca3` (粉色)
- `Electronics`: `#4ecbff` (蓝色)
- `Cosmetic` / `Cosmetics`: `#ff4444` (红色)
- `Household`: `#4ecbff` (蓝色)

### Entertainment 分类的子分类
- `Movies` / `Movie`: `#5adbb5` (绿色)
- `Games` / `Game`: `#ff7ca3` (粉色)
- `KTV`: `#a084e8` (紫色)

### Healthcare 分类的子分类
- `Medicine`: `#a084e8` (紫色)
- `Medical`: `#4ecbff` (蓝色)

## 测试步骤

1. **刷新页面**：访问 `/category-list`
2. **点击Shopping分类**：查看子分类颜色
3. **点击Dining分类**：查看子分类颜色
4. **检查控制台**：确认颜色映射正确

## 预期结果

### Shopping 分类页面
- `Clothing`: 粉色 (`#ff7ca3`)
- `Household`: 蓝色 (`#4ecbff`) - 之前是灰色，现在应该是蓝色
- `Cosmetic`: 红色 (`#ff4444`) - 之前是灰色，现在应该是红色

### Dining 分类页面
- `Daily meal`: 蓝色 (`#4ecbff`) - 之前是灰色，现在应该是蓝色
- `Drink`: 黄色 (`#ffe08f`) - 之前是灰色，现在应该是黄色

## 验证点

- [ ] Household 子分类显示蓝色而不是灰色
- [ ] Cosmetic 子分类显示红色而不是灰色
- [ ] Daily meal 子分类显示蓝色而不是灰色
- [ ] Drink 子分类显示黄色而不是灰色
- [ ] Clothing 和 Cosmetic 有不同的颜色（粉色 vs 红色）
- [ ] 所有子分类都有对应的颜色
- [ ] 没有子分类显示灰色 (#666666)

## 颜色分配逻辑

- **粉色** (`#ff7ca3`): 食物和服装 (Snacks, Clothing, Games)
- **红色** (`#ff4444`): 化妆品 (Cosmetics)
- **蓝色** (`#4ecbff`): 交通和日常用品 (Bus, Electronics, Household, Medical, Meals, Daily meal)
- `Household`: 蓝色 (`#4ecbff`) - 之前是灰色，现在应该是蓝色
- **黄色** (`#ffe08f`): 饮料和日常 (Drinks, Daily)
- **绿色** (`#5adbb5`): 餐厅和娱乐 (Restaurant, Subway, Movies)
- **紫色** (`#a084e8`): 交通和医疗 (Taxi, Train, Medicine, KTV) 