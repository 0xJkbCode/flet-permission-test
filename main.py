import flet as ft
import flet_permission_handler as fph

def main(page: ft.Page):
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.appbar = ft.AppBar(title=ft.Text("اختبار صلاحيات جهات الاتصال"))
    ph = fph.PermissionHandler()
    page.overlay.append(ph)

    def check_permission(e):
        # We are now checking for CONTACTS permission
        o = ph.check_permission(fph.PermissionType.CONTACTS)
        page.add(ft.Text(f"Checked CONTACTS: {o}"))
        page.update()

    def request_permission(e):
        # We are now requesting CONTACTS permission
        o = ph.request_permission(fph.PermissionType.CONTACTS)
        page.add(ft.Text(f"Requested CONTACTS: {o}"))
        page.update()

    def open_app_settings(e):
        o = ph.open_app_settings()
        page.add(ft.Text(f"App Settings Opened: {o}"))
        page.update()

    page.add(
        ft.Text("الخطوة 1: اضغط لطلب الصلاحية", size=16),
        ft.ElevatedButton(
            "Request CONTACTS Permission",
            on_click=request_permission,
        ),
        ft.Text("الخطوة 2: اضغط للتحقق من الحالة", size=16),
        ft.ElevatedButton(
            "Check CONTACTS Permission Status",
            on_click=check_permission,
        ),
        ft.Divider(),
        ft.ElevatedButton("Open App Settings", on_click=open_app_settings),
    )

ft.app(main)