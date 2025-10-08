import flet as ft





def main(page: ft.Page):
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.appbar = ft.AppBar(title=ft.Text("اختبار صلاحيات"))
    ph = ft.PermissionHandler()
    page.overlay.append(ph)

    def check_permission(e):

        print("Type E is : ", dir(e))
        print("Data from E is : ", e.control.data)
        o = ph.check_permission(e.control.data)
        print("O is After check permission : ", o)
        page.add(ft.Text(f"Checked {e.control.data.name}: {o}"))

    def request_permission(e):
        o = ph.request_permission(e.control.data)
        page.add(ft.Text(f"Requested {e.control.data.name}: {o}"))
        print("O is After request permission : ", o)

    def open_app_settings(e):
        o = ph.open_app_settings()
        
        page.add(ft.Text(f"App Settings: {o}"))
        print("O is After open settings : ", o)

    page.add(
        ft.OutlinedButton(
            "اختبار صلاحيه جهات الاتصال",
            data=ft.PermissionType.STORAGE,
            on_click=check_permission,
        ),
        ft.OutlinedButton(
            "ارسال طلب الى صلاحيه جهات الاتصال",
            data=ft.PermissionType.STORAGE,
            on_click=request_permission,
        ),
        ft.OutlinedButton("Open App Settings", on_click=open_app_settings),
    )


ft.app(main)
