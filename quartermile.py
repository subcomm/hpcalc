import math
import flet as ft

# ---- Core 1/4-mile formulas ----

def hp_from_et_weight(et, weight):
    """Estimate flywheel HP from 1/4-mile ET (sec) and vehicle weight (lbs)."""
    return weight / ((et / 5.825) ** 3)


def et_from_hp_weight(hp, weight):
    """Estimate 1/4-mile ET (sec) from HP and weight."""
    return 5.825 * ((weight / hp) ** (1 / 3))


def hp_from_mph_weight(mph, weight):
    """Estimate flywheel HP from 1/4-mile trap speed (mph) and weight."""
    return weight * ((mph / 234) ** 3)


def mph_from_hp_weight(hp, weight):
    """Estimate 1/4-mile MPH from HP and weight."""
    return 234 * ((hp / weight) ** (1 / 3))


def hp_to_kw(hp):
    return hp * 0.7457


def kw_to_hp(kw):
    return kw / 0.7457


# ---- Simple 1/4 <-> 1/8 conversion helpers (approximate) ----
# These are common ballpark ratios, not exact physics.
ET_1_8_FROM_1_4_FACTOR = 0.66   # ET_1/8 ≈ 0.66 * ET_1/4
MPH_1_8_FROM_1_4_FACTOR = 0.79  # MPH_1/8 ≈ 0.79 * MPH_1/4

def et_1_8_from_1_4(et_qtr):
    return et_qtr * ET_1_8_FROM_1_4_FACTOR

def et_1_4_from_1_8(et_eighth):
    return et_eighth / ET_1_8_FROM_1_4_FACTOR

def mph_1_8_from_1_4(mph_qtr):
    return mph_qtr * MPH_1_8_FROM_1_4_FACTOR

def mph_1_4_from_1_8(mph_eighth):
    return mph_eighth / MPH_1_8_FROM_1_4_FACTOR


# ---- Flet UI ----

