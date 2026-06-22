#!/bin/bash

# ============================================================
# محلل الأسهم - أوامر البدء السريع
# Stock Analyzer - Quick Start Commands
# ============================================================

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        محلل الأسهم - مساعد البدء السريع                       ║"
echo "║                                                                ║"
echo "║        Stock Analyzer - Quick Start Helper                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# الألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دالة للطباعة الملونة
print_section() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# الخيارات
case "${1:-help}" in
    
    # البدء السريع
    start)
        print_section "الخطوة 1: البدء السريع"
        
        if [ ! -f ".env" ]; then
            print_info "نسخ ملف البيئة..."
            cp .env.example .env
            print_success "تم نسخ .env.example إلى .env"
            print_warning "تأكد من تعديل .env بمفاتيحك الشخصية قبل التشغيل"
        fi
        
        print_info "تشغيل Docker..."
        docker-compose up -d
        print_success "Docker قيد التشغيل"
        
        print_info "الانتظار 3 دقائق لتهيئة الخدمات..."
        sleep 10
        
        print_success "الخطوة 1: اكتملت!"
        echo ""
        echo "الخادم متاح على:"
        echo -e "  ${GREEN}Frontend:${NC}        http://localhost:3000"
        echo -e "  ${GREEN}Backend:${NC}         http://localhost:5000/api"
        echo -e "  ${GREEN}pgAdmin:${NC}         http://localhost:5050"
        echo -e "  ${GREEN}Redis Commander:${NC} http://localhost:8081"
        ;;
    
    # إيقاف التطبيق
    stop)
        print_section "إيقاف التطبيق"
        docker-compose down
        print_success "تم إيقاف جميع الخدمات"
        ;;
    
    # إعادة تشغيل
    restart)
        print_section "إعادة تشغيل التطبيق"
        docker-compose restart
        print_success "تم إعادة تشغيل جميع الخدمات"
        ;;
    
    # عرض السجلات
    logs)
        print_section "السجلات (Ctrl+C للخروج)"
        docker-compose logs -f
        ;;
    
    # اختبار الاتصال
    test)
        print_section "اختبار الاتصالات"
        
        print_info "اختبار الاتصال بـ Frontend..."
        if curl -s http://localhost:3000 > /dev/null; then
            print_success "Frontend متصل"
        else
            print_error "Frontend غير متصل"
        fi
        
        print_info "اختبار الاتصال بـ Backend API..."
        if curl -s http://localhost:5000/api > /dev/null 2>&1; then
            print_success "Backend متصل"
        else
            print_error "Backend غير متصل"
        fi
        
        print_info "اختبار الاتصال بـ PostgreSQL..."
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            print_success "PostgreSQL متصل"
        else
            print_error "PostgreSQL غير متصل"
        fi
        
        print_info "اختبار الاتصال بـ Redis..."
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis متصل"
        else
            print_error "Redis غير متصل"
        fi
        ;;
    
    # إعادة تعيين كاملة
    reset)
        print_section "تحذير: سيتم حذف جميع البيانات!"
        read -p "هل أنت متأكد؟ (نعم/لا): " confirm
        
        if [ "$confirm" = "نعم" ] || [ "$confirm" = "yes" ]; then
            print_warning "جاري حذف البيانات..."
            docker-compose down -v
            print_success "تم حذف جميع البيانات"
            
            print_info "إعادة التشغيل..."
            docker-compose up -d
            print_success "تم إعادة التشغيل"
        else
            print_info "تم الإلغاء"
        fi
        ;;
    
    # فتح shell
    shell-db)
        print_section "فتح PostgreSQL Shell"
        docker-compose exec postgres psql -U postgres -d stock_analyzer
        ;;
    
    # تنظيف الموارد
    clean)
        print_section "تنظيف الموارد المستخدمة"
        
        print_info "حذف الحاويات غير المستخدمة..."
        docker system prune -f
        
        print_info "حذف الصور غير المستخدمة..."
        docker image prune -f
        
        print_success "تم التنظيف"
        ;;
    
    # بناء الصور
    build)
        print_section "بناء صور Docker"
        docker-compose build --no-cache
        print_success "تم البناء"
        ;;
    
    # تثبيت الاعتماديات
    install)
        print_section "تثبيت الاعتماديات"
        
        if [ -f "package.json" ]; then
            print_info "تثبيت المتعلقات من package.json..."
            npm install
            print_success "تم التثبيت"
        else
            print_error "لم يتم العثور على package.json"
        fi
        ;;
    
    # تشغيل الاختبارات
    test-run)
        print_section "تشغيل الاختبارات"
        
        if [ -f "package.json" ]; then
            npm test
        else
            print_error "لم يتم العثور على الاختبارات"
        fi
        ;;
    
    # فحص الأداء
    health)
        print_section "فحص صحة النظام"
        
        print_info "استخدام الذاكرة:"
        docker stats --no-stream
        ;;
    
    # الإحصائيات
    stats)
        print_section "إحصائيات التطبيق"
        
        print_info "عدد الحاويات الجارية:"
        docker ps -q | wc -l
        
        print_info "إجمالي حجم البيانات:"
        du -sh .
        
        print_info "عدد الأسطر البرمجية:"
        find . -name "*.py" -o -name "*.js" -o -name "*.sql" | xargs wc -l 2>/dev/null | tail -1
        ;;
    
    # الرابط الدعم
    help|--help|-h)
        print_section "الأوامر المتاحة"
        
        echo ""
        echo -e "${YELLOW}الاستخدام:${NC}"
        echo "  ./QUICK_START.sh [command]"
        echo ""
        echo -e "${YELLOW}الأوامر:${NC}"
        echo ""
        echo -e "  ${GREEN}start${NC}           - بدء التطبيق"
        echo -e "  ${GREEN}stop${NC}            - إيقاف التطبيق"
        echo -e "  ${GREEN}restart${NC}         - إعادة تشغيل"
        echo -e "  ${GREEN}logs${NC}            - عرض السجلات"
        echo -e "  ${GREEN}test${NC}            - اختبار الاتصالات"
        echo -e "  ${GREEN}reset${NC}           - إعادة تعيين كاملة"
        echo -e "  ${GREEN}shell-db${NC}        - فتح PostgreSQL"
        echo -e "  ${GREEN}clean${NC}           - تنظيف الموارد"
        echo -e "  ${GREEN}build${NC}           - بناء الصور"
        echo -e "  ${GREEN}install${NC}         - تثبيت المتعلقات"
        echo -e "  ${GREEN}test-run${NC}        - تشغيل الاختبارات"
        echo -e "  ${GREEN}health${NC}          - فحص الصحة"
        echo -e "  ${GREEN}stats${NC}           - الإحصائيات"
        echo -e "  ${GREEN}help${NC}            - هذه الرسالة"
        echo ""
        echo -e "${YELLOW}الأمثلة:${NC}"
        echo ""
        echo "  # بدء التطبيق"
        echo "  ./QUICK_START.sh start"
        echo ""
        echo "  # عرض السجلات"
        echo "  ./QUICK_START.sh logs"
        echo ""
        echo "  # إيقاف التطبيق"
        echo "  ./QUICK_START.sh stop"
        echo ""
        ;;
    
    *)
        print_error "أمر غير معروف: $1"
        echo "استخدم: ./QUICK_START.sh help"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ تم إكمال العملية بنجاح${NC}"
