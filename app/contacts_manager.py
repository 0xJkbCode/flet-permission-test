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

def get_activity():
    """الحصول على FlutterActivity الحالي"""
    if not autoclass:
        return None
    
    try:
        # بما أن MainActivity يرث من FlutterActivity، يمكننا الوصول إليه مباشرة
        # باستخدام ActivityThread للحصول على Current Activity
        ActivityThread = autoclass('android.app.ActivityThread')
        
        # الحصول على current activity من ActivityThread
        current_activity = ActivityThread.currentActivity()
        
        if current_activity:
            print("Got current activity via ActivityThread")
            return current_activity
        
    except Exception as e:
        print(f"ActivityThread.currentActivity() failed: {e}")
    
    # طريقة بديلة - الحصول على Application Context
    try:
        ActivityThread = autoclass('android.app.ActivityThread')
        current_application = ActivityThread.currentApplication()
        
        if current_application:
            print("Got application context")
            return current_application.getApplicationContext()
        
    except Exception as e:
        print(f"ActivityThread.currentApplication() failed: {e}")
    
    print("Could not get activity or context")
    return None

def request_contact_permissions() -> bool:
    """طلب صلاحيات جهات الاتصال"""
    if not autoclass:
        return False
    
    try:
        current_activity = get_activity()
        if not current_activity:
            return False
        
        print(f"Got activity/context: {current_activity}")
        
        # استخدام ContextCompat للتحقق من الصلاحيات (يعمل مع Activity و Context)
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        write_permission = ContextCompat.checkSelfPermission(
            current_activity, 
            Manifest.WRITE_CONTACTS
        )
        
        print(f"Permission status: {write_permission}")
        
        if write_permission == PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission is granted")
            return True
        else:
            print("WRITE_CONTACTS permission not granted")
            
            # محاولة طلب الصلاحية إذا كان Activity متاحًا
            try:
                ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
                permissions_array = [Manifest.WRITE_CONTACTS, Manifest.READ_CONTACTS]
                ActivityCompat.requestPermissions(
                    current_activity,
                    permissions_array,
                    100
                )
                print("Permission request sent")
                return True
            except Exception as e:
                print(f"Could not request permission: {e}")
                return False
        
    except Exception as e:
        print(f"Error in permission check: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_contact(name: str, phone: str) -> bool:
    """إضافة جهة اتصال"""
    if not autoclass or not name or not phone:
        return False
    
    try:
        current_activity = get_activity()
        if not current_activity:
            return False
        
        print(f"Got activity/context for adding contact: {current_activity}")
        
        # التحقق من الصلاحيات
        ContextCompat = autoclass('androidx.core.content.ContextCompat')
        Manifest = autoclass('android.Manifest$permission')
        PackageManager = autoclass('android.content.pm.PackageManager')
        
        write_permission = ContextCompat.checkSelfPermission(
            current_activity, 
            Manifest.WRITE_CONTACTS
        )
        
        if write_permission != PackageManager.PERMISSION_GRANTED:
            print("WRITE_CONTACTS permission not granted")
            return False
        
        print("Permission confirmed, creating contact")
        
        # استيراد الكلاسات
        ContentValues = autoclass('android.content.ContentValues')
        ContactsContract = autoclass('android.provider.ContactsContract')
        Data = autoclass('android.provider.ContactsContract$Data')
        RawContacts = autoclass('android.provider.ContactsContract$RawContacts')
        StructuredName = autoclass('android.provider.ContactsContract$CommonDataKinds$StructuredName')
        Phone = autoclass('android.provider.ContactsContract$CommonDataKinds$Phone')
        
        # الحصول على ContentResolver
        content_resolver = current_activity.getContentResolver()
        print("Got ContentResolver")
        
        # إنشاء جهة اتصال جديدة
        values = ContentValues()
        values.put(RawContacts.ACCOUNT_TYPE, None)
        values.put(RawContacts.ACCOUNT_NAME, None)
        
        raw_contact_uri = content_resolver.insert(RawContacts.CONTENT_URI, values)
        if not raw_contact_uri:
            print("Failed to create raw contact")
            return False
        
        raw_contact_id = int(raw_contact_uri.getLastPathSegment())
        print(f"Created raw contact with ID: {raw_contact_id}")
        
        # إضافة الاسم
        name_values = ContentValues()
        name_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        name_values.put(Data.MIMETYPE, StructuredName.CONTENT_ITEM_TYPE)
        name_values.put(StructuredName.DISPLAY_NAME, name)
        content_resolver.insert(Data.CONTENT_URI, name_values)
        print("Name added")
        
        # إضافة رقم الهاتف
        phone_values = ContentValues()
        phone_values.put(Data.RAW_CONTACT_ID, raw_contact_id)
        phone_values.put(Data.MIMETYPE, Phone.CONTENT_ITEM_TYPE)
        phone_values.put(Phone.NUMBER, phone)
        phone_values.put(Phone.TYPE, Phone.TYPE_MOBILE)
        content_resolver.insert(Data.CONTENT_URI, phone_values)
        print("Phone added")
        
        print(f"Contact '{name}' added successfully!")
        return True
        
    except Exception as e:
        print(f"Error adding contact: {e}")
        import traceback
        traceback.print_exc()
        return False
