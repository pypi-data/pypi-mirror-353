import flet as ft

class InteractiveGalleryView(ft.View):
    def __init__(self, page, title="Gallery", items=None, start_index=0, back_route="/"):
        super().__init__(
            route="/gallery",
            vertical_alignment="center",
            horizontal_alignment="center",
        )
        self.page = page
        self.items = items if items else []
        self.index = start_index
        self.appbar_visible = True
        self.zoomed = False
        self.back_route = back_route

        self.counter_text = ft.Text(
            f"{self.index + 1} / {len(self.items)}",
            size=16,
            color=ft.Colors.WHITE
        )

        self.appbar = ft.AppBar(
            title=ft.Text(title),
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.go_back),
            actions=[
                ft.IconButton(
                    ft.Icons.INFO,
                    on_click=self.show_counter,
                ),
                ft.Container(
                    content=self.counter_text,
                    padding=10,
                    alignment=ft.alignment.center,
                )
            ],
            visible=True
        )

        self.viewer = self.build_viewer()

        self.image_container = ft.AnimatedSwitcher(
            content=self.viewer,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=100
        )

        self.controls = [
            self.appbar,
            ft.GestureDetector(
                on_horizontal_drag_end=self.on_horizontal_drag,
                on_vertical_drag_end=self.on_vertical_drag,
                on_double_tap=self.on_double_tap,
                on_tap=self.toggle_appbar,
                on_scale_start=self.on_interaction_start,
                on_scale_end=self.on_interaction_end,
                content=ft.Container(
                    content=self.image_container,
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
        ]

    def build_viewer(self):
        self.viewer_control = ft.InteractiveViewer(
            content=ft.Container(
                expand=True,
                content=ft.Image(
                    src=self.items[self.index],
                    fit=ft.ImageFit.COVER,
                    expand=True,
                    filter_quality=ft.FilterQuality.HIGH
                ),
                alignment=ft.alignment.center
            ),
            scale_enabled=True,
            pan_enabled=True,
            boundary_margin=0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            interaction_end_friction_coefficient=0.00001,
            min_scale=1.0,
            max_scale=3.0,
            trackpad_scroll_causes_scale=True,
            alignment=ft.alignment.center
        )
        return self.viewer_control

    def update_display(self):
        self.viewer = self.build_viewer()
        self.image_container.content = self.viewer
        self.counter_text.value = f"{self.index + 1} / {len(self.items)}"
        self.page.update()

    def go_back(self, e):
        self.page.views.pop()
        self.page.go(self.back_route or "/")

    def on_horizontal_drag(self, e):
        if e.primary_velocity < 0:
            self.next_item()
        else:
            self.prev_item()

    def on_vertical_drag(self, e):
        if e.primary_velocity > 800:
            self.page.views.pop()
            self.page.go("/")

    def next_item(self):
        if self.index < len(self.items) - 1:
            self.index += 1
            self.update_display()

    def prev_item(self):
        if self.index > 0:
            self.index -= 1
            self.update_display()

    def toggle_appbar(self, e):
        self.appbar_visible = not self.appbar_visible
        self.appbar.visible = self.appbar_visible
        self.page.update()

    def on_interaction_start(self, e):
        if self.appbar_visible:
            self.appbar_visible = False
            self.appbar.visible = False
            self.page.update()

    def on_interaction_end(self, e):
        pass

    def on_double_tap(self, e):
        if not self.zoomed:
            self.viewer_control.scale = 2.0
            self.zoomed = True
        else:
            self.viewer_control.scale = 1.0
            self.zoomed = False
        self.page.update()

    def show_counter(self, e):
        print(f"Image {self.index + 1} of {len(self.items)}")


# # Example Usage
# def main(page: ft.Page):
#     page.window.always_on_top = True
#     page.title = "Fullscreen Gallery"

#     images = [
#         "https://picsum.photos/id/1015/1080/1920",
#         "https://picsum.photos/id/1016/1080/1920",
#         "https://picsum.photos/id/1018/1080/1920",
#         "https://picsum.photos/id/1019/1080/1920",
#     ]

#     def open_gallery(e):
#         gallery_view = InteractiveGalleryView(page, title="Gallery View", items=images,back_route="/lolo")
#         page.views.append(gallery_view)
#         page.go("/gallery")

#     page.add(ft.ElevatedButton("Open Gallery", on_click=open_gallery))

# ft.app(target=main)