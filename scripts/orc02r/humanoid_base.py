#!/usr/bin/env python3
"""Factoria HumanoidBase v2: общий гуманоидный скульпт, из которого профиль делает Orc.

Архитектура (важно для силуэта):
  1. Строится ЕДИНЫЙ воксельный объём (Sculpt) непрерывными трубами: торс, ноги,
     руки проходят сквозь стыки, поэтому силуэт цельный.
  2. Каждый воксель помечен частью тела (`part`): torso/pelvis/thigh_L/...
  3. На стыках удаляется ровно один слой вокселей (LEGO-зазор 1 воксель),
     поэтому модульность не рвёт силуэт.
  4. Детализация тремя смысловыми уровнями: LARGE (объём), MEDIUM (мышцы,
     броня, одежда, волосы/борода), SMALL (лицо, швы, кромки, заклёпки).

Все числа — из профиля (JSON). Геометрия CubeGame не используется.
Перед = -Y. x — влево/вправо (x>0 — левая сторона персонажа). z — вверх, 0 = пол.
"""

from __future__ import annotations

from voxelkit import Grid, Sculpt

MODULE_ORDER = [
    "head", "eyes", "brows", "mouth", "hair", "beard", "torso", "pelvis",
    "upper_arm_L", "forearm_L", "hand_L", "upper_arm_R", "forearm_R", "hand_R",
    "thigh_L", "shin_L", "foot_L", "thigh_R", "shin_R", "foot_R",
]