def main(page: ft.Page):
    page.title = "ET / MPH / HP Calculator (1/4 & 1/8 mile)"
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Distance selector (1/4 or 1/8)
    distance_dd = ft.Dropdown(
        label="Distance for ET & MPH inputs",
        options=[
            ft.dropdown.Option("1/4 mile"),
            ft.dropdown.Option("1/8 mile"),
        ],
        value="1/4 mile",
        width=200,
    )

    # Input fields
    weight_tf = ft.TextField(
        label="Weight (lbs)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    et_tf = ft.TextField(
        label="ET (seconds)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        helper_text="Uses distance selected above",
    )
    mph_tf = ft.TextField(
        label="Trap Speed (MPH)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        helper_text="Uses distance selected above",
    )
    hp_tf = ft.TextField(
        label="Horsepower (flywheel)",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    # Output text
    result_text = ft.Text("", selectable=True, size=14)

    def show_error(msg: str):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def parse_float(field: ft.TextField, name: str):
        if not field.value:
            raise ValueError(f"{name} is required.")
        try:
            return float(field.value)
        except ValueError:
            raise ValueError(f"{name} must be a number.")

    def using_quarter_mile() -> bool:
        return distance_dd.value == "1/4 mile"

    # -------- Button handlers --------

    def on_from_et_click(e):
        try:
            weight = parse_float(weight_tf, "Weight")
            et_input = parse_float(et_tf, "ET")

            # Normalize to 1/4-mile ET for the formulas
            if using_quarter_mile():
                et_qtr = et_input
            else:
                et_qtr = et_1_4_from_1_8(et_input)

            # Core math in 1/4-mile domain
            hp = hp_from_et_weight(et_qtr, weight)
            mph_qtr = mph_from_hp_weight(hp, weight)
            kw = hp_to_kw(hp)

            # Derived 1/8-mile estimates
            et_1_8 = et_1_8_from_1_4(et_qtr)
            mph_1_8 = mph_1_8_from_1_4(mph_qtr)

            # Update primary fields (respecting selected distance)
            if using_quarter_mile():
                et_tf.value = f"{et_qtr:.3f}"
                mph_tf.value = f"{mph_qtr:.1f}"
            else:
                et_tf.value = f"{et_1_8:.3f}"
                mph_tf.value = f"{mph_1_8:.1f}"

            hp_tf.value = f"{hp:.1f}"

            result_text.value = (
                "From ET:\n"
                f"  HP ≈ {hp:.1f} hp ({kw:.1f} kW)\n\n"
                f"  1/4-mile: ET ≈ {et_qtr:.3f} s, MPH ≈ {mph_qtr:.1f}\n"
                f"  1/8-mile: ET ≈ {et_1_8:.3f} s, MPH ≈ {mph_1_8:.1f}\n"
                "(1/8-mile values are approximate conversions from 1/4-mile.)"
            )
            page.update()

        except ValueError as ex:
            show_error(str(ex))

    def on_from_mph_click(e):
        try:
            weight = parse_float(weight_tf, "Weight")
            mph_input = parse_float(mph_tf, "MPH")

            # Normalize to 1/4-mile MPH
            if using_quarter_mile():
                mph_qtr = mph_input
            else:
                mph_qtr = mph_1_4_from_1_8(mph_input)

            # Core math in 1/4-mile domain
            hp = hp_from_mph_weight(mph_qtr, weight)
            et_qtr = et_from_hp_weight(hp, weight)
            kw = hp_to_kw(hp)

            # Derived 1/8-mile estimates
            et_1_8 = et_1_8_from_1_4(et_qtr)
            mph_1_8 = mph_1_8_from_1_4(mph_qtr)

            # Update primary fields
            if using_quarter_mile():
                mph_tf.value = f"{mph_qtr:.1f}"
                et_tf.value = f"{et_qtr:.3f}"
            else:
                mph_tf.value = f"{mph_1_8:.1f}"
                et_tf.value = f"{et_1_8:.3f}"

            hp_tf.value = f"{hp:.1f}"

            result_text.value = (
                "From MPH:\n"
                f"  HP ≈ {hp:.1f} hp ({kw:.1f} kW)\n\n"
                f"  1/4-mile: ET ≈ {et_qtr:.3f} s, MPH ≈ {mph_qtr:.1f}\n"
                f"  1/8-mile: ET ≈ {et_1_8:.3f} s, MPH ≈ {mph_1_8:.1f}\n"
                "(1/8-mile values are approximate conversions from 1/4-mile.)"
            )
            page.update()

        except ValueError as ex:
            show_error(str(ex))

    def on_from_hp_click(e):
        try:
            weight = parse_float(weight_tf, "Weight")
            hp = parse_float(hp_tf, "HP")

            # Core math in 1/4-mile domain
            et_qtr = et_from_hp_weight(hp, weight)
            mph_qtr = mph_from_hp_weight(hp, weight)
            kw = hp_to_kw(hp)

            # 1/8-mile estimates
            et_1_8 = et_1_8_from_1_4(et_qtr)
            mph_1_8 = mph_1_8_from_1_4(mph_qtr)

            # Update fields based on selected distance
            if using_quarter_mile():
                et_tf.value = f"{et_qtr:.3f}"
                mph_tf.value = f"{mph_qtr:.1f}"
            else:
                et_tf.value = f"{et_1_8:.3f}"
                mph_tf.value = f"{mph_1_8:.1f}"

            result_text.value = (
                "From HP:\n"
                f"  {hp:.1f} hp = {kw:.1f} kW\n\n"
                f"  1/4-mile: ET ≈ {et_qtr:.3f} s, MPH ≈ {mph_qtr:.1f}\n"
                f"  1/8-mile: ET ≈ {et_1_8:.3f} s, MPH ≈ {mph_1_8:.1f}\n"
                "(1/8-mile values are approximate conversions from 1/4-mile.)"
            )
            page.update()

        except ValueError as ex:
            show_error(str(ex))

    # Buttons
    from_et_btn = ft.ElevatedButton("Compute from ET", on_click=on_from_et_click)
    from_mph_btn = ft.ElevatedButton("Compute from MPH", on_click=on_from_mph_click)
    from_hp_btn = ft.ElevatedButton("Compute from HP", on_click=on_from_hp_click)

    # Layout
    page.add(
        ft.Text("Quarter- & Eighth-Mile ET / MPH / HP Calculator", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(
            "1/4-mile formulas; 1/8-mile values are approximate conversions.",
            size=12,
            italic=True,
        ),
        ft.Divider(),
        distance_dd,
        ft.Row([weight_tf]),
        ft.Row([et_tf, mph_tf, hp_tf], wrap=True),
        ft.Row([from_et_btn, from_mph_btn, from_hp_btn], wrap=True, spacing=10),
        ft.Divider(),
        result_text,
    )


if __name__ == "__main__":
    # For browser UI, use: ft.app(target=main, view=ft.WEB_BROWSER)
    # ft.app(target=main)
    ft.app(target=main, view=ft.WEB_BROWSER)