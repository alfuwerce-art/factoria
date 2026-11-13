#!/usr/bin/env python3
"""Factoria HumanoidBase v3: компактный коренастый орк по утверждённому эталону.

Архитектура та же, что в v2 (единый Sculpt → разметка частей → зазор 1 воксель),
но силуэт, лицо и одежда перестроены под утверждённый визуальный референс:
короткие массивные конечности, крупная голова, тёмная одежда с красными акцентами,
один наплечник, диагональный ремень, повязка на лбу, хохолок, булава и сумка
как отдельные слои.

Числа — из профиля (JSON). Геометрия CubeGame не используется.
Перед = -Y. x — влево/вправо (x>0 — левая сторона персонажа). z — вверх, 0 = пол.
"""

from __future__ import annotations

from voxelkit import Grid, Sculpt

MODULE_ORDER = [
    "head", "eyes", "brows", "mouth", "hair", "torso", "pelvis",
    "upper_arm_L", "forearm_L", "hand_L", "upper_arm_R", "forearm_R", "hand_R",
    "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
    "pouch", "weapon_club",
]


class HumanoidBuilder:
    def __init__(self, profile: dict):
        self.profile = profile
        self.L = profile["landmarks"]
        self.W = profile["widths"]
        self.face = profile["face"]
        self.hair_cfg = profile["hair"]
        self.outfit = profile["outfit"]
        self.weapon_cfg = profile.get("weapon", {})
        self.detail = profile["detail"]
        self.pal = profile["palette"]
        self.s = Sculpt()
        self.cut_log: list[dict] = []
        self.front = profile["surfaces"]

    def m(self, key: str, fallback: str | None = None) -> str:
        if key in self.pal:
            return key
        if fallback and fallback in self.pal:
            return fallback
        raise KeyError(f"нет материала {key}")

    # -------------------------------------------------------------------- масса --
    def build_mass(self):
        s, W, L = self.s, self.W, self.L
        skin = self.m("skin")
        waist = L["waist"]

        def torso_part(z):
            return "pelvis" if z < waist else "torso"

        s.tube([
            (L["crotch"], W["pelvis_width"], W["pelvis_depth"], 0.0, -0.2),
            (L["crotch"] + 3, W["pelvis_width"] - 1, W["pelvis_depth"] + 0.5, 0.0, -0.3),
            (waist - 1, W["waist_width"], W["waist_depth"], 0.0, -0.4),
            (waist + 1, W["waist_width"] + 1, W["waist_depth"] + 0.5, 0.0, -0.5),
            (waist + 4, W["chest_width"] - 1, W["chest_depth"] - 1, 0.0, -0.6),
            (L["shoulder"] - 3, W["chest_width"], W["chest_depth"], 0.0, -0.7),
            (L["shoulder"] - 1, W["chest_width"], W["chest_depth"], 0.0, -0.7),
            (L["shoulder"], W["chest_width"] - 1, W["chest_depth"] - 1, 0.0, -0.5),
            (L["shoulder"] + 1, W["neck_width"] + 4, W["neck_depth"], 0.0, 0.0),
            (L["neck_top"], W["neck_width"], W["neck_depth"] - 1, 0.0, 0.0),
        ], torso_part, skin, "LARGE", p=4.2)

        # короткие массивные ноги
        cx = W["leg_center_x"]

        def leg_part(z):
            return "thigh_L" if z >= L["knee"] else "shin_L"

        s.tube([
            (L["ankle"], 9, 10, cx, 0.0),
            (L["ankle"] + 3, 10, 11, cx, 0.3),
            (L["knee"] - 2, W["shin_width"], W["shin_depth"], cx, 0.2),
            (L["knee"], W["shin_width"], W["shin_depth"], cx, 0.0),
            (L["knee"] + 3, W["thigh_width"] - 1, W["thigh_depth"] - 1, cx, -0.3),
            (L["crotch"] - 1, W["thigh_width"], W["thigh_depth"], cx, -0.3),
        ], leg_part, skin, "LARGE", p=4.0)

        # короткие толстые руки
        acx = W["arm_center_x"]

        def arm_part(z):
            return "upper_arm_L" if z >= L["elbow"] else "forearm_L"

        s.tube([
            (L["wrist"] + 1, 7, 7, acx, -1.0),
            (L["wrist"] + 3, 8, 8, acx, -1.0),
            (L["elbow"] - 1, 8, 8, acx, -1.0),
            (L["elbow"], 7.5, 8, acx, -1.0),
            (L["elbow"] + 2, 8, 9, acx, -1.0),
            (L["shoulder"] - 2, 8, 9, acx, -1.0),
            (L["shoulder"], 7, 8, acx, -1.0),
        ], arm_part, skin, "LARGE", p=3.8)

        # крупные кисти-«рукавицы»
        hw = W["hand_width"]
        x0 = int(round(acx - hw / 2.0))
        palm_top = L["wrist"] - 1
        palm_bottom = L["wrist"] - 4
        s.box(x0, x0 + hw - 1, -6, -1, palm_bottom, palm_top, "hand_L", skin, "LARGE")
        s.box(x0, x0 + hw - 1, -6, -2, L["hand_tip"], palm_bottom - 1, "hand_L", skin, "LARGE")
        s.box(x0 - 1, x0 - 1, -6, -3, palm_bottom, palm_bottom + 1, "hand_L", skin, "MEDIUM")

        # устойчивые широкие стопы
        fc = W["leg_center_x"]
        fw, fl = W["foot_width"], W["foot_length"]
        s.tube([
            (L["ground"], fw, fl, fc, -3.0),
            (L["ground"] + 2, fw, fl, fc, -3.0),
            (L["ankle"] - 1, fw - 1, fl - 3, fc, -2.0),
            (L["ankle"], fw - 2, fl - 5, fc, -1.0),
        ], "foot_L", skin, "LARGE", p=5.0)

    # ------------------------------------------------------------------- голова --
    def build_head(self):
        s, W, F = self.s, self.W, self.face
        L = self.L
        skin = self.m("skin")
        chin, top = L["chin"], L["skull_top"]
        fy = self.front["head"]
        hw = W["head_width"]
        cy = W["head_center_y"]

        s.tube([
            (chin, 12, 13, 0.0, cy - 0.5),
            (chin + 1, 14, 14, 0.0, cy - 0.3),
            (chin + 2, 15, 15, 0.0, cy - 0.1),
            (chin + 3, hw, W["head_depth"], 0.0, cy),
            (L["eye"] + 1, hw, W["head_depth"], 0.0, cy),
            (L["brow"] + 1, hw, W["head_depth"], 0.0, cy),
            (top - 3, hw, W["head_depth"] - 1, 0.0, cy),
            (top - 1, hw - 2, W["head_depth"] - 2, 0.0, cy),
            (top, hw - 4, W["head_depth"] - 4, 0.0, cy),
        ], "head", skin, "LARGE", p=4.4)

        # тяжёлая встроенная челюсть
        s.box(-6, 5, fy - 1, fy, chin, chin + 1, "head", skin, "MEDIUM")
        # массивное надбровье
        s.box(-hw // 2, hw // 2 - 1, fy - 1, fy - 1, L["brow"] - 1, L["brow"], "head",
              skin, "MEDIUM")
        # скулы
        for sx in (-1, 1):
            x = hw // 2 - 2
            xx = x if sx > 0 else -1 - x
            s.box(xx, xx, fy - 1, fy - 1, L["eye"] - 1, L["eye"], "head", skin, "MEDIUM")
        # широкий плоский нос
        nw = int(F["nose_width"])
        s.box(-(nw // 2), nw // 2 - 1, fy - 1, fy - 1, L["eye"] - 2, L["eye"] - 1, "head",
              self.m("skin_light"), "MEDIUM")
        for xx in (-(nw // 2), nw // 2 - 1):
            s.put(xx, fy - 1, L["eye"] - 2, "head", self.m("skin_shadow"), "SMALL")
        # большие уши: широкое основание, заострённый верх, тёмная внутренняя часть
        for sx in (-1, 1):
            for i, (dz0, dz1, dy0, dy1) in enumerate(((0, 5, -4, 2), (1, 5, -3, 1), (2, 4, -2, 0))):
                x = hw // 2 + i
                xx = x if sx > 0 else -1 - x
                s.box(xx, xx, dy0, dy1, L["eye"] - 2 + dz0, L["eye"] - 2 + dz1,
                      "head", skin, "MEDIUM")
            s.box(hw // 2 if sx > 0 else -1 - (hw // 2),
                  hw // 2 if sx > 0 else -1 - (hw // 2),
                  -2, 0, L["eye"] - 1, L["eye"] + 1, "head", self.m("skin_shadow"), "SMALL")
        # светлая «морда» вокруг пасти (небольшая, как на эталоне)
        s.repaint(-4, 3, fy - 1, fy, L["eye"] - 4, L["eye"] - 3, self.m("skin_light"), "MEDIUM",
                  parts=("head",))
        # глазницы: узкие щели 3x1
        s.carve(-7, -5, fy, fy, L["eye"], L["eye"])
        s.carve(4, 6, fy, fy, L["eye"], L["eye"])
        s.repaint(-7, 6, fy + 1, fy + 1, L["eye"] - 1, L["eye"] - 1,
                  self.m("skin_shadow"), "SMALL", parts=("head",))
        s.repaint(-7, 6, fy - 1, fy - 1, L["eye"] + 1, L["eye"] + 1,
                  self.m("skin_shadow"), "SMALL", parts=("head",))
        # пасть (зубы и клыки — модуль mouth)
        s.carve(-3, 2, fy, fy, L["eye"] - 4, L["eye"] - 4)
        s.repaint(-3, 2, fy - 1, fy - 1, L["eye"] - 4, L["eye"] - 4,
                  self.m("skin_dark"), "SMALL", parts=("head",))
        # шрамы и боевая раскраска
        if F.get("scars", True):
            for i in range(2):
                s.put(hw // 2 - 2, fy - 1, L["eye"] + i, "head", self.m("scar"), "SMALL")
            for i in range(2):
                s.put(3, fy - 1, L["eye"] - 3 - i, "head", self.m("skin_dark"), "SMALL")

    def build_face(self):
        s, W, L = self.s, self.W, self.L
        fy = self.front["head"]
        # узкие злые глаза: тёмная щель + янтарный зрачок по центру
        for sx in (-1, 1):
            ex0 = -7 if sx < 0 else 4
            s.box(ex0, ex0 + 2, fy, fy, L["eye"], L["eye"], "eyes",
                  self.m("eye_sclera"), "SMALL")
            s.put(ex0 + 1, fy, L["eye"], "eyes", self.m("eye_iris"), "SMALL")
        # толстые брови: у переносицы ниже, к виску выше
        for sx in (-1, 1):
            for i, dz in enumerate((0, 0, 1, 1)):
                x = 1 + i
                xx = x if sx > 0 else -1 - x
                s.box(xx, xx, fy - 1, fy - 1, L["eye"] + 2 + dz, L["eye"] + 3 + dz,
                      "brows", self.m("hair"), "SMALL")
        # пасть: тёмная щель и два клыка по углам, растущие вверх
        mw = int(self.face["mouth_width"])
        s.box(-mw // 2 + 1, mw // 2 - 2, fy, fy, L["eye"] - 4, L["eye"] - 4, "mouth",
              self.m("mouth"), "SMALL")
        for sx in (-1, 1):
            for i in range(int(self.face["tusk_length"]) - 1):
                x = 3 + (i // 2) if sx > 0 else -4 - (i // 2)
                s.put(x, fy - 1, L["eye"] - 4 + i, "mouth", self.m("ivory"), "SMALL")
        # тень под бровью и под губой
        s.box(-2, 1, fy - 1, fy - 1, L["eye"] - 5, L["eye"] - 5, "mouth",
              self.m("skin_shadow"), "SMALL")
        s.repaint(-6, 5, fy, fy, L["eye"] + 1, L["eye"] + 1, self.m("skin_shadow"), "SMALL",
                  parts=("head",))

    def build_hair(self):
        cfg = self.hair_cfg
        if not cfg.get("enabled", True):
            return
        s, W, L = self.s, self.W, self.L
        hair = self.m("hair")
        hw = W["head_width"]
        top = L["skull_top"]
        # небольшой верхний хохолок
        s.box(-2, 1, -2, 1, top + 1, top + 1, "hair", hair, "MEDIUM")
        s.box(-1, 0, -1, 0, top + 2, top + 3, "hair", hair, "MEDIUM")
        s.box(-1, 0, 0, 1, top + 4, top + 4, "hair", hair, "SMALL")
        # тёмные пряди по бокам под повязкой
        for sx in (-1, 1):
            x = hw // 2 - 1
            xx = x if sx > 0 else -1 - x
            s.box(xx, xx, 3, 5, L["eye"] + 1, top - 1, "hair", hair, "SMALL")
        # красная повязка на лбу + узел и хвосты
        red = self.m("red")
        band_z0, band_z1 = L["brow"] + 2, L["brow"] + 3
        s.repaint(-hw // 2, hw // 2 - 1, self.front["head"], self.front["head"] + 1,
                  band_z0, band_z1, red, "MEDIUM", parts=("head",))
        for sx in (-1, 1):
            x = hw // 2 - 1
            xx = x if sx > 0 else -1 - x
            s.repaint(xx, xx, -8, 4, band_z0, band_z1, red, "MEDIUM", parts=("head",))
        s.repaint(-hw // 2, hw // 2 - 1, 4, 5, band_z0, band_z1, red, "MEDIUM",
                  parts=("head",))
        s.box(-1, 0, 5, 6, band_z0 - 1, band_z1, "head", self.m("red_dark"), "SMALL")
        for sx in (-1, 1):
            x = 2
            xx = x if sx > 0 else -1 - x
            s.box(xx, xx, 6, 6, band_z0 - 4, band_z0 - 1, "head", self.m("red_dark"), "SMALL")

    # ---------------------------------------------------------- мышцы и детали ---
    def build_muscles(self):
        s, W, L = self.s, self.W, self.L
        light, shadow = self.m("skin_light"), self.m("skin_shadow")
        bulge = float(self.detail.get("muscle_bulge", 1.0))
        acx, lcx = W["arm_center_x"], W["leg_center_x"]
        # бицепс/трицепс
        s.ellipsoid(acx, -5.2, L["elbow"] + 2.5, 3.0 * bulge, 1.8, 2.8, "upper_arm_L",
                    light, "MEDIUM", p=2.6)
        s.ellipsoid(acx, 3.4, L["elbow"] + 2.0, 2.6, 1.6, 2.6, "upper_arm_L", shadow,
                    "MEDIUM", p=2.6)
        # предплечье
        s.ellipsoid(acx, -4.6, L["wrist"] + 3.0, 3.0, 1.8, 2.6, "forearm_L", light,
                    "MEDIUM", p=2.6)
        # квадрицепс/икра
        s.ellipsoid(lcx, -5.8, L["knee"] + 5.0, 4.2, 1.8, 3.8, "thigh_L", light,
                    "MEDIUM", p=2.8)
        s.ellipsoid(lcx, 4.6, L["knee"] - 5.0, 3.6, 1.8, 3.4, "shin_L", light,
                    "MEDIUM", p=2.8)

    # ---------------------------------------------------------------- одежда -----
    def build_outfit(self):
        s, W, L, O = self.s, self.W, self.L, self.outfit
        tunic, tunic_d = self.m("tunic"), self.m("tunic_dark")
        pants, boot, sole = self.m("pants"), self.m("boot"), self.m("boot_sole")
        leather, leather_d = self.m("leather"), self.m("leather_dark")
        red, red_d = self.m("red"), self.m("red_dark")
        metal, bronze = self.m("metal"), self.m("bronze")
        metal_d = self.m("metal_dark")
        hw = W["head_width"]
        tf, pf, lf, sf, ff = (self.front["torso"], self.front["pelvis"], self.front["leg"],
                              self.front["shin"], self.front["foot"])
        acx, lcx = int(W["arm_center_x"]), W["leg_center_x"]

        # === туника на торсе
        if O.get("tunic", True):
            s.repaint(-W["chest_width"], W["chest_width"], -8, 6, L["waist"] + 1, L["shoulder"] - 1,
                      tunic, "MEDIUM", parts=("torso",))
            s.repaint(-W["chest_width"], W["chest_width"], -8, 6, L["waist"] + 1, L["waist"] + 1,
                      tunic_d, "SMALL", parts=("torso",))
            s.repaint(-W["chest_width"], W["chest_width"], -8, 6, L["shoulder"], L["neck_top"] - 1,
                      tunic_d, "SMALL", parts=("torso",))
            # вертикальный шов и застёжка
            s.repaint(-1, 0, tf - 1, tf, L["waist"] + 2, L["shoulder"] - 2, tunic_d, "SMALL",
                      parts=("torso",))
            for zz in (L["waist"] + 4, L["waist"] + 7):
                s.put(-1, tf - 1, zz, "torso", bronze, "SMALL")
            # короткие рукава
            s.repaint(acx - 5, acx + 4, -6, 3, L["shoulder"] - 2, L["shoulder"],
                      tunic, "MEDIUM", parts=("upper_arm_L",))

        # === штаны
        if O.get("pants", True):
            for part, z0, z1 in (("thigh_L", L["knee"] + 1, L["crotch"] - 1),
                                 ("shin_L", L["ankle"] + 1, L["knee"] - 1)):
                s.repaint(lcx - 7, lcx + 6, -8, 6, z0, z1, pants, "MEDIUM", parts=(part,))
            # заплаты на коленях
            s.repaint(lcx - 5, lcx + 4, lf - 1, lf, L["knee"] + 1, L["knee"] + 2, leather_d,
                      "SMALL", parts=("thigh_L",))

        # === сапоги
        if O.get("boots", True):
            fw, fl = W["foot_width"], W["foot_length"]
            fx0, fx1 = lcx - fw // 2, lcx + fw // 2 - 1
            s.repaint(fx0, fx1, ff, 4, 1, L["ankle"], boot, "LARGE", parts=("foot_L",))
            s.repaint(fx0, fx1, ff, 4, L["ground"], L["ground"], sole, "SMALL",
                      parts=("foot_L",))
            s.box(fx0, fx1, ff + 3, ff + 3, 1, L["ankle"], "foot_L", leather, "MEDIUM")
            s.repaint(lcx - 3, lcx + 2, ff, ff + 1, 2, 3, metal, "SMALL", parts=("foot_L",))

        # === широкий красный пояс + пряжка
        if O.get("sash", True):
            belt_z0, belt_z1 = L["waist"] - 2, L["waist"] - 1
            s.tube([(belt_z0, W["waist_width"] + 2, W["waist_depth"] + 2, 0.0, -0.3),
                    (belt_z1, W["waist_width"] + 2, W["waist_depth"] + 2, 0.0, -0.3)],
                   "pelvis", red, "MEDIUM", p=3.2)
            s.box(-2, 1, pf - 2, pf - 1, belt_z0, belt_z1, "pelvis", metal, "MEDIUM")
            s.put(-1, pf - 2, belt_z0 + 1, "pelvis", bronze, "SMALL")
            # тёмный ремень ниже
            s.tube([(belt_z0 - 1, W["waist_width"] + 1, W["waist_depth"] + 1, 0.0, -0.3),
                    (belt_z0 - 1, W["waist_width"] + 1, W["waist_depth"] + 1, 0.0, -0.3)],
                   "pelvis", leather_d, "SMALL", p=3.2)

        # === красная ткань спереди и сзади (узкая, с рваным низом)
        if O.get("loincloth", True):
            hem = L["crotch"] - 6
            for zz in range(hem, L["waist"] - 2):
                half = 2 if zz > hem + 2 else 1
                s.box(-half, half + 1, pf - 1, pf, zz, zz, "pelvis", red, "MEDIUM")
            s.carve(-1, -1, pf - 1, pf, hem, hem)
            s.carve(2, 2, pf - 1, pf, hem, hem)
            s.repaint(-2, 3, pf - 1, pf, hem, hem, red_d, "SMALL", parts=("pelvis",))
            for zz in range(L["crotch"] - 1, L["waist"] - 2):
                s.box(-4, 3, 5, 6, zz, zz, "pelvis", red_d, "MEDIUM")

        # === диагональный ремень через грудь
        if O.get("diagonal_strap", True):
            steps = 9
            for i in range(steps):
                t = i / (steps - 1)
                x = int(round(6 * (1 - t) + (-7) * t))
                z = int(round((L["shoulder"] - 1) * (1 - t) + (L["waist"] + 1) * t))
                s.box(x, x + 1, tf - 1, tf, z, z, "torso", leather, "MEDIUM")
            s.box(-1, 0, tf - 1, tf - 1, L["waist"] + 5, L["waist"] + 6, "torso", bronze, "SMALL")

        # === один тяжёлый наплечник (по профилю): кожаные пластины + железная кромка
        side = str(O.get("pauldron_side", "RIGHT")).upper()
        sgn = 1 if side == "LEFT" else -1
        ax0, ax1 = acx - 5, acx + 2

        def srang(x0, x1):
            return (x0, x1) if sgn > 0 else (-1 - x1, -1 - x0)

        for z0, x0, x1, y0, y1, mat, lvl in (
            (L["shoulder"] + 1, ax0, ax1 - 1, tf - 1, 2, leather, "MEDIUM"),
            (L["shoulder"] - 1, ax0, ax1, tf - 2, 2, leather, "MEDIUM"),
            (L["shoulder"] - 3, ax0 + 1, ax1, tf - 1, 1, leather_d, "MEDIUM"),
        ):
            xa, xb = srang(x0, x1)
            s.box(xa, xb, y0, y1, z0, z0 + 1, "torso", mat, lvl)
        # железная кромка по нижнему краю и бронзовые заклёпки
        xa, xb = srang(ax0, ax1)
        s.box(xa, xb, tf - 2, tf - 2, L["shoulder"] - 3, L["shoulder"] - 1, "torso",
              metal_d, "SMALL")
        for xx in (ax0, ax1 - 1):
            s.put(xx if sgn > 0 else -1 - xx, tf - 2, L["shoulder"], "torso", bronze, "SMALL")

        # === наручи
        for _ in range(int(O.get("bracers", 2))):
            s.tube([(L["wrist"] + 2, W["forearm_width"] + 1.5, W["forearm_depth"] + 1.5,
                     W["arm_center_x"], -1.0),
                    (L["wrist"] + 4, W["forearm_width"] + 1.5, W["forearm_depth"] + 1.5,
                     W["arm_center_x"], -1.0)],
                   "forearm_L", leather, "MEDIUM", p=3.4)
            s.box(acx - 3, acx + 3, -6, -5, L["wrist"] + 4, L["wrist"] + 4, "forearm_L",
                  bronze, "SMALL")

        # === сумка на правом бедре
        if O.get("pouch", True):
            s.box(-10, -7, 2, 6, L["crotch"] + 1, L["crotch"] + 5, "pouch", leather_d, "MEDIUM")
            s.box(-10, -7, 2, 6, L["crotch"] + 5, L["crotch"] + 5, "pouch", leather, "SMALL")
            s.put(-9, 2, L["crotch"] + 3, "pouch", bronze, "SMALL")
            s.box(-8, -7, 1, 2, L["waist"] - 3, L["waist"] - 2, "pouch", leather_d, "SMALL")

    # ---------------------------------------------------------------- оружие -----
    def build_weapon(self):
        cfg = self.weapon_cfg
        if not cfg.get("enabled", True):
            return
        s, W, L = self.s, self.W, self.L
        wood, stone = self.m("wood"), self.m("stone")
        leather_d = self.m("leather_dark")
        # булава в правой руке: толстое древко проходит через кулак
        s.box(-15, -13, -4, -2, L["hand_tip"], L["shoulder"] + 3, "weapon_club", wood,
              "MEDIUM")
        s.box(-15, -13, -5, -1, L["wrist"] - 2, L["wrist"] + 1, "weapon_club", leather_d,
              "SMALL")
        s.box(-15, -13, -5, -1, L["shoulder"] + 1, L["shoulder"] + 2, "weapon_club",
              leather_d, "SMALL")
        # каменная голова с фаской и гранями
        s.box(-19, -13, -7, -1, L["shoulder"] + 4, L["shoulder"] + 7, "weapon_club",
              stone, "MEDIUM")
        s.box(-18, -14, -6, -2, L["shoulder"] + 8, L["shoulder"] + 8, "weapon_club",
              stone, "MEDIUM")
        s.box(-18, -14, -6, -2, L["shoulder"] + 3, L["shoulder"] + 3, "weapon_club",
              stone, "MEDIUM")
        s.box(-19, -18, -4, -2, L["shoulder"] + 4, L["shoulder"] + 7, "weapon_club",
              stone, "SMALL")
        s.put(-16, -7, L["shoulder"] + 6, "weapon_club", self.m("metal_light"), "SMALL")
        s.put(-15, -7, L["shoulder"] + 5, "weapon_club", self.m("metal_dark"), "SMALL")
        # фасетка каменной головы (снимаем углы)
        for cx_, cy_ in ((-19, -7), (-13, -7), (-19, -1), (-13, -1)):
            s.carve(cx_, cx_, cy_, cy_, L["shoulder"] + 4, L["shoulder"] + 7)
        # тёмное основание головы
        s.repaint(-19, -13, -7, -1, L["shoulder"] + 4, L["shoulder"] + 4,
                  self.m("metal_dark"), "SMALL", parts=("weapon_club",))

    # --------------------------------------------------------------- детали ------
    def build_details(self):
        s, W, L = self.s, self.W, self.L
        metal_d = self.m("metal_dark")
        bronze = self.m("bronze")
        tf = self.front["torso"]
        # швы туники
        for zz in range(L["waist"] + 2, L["shoulder"] - 1, 4):
            s.repaint(-6, 5, tf - 1, tf - 1, zz, zz, self.m("tunic_dark"), "SMALL",
                      parts=("torso",))
        # заклёпки наплечника и пряжки
        for zz in (L["shoulder"] - 1, L["shoulder"] - 3):
            s.put(13, tf - 2, zz, "torso", bronze, "SMALL")
        # костяшки и швы пальцев (только на пальцах, ладонь остаётся цельной)
        hw = W["hand_width"]
        x0 = int(round(W["arm_center_x"] - hw / 2.0))
        for fx in (x0 + 2, x0 + 4, x0 + 6):
            s.repaint(fx, fx, -6, -2, L["hand_tip"], L["wrist"] - 5,
                      self.m("skin_shadow"), "SMALL", parts=("hand_L",))
        for fx in range(x0, x0 + hw, 2):
            s.put(fx, -6, L["wrist"] - 3, "hand_L", self.m("skin_light"), "SMALL")
        # царапины на камне булавы
        s.put(-15, -6, L["shoulder"] + 3, "weapon_club", metal_d, "SMALL")
        s.put(-16, -6, L["shoulder"] + 2, "weapon_club", metal_d, "SMALL")
        _ = metal_d

    # ---------------------------------------------------------------- стыки ------
    def cut_joints(self):
        L = self.L
        skin = self.m("skin")
        bridging = ("red", "red_dark", "metal", "metal_dark", "metal_light", "bronze")
        # каждый сегмент держится в своих анатомических границах (декор может свисать)
        ranges = {
            "head": (L["chin"], L["skull_top"] + 1),
            "torso": (L["waist"], L["neck_top"]),
            "pelvis": (L["crotch"], L["waist"] - 1),
            "upper_arm_L": (L["elbow"], L["shoulder"]), "forearm_L": (L["wrist"] + 1, L["elbow"] - 1),
            "hand_L": (L["hand_tip"], L["wrist"] - 1),
            "upper_arm_R": (L["elbow"], L["shoulder"]), "forearm_R": (L["wrist"] + 1, L["elbow"] - 1),
            "hand_R": (L["hand_tip"], L["wrist"] - 1),
            "thigh_L": (L["knee"], L["crotch"] - 1), "shin_L": (L["ankle"] + 1, L["knee"] - 1),
            "foot_L": (L["ground"], L["ankle"]),
            "thigh_R": (L["knee"], L["crotch"] - 1), "shin_R": (L["ankle"] + 1, L["knee"] - 1),
            "foot_R": (L["ground"], L["ankle"]),
        }
        clamped = 0
        body_mats = {self.m(k) for k in ("skin", "skin_light", "skin_shadow", "skin_dark",
                                        "pants", "boot", "tunic", "tunic_dark")
                     if k in self.pal}
        for part, (zmin, zmax) in ranges.items():
            for pos, val in list(self.s.cells.items()):
                if val[2] == part and val[0] in body_mats and not (zmin <= pos[2] <= zmax):
                    del self.s.cells[pos]
                    clamped += 1
        # канавка на стыке: снимаем только наружную оболочку, сердечник остаётся
        cuts = [("head", L["chin"]), ("torso", L["waist"]), ("pelvis", L["crotch"]),
                ("thigh_L", L["knee"]), ("shin_L", L["ankle"] + 1),
                ("upper_arm_L", L["elbow"]), ("forearm_L", L["wrist"] + 1),
                ("thigh_R", L["knee"]), ("shin_R", L["ankle"] + 1),
                ("upper_arm_R", L["elbow"]), ("forearm_R", L["wrist"] + 1)]
        for part, z in cuts:
            self.cut_log.append({"part": part, "z": z,
                                 "dropped_voxels": self.s.cut_shell(part, z, keep_mats=bridging)})
        self.cut_log.append({"clamped_skin_voxels": clamped})

    # ------------------------------------------------------------------ сборка ---
    def build(self) -> dict[str, Grid]:
        self.build_mass()
        self.build_head()
        self.build_muscles()
        self.build_outfit()
        self.build_weapon()
        self.build_hair()
        self.build_face()
        self.build_details()
        self.s.merge(self.s.mirror_side("L"))
        self.cut_joints()
        return self.s.to_grids(MODULE_ORDER)