class HumanoidBuilder:
    def __init__(self, profile: dict):
        self.profile = profile
        self.L = profile["landmarks"]
        self.W = profile["widths"]
        self.face = profile["face"]
        self.hair_cfg = profile["hair"]
        self.beard_cfg = profile["beard"]
        self.armor_cfg = profile["armor"]
        self.detail = profile["detail"]
        self.pal = profile["palette"]
        self.s = Sculpt()
        self.cut_log: list[dict] = []
        # Передние/задние поверхности (воксели), вычисленные из ширин профиля
        self.front = profile.get("surfaces", {})

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
            (L["crotch"], W["pelvis_width"], W["pelvis_depth"], 0.0, 0.0),
            (L["crotch"] + 3, W["pelvis_width"] - 1, W["pelvis_depth"], 0.0, 0.0),
            (waist - 3, W["waist_width"] + 0.5, W["waist_depth"], 0.0, -0.2),
            (waist - 1, W["waist_width"], W["waist_depth"], 0.0, -0.3),
            (waist + 1, W["waist_width"] + 1, W["waist_depth"], 0.0, -0.5),
            (waist + 3, W["waist_width"] + 2.5, W["waist_depth"] + 1, 0.0, -0.6),
            (waist + 5, W["waist_width"] + 4, W["waist_depth"] + 2, 0.0, -0.7),
            (L["shoulder"] - 3, W["chest_width"] - 1, W["chest_depth"] - 1, 0.0, -0.8),
            (L["shoulder"] - 2, W["chest_width"] - 0.5, W["chest_depth"], 0.0, -0.8),
            (L["shoulder"] - 1, W["chest_width"], W["chest_depth"], 0.0, -0.8),
            (L["shoulder"], W["chest_width"] - 0.5, W["chest_depth"] - 0.5, 0.0, -0.5),
            (L["shoulder"] + 1, W["neck_width"] + 5, W["neck_depth"] + 2, 0.0, 0.0),
            (L["shoulder"] + 2, W["neck_width"] + 1, W["neck_depth"], 0.0, 0.0),
            (L["neck_top"], W["neck_width"], W["neck_depth"] - 0.5, 0.0, 0.0),
        ], torso_part, skin, "LARGE", p=4.2)

        # ноги: непрерывная труба от щиколотки до бедра
        cx = W["leg_center_x"]

        def leg_part(z):
            return "thigh_L" if z >= L["knee"] else "shin_L"

        s.tube([
            (L["ankle"] + 1, 7, 7, cx, 0.0),
            (L["ankle"] + 3, 8, 9, cx, 0.3),
            (L["ankle"] + 6, W["shin_width"] + 0.5, W["shin_depth"] + 0.5, cx, 0.3),
            (L["ankle"] + 9, W["shin_width"], W["shin_depth"], cx, 0.0),
            (L["knee"] - 1, W["shin_width"] - 0.5, W["shin_depth"], cx, 0.0),
            (L["knee"], W["shin_width"] - 0.5, W["shin_depth"], cx, 0.0),
            (L["knee"] + 3, W["thigh_width"] - 1, W["thigh_depth"] - 0.5, cx, -0.3),
            (L["knee"] + 7, W["thigh_width"], W["thigh_depth"], cx, -0.3),
            (L["crotch"] - 1, W["thigh_width"], W["thigh_depth"], cx, -0.3),
        ], leg_part, skin, "LARGE", p=4.0)

        # руки: непрерывная труба от запястья до плеча
        acx = W["arm_center_x"]

        def arm_part(z):
            return "upper_arm_L" if z >= L["elbow"] else "forearm_L"

        s.tube([
            (L["wrist"] + 1, 5, 6, acx, -1.0),
            (L["wrist"] + 4, 6, 7, acx, -1.2),
            (L["elbow"] - 2, 6, 6.5, acx, -1.0),
            (L["elbow"], 5.5, 6.5, acx, -1.0),
            (L["elbow"] + 3, 6.5, 7, acx, -1.0),
            (L["elbow"] + 7, 6.5, 7.5, acx, -1.0),
            (L["shoulder"] - 1, 6, 7, acx, -1.2),
            (L["shoulder"], 5, 6, acx, -1.2),
        ], arm_part, skin, "LARGE", p=3.8)

        # кисти: широкая ладонь, пальцы единым блоком с намеченными швами
        hw = W["hand_width"]
        x0 = int(round(acx - hw / 2.0))
        palm_z0 = L["wrist"] - 3
        s.box(x0, x0 + hw - 1, -5, -2, palm_z0, L["wrist"], "hand_L", skin, "LARGE")
        s.box(x0, x0 + hw - 1, -5, -2, L["hand_tip"], palm_z0 - 1, "hand_L", skin, "LARGE")
        # большой палец с внутренней стороны
        s.box(x0 - 1, x0 - 1, -5, -3, palm_z0 + 1, palm_z0 + 2, "hand_L", skin, "MEDIUM")

        # стопы (ботинки) — носок вперёд
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
        face_y = self.front.get("head", -8)

        s.tube([
            (chin, 7, 9, 0.0, -2.5),
            (chin + 1, 8, 10.5, 0.0, -2.0),
            (chin + 2, 9, 11.5, 0.0, -1.8),
            (chin + 3, W["head_width"] - 0.5, W["head_depth"], 0.0, -1.5),
            (L["eye"] + 1, W["head_width"], W["head_depth"], 0.0, -1.5),
            (L["brow"] + 1, W["head_width"], W["head_depth"], 0.0, -1.5),
            (top - 1, W["head_width"] - 0.5, W["head_depth"] - 1, 0.0, -1.5),
            (top, W["head_width"] - 1.5, W["head_depth"] - 2.5, 0.0, -1.5),
        ], "head", skin, "LARGE", p=4.4)

        fy = face_y
        # MEDIUM: тяжёлая челюсть/подбородок вперёд
        s.box(-3, 2, fy - 1, fy - 1, chin, chin + 1, "head", skin, "MEDIUM")
        # MEDIUM: надбровная дуга (1 воксель вперёд, сильная, но не «козырёк»)
        s.box(-W["head_width"] // 2, W["head_width"] // 2 - 1, fy - 1, fy - 1,
              L["brow"], L["brow"] + 1, "head", skin, "MEDIUM")
        # MEDIUM: скулы
        for sx in (-1, 1):
            x = 4
            xx = x if sx > 0 else -1 - x
            s.box(xx, xx, fy - 1, fy - 1, L["eye"] - 1, L["eye"], "head", skin, "MEDIUM")
        # MEDIUM: нос
        nw = int(F["nose_width"])
        s.box(-(nw // 2), nw // 2 - 1, fy - 1, fy - 1, L["eye"] - 1, L["eye"], "head",
              self.m("skin_light"), "MEDIUM")
        for xx in (-(nw // 2), nw // 2 - 1):
            s.put(xx, fy - 1, L["eye"], "head", self.m("skin_shadow"), "SMALL")
        # MEDIUM: заострённые уши (выше линии глаз, чуть назад)
        ear_len = int(F["ear_length"])
        for i in range(ear_len):
            for sx in (-1, 1):
                x = W["head_width"] // 2 - 1 + i
                xx = x if sx > 0 else -1 - x
                z0 = L["eye"] + 1 + i
                s.box(xx, xx, -2 + i // 2, 1 + i // 2, z0, z0 + 2, "head", skin, "MEDIUM")
        s.put(W["head_width"] // 2 - 1, 0, L["eye"] + 2, "head", self.m("skin_shadow"), "SMALL")
        s.put(-W["head_width"] // 2, 0, L["eye"] + 2, "head", self.m("skin_shadow"), "SMALL")

        # SMALL: глазницы (углубления 2x1) — глаза отдельным модулем
        s.carve(1, 2, fy, fy, L["eye"], L["eye"])
        s.carve(-3, -2, fy, fy, L["eye"], L["eye"])
        s.repaint(-3, 2, fy + 1, fy + 1, L["eye"] - 1, L["eye"] - 1,
                  self.m("skin_shadow"), "SMALL", parts=("head",))
        # SMALL: нахмуренная переносица между бровями
        s.repaint(-1, 0, fy - 1, fy - 1, L["eye"] + 1, L["brow"], self.m("skin_shadow"),
                  "SMALL", parts=("head",))
        # SMALL: щель рта (зубы и клыки — модуль mouth)
        s.carve(-3, 2, fy, fy, L["eye"] - 3, L["eye"] - 3)
        s.repaint(-3, 2, fy - 1, fy - 1, L["eye"] - 3, L["eye"] - 3,
                  self.m("skin_dark"), "SMALL", parts=("head",))
        # SMALL: шрамы и боевая раскраска
        if F.get("scars", True):
            for i in range(2):
                s.put(4, fy - 1, L["eye"] + i, "head", self.m("scar"), "SMALL")
            s.put(-2, fy - 2, L["brow"] + 1, "head", self.m("scar"), "SMALL")
            for i in range(2):
                s.put(3, fy - 1, L["eye"] - 2 - i, "head", self.m("skin_dark"), "SMALL")

    def build_face(self):
        s, W, L = self.s, self.W, self.L
        fy = self.front["head"]
        # глаза: тёмные щели 2x1 с янтарной искрой (глубоко посаженные, без «мультяшных» белков)
        for sx in (-1, 1):
            ex0 = 1 if sx > 0 else -3
            s.box(ex0, ex0 + 1, fy, fy, L["eye"], L["eye"], "eyes",
                  self.m("eye_sclera"), "SMALL")
            s.put(ex0 + (0 if sx < 0 else 1), fy, L["eye"], "eyes", self.m("eye_iris"), "SMALL")
        # тяжёлые брови: у переносицы ниже, к виску выше
        for sx in (-1, 1):
            for i, dz in enumerate((0, 0, 1, 1)):
                x = 1 + i
                xx = x if sx > 0 else -1 - x
                s.box(xx, xx, fy - 1, fy - 1, L["eye"] + 1 + dz, L["eye"] + 1 + dz,
                      "brows", self.m("hair"), "SMALL")
        # рот: губы, ряд зубов, два клыка (растут вверх из нижней челюсти)
        mw = int(self.face["mouth_width"])
        s.box(-mw // 2 + 1, mw // 2 - 2, fy, fy, L["eye"] - 3, L["eye"] - 3, "mouth",
              self.m("mouth"), "SMALL")
        for xx in (-1, 0):
            s.put(xx, fy, L["eye"] - 3, "mouth", self.m("ivory"), "SMALL")
        tusk = int(self.face["tusk_length"])
        for sx in (-1, 1):
            for i in range(tusk):
                x = 2 + (i // 2) if sx > 0 else -3 - (i // 2)
                zz = L["eye"] - 4 + i
                s.put(x, fy - 1, zz, "mouth", self.m("ivory"), "SMALL")
        s.box(-2, 1, fy - 1, fy - 1, L["eye"] - 4, L["eye"] - 4, "mouth",
              self.m("skin_dark"), "SMALL")

    def build_hair(self):
        cfg = self.hair_cfg
        if not cfg.get("enabled", True):
            return
        s, W, L = self.s, self.W, self.L
        hw = W["head_width"]
        top = L["skull_top"]
        hair = self.m("hair")
        # MEDIUM: шапка волос по черепу + затылок (лоб открыт, кромка без «шлема»)
        s.box(-hw // 2 + 2, hw // 2 - 3, -5, 4, top + 1, top + 1, "hair", hair, "MEDIUM")
        s.box(-hw // 2 + 3, hw // 2 - 4, -4, 3, top + 2, top + 2, "hair", hair, "MEDIUM")
        s.box(-3, 2, 4, 5, L["eye"] + 1, top, "hair", hair, "MEDIUM")
        # MEDIUM: короткий пучок
        s.box(-1, 0, -2, 0, top + 3, top + 4, "hair", hair, "MEDIUM")
        # SMALL: бронзовое кольцо пучка
        s.box(-1, 0, -2, 0, top + 3, top + 3, "hair", self.m("bronze"), "SMALL")
        # SMALL: пряди у виска
        s.put(-4, -4, L["eye"] + 2, "hair", hair, "SMALL")
        s.put(3, -4, L["eye"] + 2, "hair", hair, "SMALL")

    def build_beard(self):
        cfg = self.beard_cfg
        if not cfg.get("enabled", True):
            return
        s, W, L, F = self.s, self.W, self.L, self.face
        fy = self.front["head"]
        hair = self.m("beard")
        chin, eye = L["chin"], L["eye"]
        # MEDIUM: борода из прядей с рваным низом, объёмно обхватывает челюсть
        top = chin - 1
        for x in range(-5, 4):
            ax = abs(x + 0.5)
            if ax > 4.6:
                continue
            length = int(round(6.0 - ax * 0.8 + ((x * 5 + 1) % 3) * 0.8))
            # боковые пряди уходят назад, центральные — вперёд
            y0 = fy if ax <= 2.5 else fy + 1
            y1 = y0 + 1
            s.box(x, x, y0, y1, top - length, top, "beard", hair, "MEDIUM")
        for sx in (-1, 1):
            x0, x1 = 2, 4
            s.box(x0 if sx > 0 else -1 - x1, x1 if sx > 0 else -1 - x0,
                  fy - 1, fy, chin + 1, chin + 3, "beard", hair, "MEDIUM")
        # MEDIUM: две косы с бронзовыми бусинами (выступают вперёд и ниже бороды)
        for sx in (-1, 1):
            x = 1 if sx > 0 else -3
            s.box(x, x + 1, fy - 1, fy, chin - 10, chin - 6, "beard", hair, "MEDIUM")
            s.box(x, x + 1, fy - 1, fy, chin - 8, chin - 8, "beard",
                  self.m("bronze"), "SMALL")
        # SMALL: усы над губой и пятно под губой
        s.box(-3, 2, fy - 1, fy - 1, eye - 2, eye - 2, "beard", hair, "SMALL")
        s.box(-2, 1, fy - 1, fy - 1, eye - 4, eye - 4, "beard", hair, "SMALL")
        # SMALL: бакенбарды к ушам
        for sx in (-1, 1):
            x = W["head_width"] // 2 - 1
            xx = x if sx > 0 else -1 - x
            s.box(xx, xx, fy, fy + 1, eye - 2, eye, "beard", hair, "SMALL")

    # ------------------------------------------------------------------ мышцы ----
    def build_muscles(self):
        s, W, L = self.s, self.W, self.L
        light, shadow = self.m("skin_light"), self.m("skin_shadow")
        bulge = float(self.detail.get("muscle_bulge", 1.0))
        tf = self.front.get("torso", -6)
        for sx in (-1, 1):
            s.ellipsoid(sx * 4.0, tf + 1.0, L["shoulder"] - 3.0, 3.4 * bulge, 1.9, 2.3,
                        "torso", light, "MEDIUM", p=2.8)
        s.repaint(-1, 0, tf, tf + 1, L["shoulder"] - 5, L["shoulder"] - 2, shadow, "SMALL",
                  parts=("torso",))
        for zz in (L["waist"] + 1, L["waist"] + 3):
            for sx in (-1, 1):
                x0 = 1 if sx > 0 else -5
                s.box(x0, x0 + 3, tf, tf + 1, zz, zz, "torso", light, "MEDIUM")
            s.repaint(-1, 0, tf, tf + 1, zz, zz, shadow, "SMALL", parts=("torso",))
        for sx in (-1, 1):
            s.ellipsoid(sx * 7.0, 0.0, L["waist"] + 5, 2.2, 3.6, 3.0, "torso", shadow,
                        "MEDIUM", p=2.8)
        s.box(-5, 4, 0, 2, L["shoulder"], L["shoulder"] + 1, "torso", light, "MEDIUM")
        for sx in (-1, 1):
            s.ellipsoid(sx * 3.6, 4.2, L["crotch"] + 2.5, 3.2, 1.6, 2.2, "pelvis", shadow,
                        "MEDIUM", p=2.8)
        acx, lcx = W["arm_center_x"], W["leg_center_x"]
        s.ellipsoid(acx, -4.2, L["elbow"] + 3.5, 2.4, 1.6, 2.6, "upper_arm_L", light,
                    "MEDIUM", p=2.6)
        s.ellipsoid(acx, 2.6, L["elbow"] + 3.0, 2.2, 1.4, 2.4, "upper_arm_L", shadow,
                    "MEDIUM", p=2.6)
        s.ellipsoid(acx, -4.0, L["wrist"] + 6.0, 2.4, 1.6, 2.6, "forearm_L", light,
                    "MEDIUM", p=2.6)
        s.ellipsoid(lcx, -4.6, L["knee"] + 6.0, 3.4, 1.6, 3.4, "thigh_L", light,
                    "MEDIUM", p=2.8)
        s.ellipsoid(lcx, 3.6, L["knee"] + 5.0, 2.8, 1.4, 2.8, "thigh_L", shadow,
                    "MEDIUM", p=2.8)
        s.ellipsoid(lcx, 3.6, L["knee"] - 7.0, 2.8, 1.5, 3.0, "shin_L", light,
                    "MEDIUM", p=2.8)

    # ------------------------------------------------------------------ броня ----
    def build_armor(self):
        """Лёгкая, акцентная броня: тёмное железо + кожа + бронза. Тело остаётся читаемым."""
        s, W, L = self.s, self.W, self.L
        metal, metal_d, metal_l = self.m("metal"), self.m("metal_dark"), self.m("metal_light")
        leather, leather_d = self.m("leather"), self.m("leather_dark")
        cloth, cloth_d, bronze = self.m("cloth"), self.m("cloth_dark"), self.m("bronze")
        side = str(self.armor_cfg.get("pauldron_side", "LEFT")).upper()
        sgn = 1 if side == "LEFT" else -1
        acx = int(W["arm_center_x"])
        lcx = W["leg_center_x"]
        ax0, ax1 = acx - 2, acx + 3
        tf = self.front["torso"]
        pf = self.front["pelvis"]
        lf = self.front["leg"]
        sf = self.front["shin"]
        ff = self.front["foot"]

        def side_rng(x0, x1):
            return (x0, x1) if sgn > 0 else (-1 - x1, -1 - x0)

        # === наплечник: пластины, вертикально обхватывающие плечо
        layers = [
            (L["shoulder"] + 1, ax0 - 1, ax1, tf - 1, 1),
            (L["shoulder"] - 1, ax0 - 1, ax1, tf - 1, 2),
            (L["shoulder"] - 3, ax0, ax1, tf, 3),
        ]
        for z0, x0, x1, y0, y1 in layers:
            xa, xb = side_rng(x0, x1)
            s.box(xa, xb, y0, y1, z0, z0 + 1, "torso", metal, "MEDIUM")
        # бронзовая кромка по нижнему краю + заклёпочные блики
        xa, xb = side_rng(ax0 - 1, ax1)
        s.box(xa, xb, tf - 1, tf - 1, L["shoulder"] + 1, L["shoulder"] + 1, "torso",
              bronze, "SMALL")
        s.put(ax0 - 1 if sgn > 0 else -1 - (ax0 - 1), tf, L["shoulder"] + 2, "torso",
              metal_l, "SMALL")
        s.put(ax1 if sgn > 0 else -1 - ax1, tf, L["shoulder"] + 2, "torso", metal_l, "SMALL")
        # === противоположное плечо: кожаный ремень с заклёпкой
        oxa, oxb = (-1 - ax1, -1 - (ax0 - 1)) if sgn > 0 else (ax0 - 1, ax1)
        s.box(oxa, oxb, tf, 1, L["shoulder"], L["shoulder"], "torso", leather, "MEDIUM")
        s.put(oxa + 2, tf, L["shoulder"], "torso", bronze, "SMALL")
        # === X-образная упряжь на груди с бронзовой пряжкой
        steps = 9
        for direction in (1, -1):
            for i in range(steps):
                t = i / (steps - 1)
                x = int(round(direction * (ax0 - 1) * (1 - t)
                              + (-direction) * (W["waist_width"] // 2) * t))
                z = int(round((L["shoulder"] - 2) * (1 - t) + (L["waist"] + 1) * t))
                s.box(x, x + 1, tf - 1, tf, z, z, "torso", leather_d, "MEDIUM")
        s.box(-1, 0, tf - 1, tf - 1, L["waist"] + 4, L["waist"] + 5, "torso", bronze, "SMALL")
        # === бронзовое кольцо на шее
        for dx in range(-3, 3):
            s.put(dx, -4, L["shoulder"] + 2, "torso", bronze, "SMALL")
            s.put(dx, 3, L["shoulder"] + 2, "torso", bronze, "SMALL")
            s.put(-3 if dx < 0 else 2, dx, L["shoulder"] + 2, "torso", bronze, "SMALL")

        # === пояс (перекрывает стык таз/торс, как одежда над LEGO-зазором)
        belt_z = L["waist"] - 1
        s.tube([(belt_z, W["waist_width"] + 2, W["waist_depth"] + 2, 0.0, -0.3),
                (belt_z + 1, W["waist_width"] + 2, W["waist_depth"] + 2, 0.0, -0.3)],
               "pelvis", leather_d, "MEDIUM", p=3.2)
        for x in (-5, -2, 2, 5):
            s.put(x, pf, belt_z, "pelvis", bronze, "SMALL")
        s.box(-2, 1, pf - 1, pf, belt_z, belt_z + 1, "pelvis", metal, "MEDIUM")
        # === набедренные ремни
        for sx in (-1, 1):
            x0, x1 = 6, 8
            xa, xb = (x0, x1) if sx > 0 else (-1 - x1, -1 - x0)
            s.box(xa, xb, pf + 1, 3, L["crotch"] - 1, L["crotch"] + 3, "pelvis",
                  leather, "MEDIUM")
            s.box(xa, xb, pf + 1, pf + 1, L["crotch"] + 1, L["crotch"] + 2, "pelvis",
                  bronze, "SMALL")
        # === передний фартук (узкая тёмная ткань, асимметричный рваный низ)
        hem = L["crotch"] - 7
        for zz in range(hem, belt_z):
            half = 3 if zz > hem + 3 else 2
            s.box(-half, half + 1, pf - 1, pf, zz, zz, "pelvis", cloth, "MEDIUM")
        s.carve(-2, -2, pf - 1, pf, hem, hem)
        s.carve(2, 2, pf - 1, pf, hem, hem)
        s.carve(1, 1, pf - 1, pf, hem, hem + 1)
        s.repaint(-3, 3, pf - 1, pf, hem, hem, cloth_d, "SMALL", parts=("pelvis",))
        s.repaint(-1, -1, pf - 1, pf, hem + 2, belt_z - 2, cloth_d, "SMALL", parts=("pelvis",))
        # === задний фартук
        for zz in range(L["crotch"] - 4, belt_z):
            s.box(-3, 2, 4, 5, zz, zz, "pelvis", cloth, "MEDIUM")

        # === наруч: кожа + бронзовая полоса
        s.tube([(L["wrist"] + 1, 8, 8, acx, -1.2), (L["wrist"] + 2, 8, 8, acx, -1.2)],
               "forearm_L", leather, "MEDIUM", p=3.4)
        s.box(acx - 2, acx + 2, -5, -5, L["wrist"] + 2, L["wrist"] + 2, "forearm_L",
              bronze, "SMALL")
        # === кожаный ремень на бицепсе
        s.tube([(L["elbow"] + 4, 8, 8, acx, -1.0), (L["elbow"] + 4, 8, 8, acx, -1.0)],
               "upper_arm_L", leather_d, "SMALL", p=3.4)
        # === понож: кожаная обмотка + небольшая железная пластина
        s.tube([(L["ankle"] + 4, W["shin_width"] + 1.5, W["shin_depth"] + 1.5, lcx, 0.0),
                (L["ankle"] + 5, W["shin_width"] + 1.5, W["shin_depth"] + 1.5, lcx, 0.0)],
               "shin_L", leather, "MEDIUM", p=3.4)
        gx0, gx1 = lcx - 2, lcx + 1
        s.box(gx0, gx1, sf - 1, sf, L["ankle"] + 6, L["ankle"] + 8, "shin_L", metal_d, "MEDIUM")
        s.put(gx0, sf - 1, L["ankle"] + 7, "shin_L", bronze, "SMALL")
        # === наколенник
        s.box(gx0, gx1, lf - 1, lf, L["knee"] + 1, L["knee"] + 2, "thigh_L", metal_d, "MEDIUM")
        # === ботинок: кожа, железный носок, подошва, ремень
        fw, fl = W["foot_width"], W["foot_length"]
        fx0, fx1 = lcx - fw // 2, lcx + fw // 2 - 1
        s.repaint(fx0, fx1, ff, 3, L["ground"] + 1, L["ankle"] - 1, leather_d, "LARGE",
                  parts=("foot_L",))
        s.box(fx0, fx1, ff, ff + 1, L["ground"] + 1, L["ankle"] - 1, "foot_L", metal_d, "MEDIUM")
        s.box(fx0, fx1, ff + 5, ff + 5, L["ground"] + 1, L["ankle"] - 1, "foot_L",
              leather, "MEDIUM")
        s.repaint(fx0, fx1, ff, 3, L["ground"], L["ground"], leather_d, "SMALL",
                  parts=("foot_L",))
        s.repaint(fx0, fx1, ff, 3, L["ankle"] - 1, L["ankle"] - 1, leather, "MEDIUM",
                  parts=("foot_L",))

    # --------------------------------------------------------------- детали ------
    def build_details(self):
        s, W, L = self.s, self.W, self.L
        metal_d, cloth_d = self.m("metal_dark"), self.m("cloth_dark")
        bronze = self.m("bronze")
        pf = self.front["pelvis"]
        sf, tf = self.front["shin"], self.front["torso"]
        # швы и складки ткани (две вертикальные складки, без «лестницы»)
        for x in (-2, 2):
            s.repaint(x, x, pf - 1, pf, L["crotch"] - 6, L["waist"] - 4, cloth_d, "SMALL",
                      parts=("pelvis",))
        # царапины на железе поножа и наплечника
        for zz in (L["ankle"] + 5, L["ankle"] + 6):
            s.put(W["leg_center_x"] - 2, sf - 1, zz, "shin_L", metal_d, "SMALL")
        for xx in (9, 12):
            s.put(xx, tf - 1, L["shoulder"] + 1, "torso", metal_d, "SMALL")
        # костяшки, швы пальцев и ногти
        hw = W["hand_width"]
        x0 = int(round(W["arm_center_x"] - hw / 2.0))
        for fx in (x0 + 2, x0 + 4):
            s.repaint(fx, fx, -5, -2, L["hand_tip"], L["wrist"] - 4,
                      self.m("skin_shadow"), "SMALL", parts=("hand_L",))
        for fx in range(x0, x0 + hw, 2):
            s.put(fx, -5, L["wrist"] - 3, "hand_L", self.m("skin_light"), "SMALL")
            s.put(fx, -5, L["hand_tip"], "hand_L", self.m("skin_light"), "SMALL")
        # серьга (маленькая деталь идентичности)
        s.put(W["head_width"] // 2, -1, L["eye"] - 1, "head", bronze, "SMALL")

    # ---------------------------------------------------------------- стыки ------
    def cut_joints(self):
        L = self.L
        skin = (self.m("skin"),)
        cuts = [("head", L["chin"] - 1), ("torso", L["waist"]), ("pelvis", L["crotch"]),
                ("thigh_L", L["knee"]), ("shin_L", L["ankle"] + 1),
                ("upper_arm_L", L["elbow"]), ("forearm_L", L["wrist"] + 1),
                ("thigh_R", L["knee"]), ("shin_R", L["ankle"] + 1),
                ("upper_arm_R", L["elbow"]), ("forearm_R", L["wrist"] + 1)]
        for part, z in cuts:
            self.cut_log.append({"part": part, "z": z,
                                 "dropped_voxels": self.s.cut(part, z, mats=skin)})

    # ------------------------------------------------------------------ сборка ---
    def build(self) -> dict[str, Grid]:
        self.build_mass()
        self.build_head()
        self.build_muscles()
        self.build_armor()
        self.build_hair()
        self.build_beard()
        # окно рта освобождается от бороды до отрисовки лица
        fy = self.front["head"]
        self.s.carve(-3, 2, fy - 1, fy, self.L["eye"] - 2, self.L["eye"] - 2)
        self.build_face()
        self.build_details()
        self.s.merge(self.s.mirror_side("L"))
        self.cut_joints()
        return self.s.to_grids(MODULE_ORDER)
