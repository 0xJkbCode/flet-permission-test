import flet as ft
import os

# التحقق من أننا على Android
try:
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    print("Pyjnius not found, native Android functions will not be available.")
    autoclass = None
    IS_ANDROID = False

def get_context():
    """الحصول على Application Context بدلاً من Activity"""
    if not autoclass:
        return None
    
    try:
        # الطريقة الأفضل - استخدام Application Context
        # هذا يعمل بشكل أفضل من Activity للعمليات طويلة المدى
        Context = autoclass('android.content.Context')
        
        # محاولة الحصول على Application Context من خلال Static Method
        ActivityThread = autoclass('android.app.ActivityThread')
        current_application = ActivityThread.currentApplication()
        
        if current_application:
            context = current_application.getApplicationContext()
            print("Got ApplicationContext via ActivityThread")
            return context
    except Exception as e:
        print(f"ActivityThread method failed: {e}")
    
    print("Could not get context")
    return None

def request_contact_permissions() -> bool:
    """طلب صلاحيات جهات الاتصال"""
    if not autoclass:
        return False
    
    try:
        context = get_context()
        if not context:
            print("Could not get context")
            return False
        
        print(f"Got context: {context}")
        
        # استخدام ContextCompat بدلاً من ActivityCompat للتحقق من الصلاحيات
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        # التحقق من الصلاحية
        write_permission = ContextCompat.checkSelfPermission(
            context, 
            Manifest.WRITE_CONTACTS
        )
        
        print(f"Permission status: {write_permission}")
        
        if write_permission == PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission is granted")
            return True
        else:
            print("WRITE_CONTACTS permission not granted")
            # لا يمكن طلب الصلاحية من Context، نحتاج Activity للطلب
            # لكن يمكننا إرشاد المستخدم للإعدادات
            return False
        
    except Exception as e:
        print(f"Error in permission check: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_contact(name: str, phone: str) -> bool:
    """إضافة جهة اتصال باستخدام ApplicationContext"""
    if not autoclass or not name or not phone:
        return False
    
    try:
        context = get_context()
        if not context:
            print("Could not get context for adding contact")
            return False
        
        print(f"Got context for adding contact: {context}")
        
        # التحقق من الصلاحيات أولاً
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        write_permission = ContextCompat.checkSelfPermission(
            context, 
            Manifest.WRITE_CONTACTS
        )
        
        if write_permission != PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission not granted")
            return False
        
        print("Permission confirmed, proceeding with contact creation")
        
        # استيراد الكلاسات
        ContentValues = autoclass('android.content.ContentValues')
        ContactsContract = autoclass('android.provider.ContactsContract')
        Data = autoclass('android.provider.ContactsContract$Data')
        RawContacts = autoclass('android.provider.ContactsContract$RawContacts')
        StructuredName = autoclass('android.provider.ContactsContract$CommonDataKinds$StructuredName')
        Phone = autoclass('android.provider.ContactsContract$CommonDataKinds$Phone')
        
        print("Loaded ContactsContract classes")
        
        # الحصول على ContentResolver من Context
        content_resolver = context.getContentResolver()
        print("Got ContentResolver from context")
        
        # إنشاء جهة اتصال جديدة
        values = ContentValues()
        values.put(RawContacts.ACCOUNT_TYPE, None)
        values.put(RawContacts.ACCOUNT_NAME, None)
        
        print("Creating raw contact...")
        raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
        
        if not raw_contact_uri:
            print("Failed to create raw contact")
            return False
        
        raw_contact_id = int(raw_contact_uri.getLastPathSegment())
        print(f"Created raw contact with ID: {raw_contact_id}")
        
        # إضافة الاسم
        print("Adding name...")
        name_values = ContentValues()
        name_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        name_values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
        name_values.put(StructuredName.DISPLAY_NAME, name)
        content_resolver.insert(Data.CONTENT_URI, name_values)
        print("Name added successfully")
        
        # إضافة رقم الهاتف
        print("Adding phone number...")
        phone_values = ContentValues()
        phone_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        phone_values.put(Data.MIMETYPE, Phone.CONTENT_ITEM_TYPE)
        phone_values.put(Phone.NUMBER, phone)
        phone_values.put(Phone.TYPE, Phone.TYPE_MOBILE)
        content_resolver.insert(Data.CONTENT_URI, phone_values)
        print("Phone number added successfully")
        
        print(f"Contact '{name}' added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding contact: {e}")
        import traceback
        traceback.print_exc()
        return False

# دالة إضافية لفتح إعدادات التطبيق
def open_app_settings():
    """فتح إعدادات التطبيق لطلب الصلاحيات يدوياً"""
    try:
        context = get_context()
        if not context:
            return False
        
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        
        intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        package_name = context.getPackageName()
        uri = Uri.fromParts("package", package_name, None)
        intent.setData(uri)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        
        context.startActivity(intent)
        print("Opened app settings")
        return True
        
    except Exception as e:
        print(f"Error opening app settings: {e}")
        return False
