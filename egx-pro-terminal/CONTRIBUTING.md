# 🤝 دليل المساهمة في EGX Pro Terminal

> **شكراً لاهتمامك بالمساهمة في EGX Pro Terminal!**  
> هذا الدليل يوضح كيفية المساهمة بشكل فعال واحترافي.

---

## 📋 جدول المحتويات

1. [قبل البدء](#قبل-البدء)
2. [كيفية المساهمة](#كيفية-المساهمة)
3. [معايير الكود](#معايير-الكود)
4. [اختبار التغييرات](#اختبار-التغييرات)
5. [إرسال الطلب (Pull Request)](#إرسال-الطلب)

---

## قبل البدء

### المتطلبات الأساسية:

- Python 3.10 أو أحدث
- Git
- حساب GitHub

### إعداد البيئة:

```bash
# 1. استنساخ المستودع
git clone https://github.com/m02417710-maker/egx-pro-terminal.git
cd egx-pro-terminal

# 2. إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/macOS
# أو: venv\Scripts\activate  # Windows

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. تشغيل الاختبارات
python -m pytest tests/
```

---

## كيفية المساهمة

### 1. الإبلاغ عن مشكلة (Issue)

إذا وجدت خطأ أو لديك اقتراح:

1. تأكد من عدم وجود مشكلة مشابهة مفتوحة.
2. افتح مشكلة جديدة باستخدام القوالب المتوفرة.
3. اشرح المشكلة بوضوح مع أمثلة قابلة للتكرار.

### 2. إصلاح خطأ

```bash
# 1. أنشئ فرعاً جديداً
git checkout -b fix/وصف-مختصر-للخطأ

# 2. أجرِ التغييرات
# ...

# 3. اختبر التغييرات
python -m pytest tests/

# 4. commit
git commit -m "fix: وصف مختصر للإصلاح"

# 5. push
git push origin fix/وصف-مختصر-للخطأ
```

### 3. إضافة ميزة جديدة

```bash
# 1. أنشئ فرعاً جديداً
git checkout -b feature/اسم-الميزة

# 2. طوّر الميزة
# ...

# 3. اختبر التغييرات
python -m pytest tests/

# 4. commit
git commit -m "feat: وصف الميزة الجديدة"

# 5. push
git push origin feature/اسم-الميزة
```

---

## معايير الكود

### التنسيق:

- اتبع [PEP 8](https://pep8.org/) لتنسيق Python.
- استخدم Black formatter: `black core/ data/ config/ tests/`
- أقصى طول للسطر: 100 حرف.

### التوثيق:

- جميع الدوال يجب أن تحتوي على docstrings.
- استخدم النوعية (Type Hints) في المعاملات.
- علّق الكود المعقد بشكل وافٍ.

### مثال:

```python
def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        data: Closing price series
        period: RSI calculation period (default: 14)

    Returns:
        pd.Series: RSI values (0-100)
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
```

---

## اختبار التغييرات

### تشغيل الاختبارات:

```bash
# جميع الاختبارات
python -m pytest tests/

# مع تغطية الكود
python -m pytest tests/ --cov=core --cov=data --cov=config

# اختبار معين
python -m pytest tests/test_analysis.py::test_rsi_calculation -v
```

### إضافة اختبارات جديدة:

- جميع الميزات الجديدة يجب أن تُرفق باختبارات.
- استخدم pytest framework.
- غطّي حالات الحافة (Edge Cases).

---

## إرسال الطلب

### Pull Request Checklist:

- [ ] الفرع محدّث مع `main`.
- [ ] جميع الاختبارات تمر بنجاح.
- [ ] الكود مُنسّق بـ Black.
- [ ] docstrings مكتملة.
- [ ] التغييرات موثقة في `CHANGELOG.md`.
- [ ] لا يوجد أسرار (API keys) في الكود.

### عنوان الـ PR:

اتبع [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` ميزة جديدة
- `fix:` إصلاح خطأ
- `docs:` تغيير في التوثيق
- `test:` اختبارات
- `refactor:` إعادة هيكلة
- `perf:` تحسين الأداء

### مثال:

```
feat: إضافة مؤشر ADX إلى لوحة التحليل

- إضافة حساب ADX في core/analysis.py
- إضافة اختبارات الوحدة
- تحديث واجهة Streamlit
```

---

## 🙏 شكراً!

كل مساهمة — صغيرة كانت أم كبيرة — تُحدث فرقاً. نقدّر وقتك وجهدك.

**صُنع بـ ❤️ في مصر** 🇪🇬
