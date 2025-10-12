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

# --- Android Native Functions ---
def get_activity():
    """الحصول على Activity بطريقة مباشرة"""
    if not autoclass:
        return None
    
    try:
        # استخدام MainActivity التي اكتشفتها
        MainActivity = autoclass('com.flet.permission_test.MainActivity')
        return MainActivity.mActivity
    except Exception as e:
        print(f"Error getting MainActivity directly: {e}")
        
        # الطريقة البديلة باستخدام متغير البيئة
        try:
            activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if activity_host_class:
                activity_host = autoclass(activity_host_class)
                return activity_host.mActivity
        except Exception as e2:
            print(f"Error getting activity via environment variable: {e2}")
        
        return None

def request_contact_permissions() -> bool:
    """طلب صلاحيات جهات الاتصال باستخدام pyjnius"""
    if not autoclass:
        print("Cannot request permissions, pyjnius is not available.")
        return False
    
    try:
        # الحصول على Activity
        current_activity = get_activity()
        if not current_activity:
            print("Could not get current activity")
            return False
        
        # استيراد الكلاسات الضرورية
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        # التحقق من الصلاحية
        write_permission = ActivityCompat.checkSelfPermission(
            current_activity, 
            Manifest.WRITE_CONTACTS
        )
        
        if write_permission == PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission is already granted.")
            return True
        
        # طلب الصلاحية
        print("Requesting WRITE_CONTACTS permission...")
        permissions_array = [Manifest.WRITE_CONTACTS, Manifest.READ_CONTACTS]
        ActivityCompat.requestPermissions(
            current_activity,
            permissions_array,
            100  # Request code
        )
        
        print("Permission request dialog should be shown.")
        return True
        
    except Exception as e:
        print(f"Error requesting permissions via pyjnius: {e}")
        return False

def add_contact(name: str, phone: str) -> bool:
    """إضافة جهة اتصال باستخدام pyjnius"""
    if not autoclass:
        print("Cannot add contact, pyjnius is not available.")
        return False
    
    if not name or not phone:
        print("Name and phone are required")
        return False
    
    try:
        # الحصول على Activity
        current_activity = get_activity()
        if not current_activity:
            print("Could not get current activity")
            return False
        
        # التحقق من الصلاحيات أولاً
        ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        write_permission = ActivityCompat.checkSelfPermission(
            current_activity, 
            Manifest.WRITE_CONTACTS
        )
        
        if write_permission != PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission not granted")
            return False
        
        # استيراد الكلاسات الضرورية لإضافة جهة الاتصال
        ContentValues = autoclass('android.content.ContentValues')
        ContactsContract = autoclass('android.provider.ContactsContract')
        Data = ContactsContract.Data
        RawContacts = ContactsContract.RawContacts  
        StructuredName = ContactsContract.CommonDataKinds.StructuredName
        Phone = ContactsContract.CommonDataKinds.Phone
        
        # الحصول على ContentResolver
        content_resolver = current_activity.getContentResolver()
        
        # إنشاء جهة اتصال جديدة
        values = ContentValues()
        values.put(RawContacts.ACCOUNT_TYPE, None)
        values.put(RawContacts.ACCOUNT_NAME, None)
        
        raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
        if not raw_contact_uri:
            print("Failed to create raw contact")
            return False
        
        # الحصول على raw_contact_id
        raw_contact_id = int(raw_contact_uri.getLastPathSegment())
        
        # إضافة الاسم
        name_values = ContentValues()
        name_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        name_values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
        name_values.put(StructuredName.DISPLAY_NAME, name)
        content_resolver.insert(Data.CONTENT_URI, name_values)
        
        # إضافة رقم الهاتف
        phone_values = ContentValues()
        phone_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        phone_values.put(Data.MIMETYPE, Phone.CONTENT_ITEM_TYPE)
        phone_values.put(Phone.NUMBER, phone)
        phone_values.put(Phone.TYPE, Phone.TYPE_MOBILE)
        content_resolver.insert(Data.CONTENT_URI, phone_values)
        
        print(f"Contact '{name}' added successfully via pyjnius.")
        return True
        
    except Exception as e:
        print(f"Error adding contact via pyjnius: {e}")
        import traceback
        traceback.print_exc()
        return False
